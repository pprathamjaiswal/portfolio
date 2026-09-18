"""Views for the portfolio site."""

from __future__ import annotations

import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET, require_POST

from . import content, github
from .forms import ContactForm
from .notifications import notify_new_contact

logger = logging.getLogger(__name__)


def _client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def home(request):
    """Render the single-page portfolio."""
    overview = github.get_overview()

    context = {
        "profile": content.PROFILE,
        "avatar_url": content.AVATAR_URL,
        "use_local_avatar": content.USE_LOCAL_AVATAR,
        "socials": [s for s in content.SOCIALS if s.get("url")],
        "primary_socials": [s for s in content.SOCIALS if s.get("url") and s.get("primary")],
        "skill_groups": content.SKILL_GROUPS,
        "marquee_skills": content.MARQUEE_SKILLS,
        "focus_areas": content.FOCUS_AREAS,
        "experience": content.EXPERIENCE,
        "education": content.EDUCATION,
        "certifications": content.CERTIFICATIONS,
        "achievements": content.ACHIEVEMENTS,
        "featured_projects": content.FEATURED_PROJECTS,
        # Drives the Background section's column count so a single populated
        # list spreads across the row instead of leaving the section lopsided.
        "background_columns": sum(
            1
            for block in (content.EDUCATION, content.CERTIFICATIONS, content.ACHIEVEMENTS)
            if block
        ),
        "seo": content.SEO,
        "github": overview,
        # Static links that must survive a GitHub outage.
        "github_username": content.GITHUB_USERNAME,
        "github_profile_url": content.GITHUB_PROFILE_URL,
        "github_repos_url": content.GITHUB_REPOS_URL,
        "has_github": overview["available"],
        "site_url": settings.SITE_URL,
    }
    context["nav_links"] = content.nav_links(context)
    return render(request, "index.html", context)


def _wants_json(request) -> bool:
    """True for the fetch() path; False for a plain form POST without JS."""
    return (
        "application/json" in (request.content_type or "")
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or "application/json" in request.headers.get("Accept", "")
    )


def _reply(request, ok: bool, message: str, status: int):
    """
    Answer with JSON for fetch(), or a redirect for a no-JavaScript POST.

    The redirect carries a fixed status code rather than the message text: the
    page must never echo an attacker-supplied string back to a visitor.
    """
    if _wants_json(request):
        return JsonResponse({"success": ok, "message": message}, status=status)
    return redirect("/?contact=" + ("ok" if ok else "error") + "#contact")


@require_POST
def contact_submit(request):
    """Accept a contact message. CSRF protected and rate limited per IP."""
    ip = _client_ip(request)
    bucket = f"contact:{ip}"
    attempts = cache.get(bucket, 0)
    if attempts >= settings.CONTACT_RATE_LIMIT:
        return _reply(
            request,
            False,
            "You've sent a few messages already — please try again later.",
            429,
        )

    if request.content_type and "application/json" in request.content_type:
        try:
            payload = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _reply(request, False, "We couldn't read that request.", 400)
        if not isinstance(payload, dict):
            return _reply(request, False, "We couldn't read that request.", 400)
    else:
        payload = request.POST.dict()

    form = ContactForm(payload)
    if not form.is_valid():
        return _reply(request, False, form.first_error(), 400)

    try:
        contact = form.save()
    except Exception:
        logger.exception("Failed to save contact message")
        return _reply(
            request, False, "Something went wrong on our end. Please try again.", 500
        )

    # Saved first, notified second: if email is down the message is not lost.
    notify_new_contact(contact)

    cache.set(bucket, attempts + 1, 60 * 60)
    return _reply(
        request, True, "Thanks — your message is on its way. I'll reply soon.", 200
    )


@require_GET
@cache_control(max_age=300, public=True)
def github_repos(request):
    """
    Public JSON feed of curated repositories.

    The GitHub token is used only inside base/github.py on the server; this
    response carries nothing but the public repository fields the page shows.
    """
    overview = github.get_overview()
    if not overview["available"]:
        return JsonResponse(
            {"success": False, "repos": [], "message": "GitHub data is unavailable right now."},
            status=503,
        )
    return JsonResponse(
        {
            "success": True,
            "profile": overview["profile"],
            "repos": overview["repos"],
            "total_stars": overview["total_stars"],
        }
    )


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def handler404(request, exception):
    return render(request, "404.html", {"seo": content.SEO}, status=404)


def handler500(request):
    return render(request, "500.html", {"seo": content.SEO}, status=500)
