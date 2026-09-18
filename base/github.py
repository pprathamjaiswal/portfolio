"""
Server-side GitHub integration.

Security model
--------------
The GitHub token lives in ``settings.GITHUB_TOKEN``, which is populated from
the ``GITHUB_TOKEN`` environment variable. Every call in this module runs in
the Django process. The token is never placed in a template context, never
serialised into the JSON returned to the browser, and never logged — error
paths log the status code and URL only.

Resilience
----------
Results are cached for ``settings.GITHUB_CACHE_SECONDS``. A second, much
longer-lived "stale" copy is kept as well, so if GitHub is down, rate-limits
us, or the token expires, the site keeps rendering the last good data instead
of showing an empty section. If there is no cached copy at all, every function
degrades to an empty result and the caller hides the section.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from datetime import datetime, timezone

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

API_ROOT = "https://api.github.com"
USER_AGENT = "portfolio-site/1.0"
REQUEST_TIMEOUT = 8  # seconds

_CACHE_PREFIX = "github"
_STALE_TTL = 60 * 60 * 24 * 14  # keep a fallback copy for two weeks
_FAILURE_BACKOFF = 120  # pause calls this long after a failure with no fallback

# Repos whose only content is a README/boilerplate are not worth showing.
_MIN_REPO_SIZE_KB = 1


# ---------------------------------------------------------------------------
# Low level
# ---------------------------------------------------------------------------


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }
    token = (getattr(settings, "GITHUB_TOKEN", "") or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get(path: str):
    """GET a GitHub API path. Returns parsed JSON, or None on any failure."""
    url = f"{API_ROOT}{path}"
    request = urllib.request.Request(url, headers=_headers(), method="GET")
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            if response.status != 200:
                logger.warning("GitHub %s returned HTTP %s", path, response.status)
                return None
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Log the status only — never the headers, which carry the token.
        logger.warning("GitHub %s failed: HTTP %s", path, exc.code)
    except urllib.error.URLError as exc:
        logger.warning("GitHub %s unreachable: %s", path, exc.reason)
    except (TimeoutError, json.JSONDecodeError, ValueError) as exc:
        logger.warning("GitHub %s unusable response: %s", path, exc.__class__.__name__)
    return None


def _cached(key: str, builder):
    """Cache-through helper with a long-lived stale fallback."""
    fresh_key = f"{_CACHE_PREFIX}:{key}"
    stale_key = f"{_CACHE_PREFIX}:stale:{key}"
    backoff_key = f"{_CACHE_PREFIX}:backoff:{key}"

    hit = cache.get(fresh_key)
    if hit is not None:
        return hit

    # A recent total failure with nothing to fall back on: skip the call so a
    # GitHub outage cannot add its timeout to every page load.
    if cache.get(backoff_key):
        return None

    value = builder()
    if value:
        cache.set(fresh_key, value, settings.GITHUB_CACHE_SECONDS)
        cache.set(stale_key, value, _STALE_TTL)
        return value

    stale = cache.get(stale_key)
    if stale is not None:
        logger.info("Serving stale GitHub data for %s", key)
        # Back off briefly so a GitHub outage does not mean a request storm.
        cache.set(fresh_key, stale, 300)
        return stale

    cache.set(backoff_key, True, _FAILURE_BACKOFF)
    return value


# ---------------------------------------------------------------------------
# Shaping
# ---------------------------------------------------------------------------


def _parse_time(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _score(repo: dict) -> float:
    """Rank repositories by signal: stars, forks, then recency of real work."""
    stars = repo.get("stargazers_count", 0) or 0
    forks = repo.get("forks_count", 0) or 0

    recency = 0.0
    pushed = _parse_time(repo.get("pushed_at"))
    if pushed:
        days = (datetime.now(timezone.utc) - pushed).days
        if days <= 30:
            recency = 6.0
        elif days <= 90:
            recency = 4.0
        elif days <= 365:
            recency = 2.0
        elif days <= 730:
            recency = 0.5

    completeness = 0.0
    if (repo.get("description") or "").strip():
        completeness += 2.0
    if repo.get("homepage"):
        completeness += 1.5
    if repo.get("topics"):
        completeness += 1.0
    if repo.get("language"):
        completeness += 0.5

    return stars * 4 + forks * 3 + recency + completeness


def _is_meaningful(repo: dict, excluded: set[str]) -> bool:
    if repo.get("fork") or repo.get("archived") or repo.get("private"):
        return False
    if repo.get("disabled"):
        return False
    name = (repo.get("name") or "").strip()
    if not name or name.lower() in excluded:
        return False
    if (repo.get("size") or 0) < _MIN_REPO_SIZE_KB:
        return False
    # Needs at least one sign of being a real project.
    return bool(
        (repo.get("description") or "").strip()
        or repo.get("stargazers_count")
        or repo.get("homepage")
        or repo.get("topics")
    )


# Words that should not be title-cased when a repo slug becomes a heading.
_ACRONYMS = {
    "ai": "AI", "ml": "ML", "dsa": "DSA", "api": "API", "apis": "APIs",
    "ui": "UI", "ux": "UX", "cli": "CLI", "css": "CSS", "html": "HTML",
    "js": "JS", "ts": "TS", "sql": "SQL", "db": "DB", "llm": "LLM",
    "llms": "LLMs", "genai": "GenAI", "crud": "CRUD", "pwa": "PWA",
    "seo": "SEO", "os": "OS", "io": "IO", "qr": "QR", "nlp": "NLP",
    "cv": "CV", "3d": "3D", "2d": "2D",
}
_WORDMARKS = {
    "nextjs": "Next.js", "reactjs": "React", "nodejs": "Node.js",
    "vuejs": "Vue", "django": "Django", "react": "React", "node": "Node",
    "python": "Python", "java": "Java", "mongodb": "MongoDB",
    "mysql": "MySQL", "postgres": "Postgres", "firebase": "Firebase",
    "tailwind": "Tailwind", "typescript": "TypeScript", "javascript": "JavaScript",
}


def _prettify(name: str) -> str:
    """Turn a repo slug into a readable heading: `genai-chat` -> `GenAI Chat`."""
    words = [word for word in name.replace("_", "-").replace(".", "-").split("-") if word]
    out = []
    for word in words:
        key = word.lower()
        if key in _ACRONYMS:
            out.append(_ACRONYMS[key])
        elif key in _WORDMARKS:
            out.append(_WORDMARKS[key])
        elif word.isupper() and len(word) <= 4:
            out.append(word)
        else:
            out.append(word[:1].upper() + word[1:])
    return " ".join(out) or name


def _shape_repo(repo: dict) -> dict:
    """Reduce a GitHub payload to exactly the public fields the page needs."""
    pushed = _parse_time(repo.get("pushed_at"))
    homepage = (repo.get("homepage") or "").strip()
    if homepage and not homepage.startswith(("http://", "https://")):
        homepage = f"https://{homepage}"

    return {
        "name": repo.get("name", ""),
        "display_name": _prettify(repo.get("name", "") or ""),
        "description": (repo.get("description") or "").strip(),
        "url": repo.get("html_url", ""),
        "homepage": homepage,
        "language": repo.get("language") or "",
        "stars": repo.get("stargazers_count", 0) or 0,
        "forks": repo.get("forks_count", 0) or 0,
        "topics": (repo.get("topics") or [])[:4],
        "updated": pushed.strftime("%b %Y") if pushed else "",
        "updated_iso": pushed.isoformat() if pushed else "",
    }


def _shape_profile(user: dict) -> dict:
    return {
        "login": user.get("login", ""),
        "name": user.get("name") or user.get("login", ""),
        "avatar": user.get("avatar_url", ""),
        "url": user.get("html_url", ""),
        "bio": (user.get("bio") or "").strip(),
        "location": user.get("location") or "",
        "public_repos": user.get("public_repos", 0) or 0,
        "followers": user.get("followers", 0) or 0,
        "following": user.get("following", 0) or 0,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_profile() -> dict:
    """Public GitHub profile fields, or {} when unavailable."""
    username = settings.GITHUB_USERNAME
    if not username:
        return {}

    def build():
        data = _get(f"/users/{username}")
        return _shape_profile(data) if isinstance(data, dict) else {}

    return _cached(f"profile:{username}", build) or {}


def get_repositories(limit: int | None = None) -> list[dict]:
    """Curated, ranked repositories. Returns [] when unavailable."""
    username = settings.GITHUB_USERNAME
    if not username:
        return []

    limit = limit or settings.GITHUB_MAX_REPOS
    excluded = {name.lower() for name in settings.GITHUB_EXCLUDE_REPOS}

    def build():
        data = _get(f"/users/{username}/repos?per_page=100&sort=pushed&type=owner")
        if not isinstance(data, list):
            return []
        meaningful = [repo for repo in data if _is_meaningful(repo, excluded)]
        meaningful.sort(key=_score, reverse=True)
        return [_shape_repo(repo) for repo in meaningful[:24]]

    repos = _cached(f"repos:{username}", build) or []
    return repos[:limit]


def get_overview() -> dict:
    """Everything the page needs in one call, plus an availability flag."""
    profile = get_profile()
    repos = get_repositories()

    languages: dict[str, int] = {}
    stars = 0
    for repo in repos:
        stars += repo["stars"]
        if repo["language"]:
            languages[repo["language"]] = languages.get(repo["language"], 0) + 1

    return {
        "profile": profile,
        "repos": repos,
        "available": bool(profile or repos),
        "total_stars": stars,
        "top_languages": sorted(languages, key=languages.get, reverse=True)[:5],
    }
