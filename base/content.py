"""
Single source of truth for every piece of written content on the site.

Edit this file to update the portfolio — no template changes required.

Every section below renders only when it has content, so deleting an entry or
emptying a list simply removes that block from the page. Nothing here is
invented: the profile, skills, links and education come from the GitHub
profile and profile README for `pprathamjaiswal`, and from this project's own
source tree.
"""

from __future__ import annotations

from django.conf import settings  # type: ignore[reportMissingModuleSource]

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

PROFILE = {
    "name": "Pratham Jaiswal",
    "first_name": "Pratham",
    "title": "Full-Stack AI Engineer",
    "subtitle": "Full-Stack AI Engineer · MERN Stack Developer",
    # Rotating words in the hero headline.
    "roles": [
        "Full-Stack AI Engineer",
        "MERN Stack Developer",
        "Software Developer",
        "Full-Stack Developer",
    ],
    "location": "Mumbai, India",
    "email": "pratham.m.jaiswal@gmail.com",
    # Short, recruiter-facing summary used in the hero.
    "tagline": (
        "I build scalable full-stack applications with the MERN stack and "
        "Next.js, and engineer AI-powered features on top of them — from the "
        "interface down to the APIs, data models and model integrations behind it."
    ),
    # Longer introduction used in the About section. Keep it to 2–3 paragraphs.
    "about": [
        "I'm a full stack developer based in Mumbai, currently pursuing my MCA "
        "at Manipal University Jaipur. I work across the full stack, and most of "
        "what I know came from building: picking an idea, shipping it, and "
        "rewriting the parts that turned out badly the first time.",
        "My core stack is MERN — MongoDB, Express, React and Node.js — extended "
        "with Next.js, TypeScript and Tailwind CSS on the front end, and Python "
        "and Django on the back end. I care about the parts users never see: "
        "clean data models, sensible error handling, and pages that stay fast on "
        "a mid-range phone.",
        "On the AI side I build with generative AI and LLM APIs, applying them to "
        "practical product features rather than demos, and I keep a steady habit "
        "of data structures and algorithms practice. I'm open to software "
        "engineering roles.",
    ],
    # Optional CV. Drop the file at static/docs/resume.pdf and set to True.
    "resume_enabled": False,
    "resume_path": "docs/resume.pdf",
    # Availability pill shown in the hero. Set to None to hide it.
    "availability": "Open to Software Engineering Roles",
}

# GitHub avatar for `pprathamjaiswal`. To use your own photo instead, drop it at
# static/img/profile.jpg and set USE_LOCAL_AVATAR = True.
AVATAR_URL = "https://avatars.githubusercontent.com/u/85238761?v=4"
USE_LOCAL_AVATAR = False

# ---------------------------------------------------------------------------
# GitHub links
#
# These are plain strings, deliberately separate from the live API data in
# base/github.py: the profile and repository links must keep working even when
# GitHub is unreachable, rate-limiting us, or the token has expired.
# ---------------------------------------------------------------------------

# Single source of truth: the username comes from settings (GITHUB_USERNAME in
# the environment), so the links here and the API calls can never disagree.
GITHUB_USERNAME = settings.GITHUB_USERNAME
GITHUB_PROFILE_URL = f"https://github.com/{GITHUB_USERNAME}"
GITHUB_REPOS_URL = f"{GITHUB_PROFILE_URL}?tab=repositories"

# ---------------------------------------------------------------------------
# Social links — an entry with an empty url is skipped automatically
# ---------------------------------------------------------------------------

SOCIALS = [
    {
        "name": "GitHub",
        "url": "https://github.com/pprathamjaiswal",
        "handle": "@pprathamjaiswal",
        "icon": "github",
        "primary": True,
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com/in/pratham-jaiswal-552168203/",
        "handle": "Pratham Jaiswal",
        "icon": "linkedin",
        "primary": True,
    },
    {
        "name": "X",
        "url": "https://x.com/Pratham48329874",
        "handle": "@Pratham48329874",
        "icon": "x",
        "primary": False,
    },
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/pratham.jaiswal/",
        "handle": "@pratham.jaiswal",
        "icon": "instagram",
        "primary": False,
    },
    {
        "name": "Email",
        "url": "mailto:pratham.m.jaiswal@gmail.com",
        "handle": "pratham.m.jaiswal@gmail.com",
        "icon": "mail",
        "primary": True,
    },
]

# ---------------------------------------------------------------------------
# Skills — grouped exactly as they appear on the site
# ---------------------------------------------------------------------------

SKILL_GROUPS = [
    {
        "name": "Languages",
        "icon": "code",
        "items": ["JavaScript", "TypeScript", "Python", "C++", "SQL"],
    },
    {
        "name": "Frontend",
        "icon": "layout",
        "items": [
            "React",
            "Next.js",
            "Redux",
            "Tailwind CSS",
            "HTML5",
            "CSS3",
        ],
    },
    {
        "name": "Backend",
        "icon": "server",
        "items": ["Node.js", "Express", "Django", "REST APIs"],
    },
    {
        "name": "Databases",
        "icon": "database",
        "items": ["MongoDB", "MySQL", "SQLite", "Firebase"],
    },
    {
        "name": "AI Engineering",
        "icon": "sparkles",
        "items": [
            "Generative AI & LLM APIs",
            "AI feature integration",
            "Machine learning foundations",
            "Regression & classification",
        ],
    },
    {
        "name": "Tools & Deployment",
        "icon": "tool",
        "items": ["Git", "GitHub", "Gunicorn", "WhiteNoise", "Azure", "AWS", "VS Code"],
    },
]

# Compact strip of headline technologies shown under the hero.
MARQUEE_SKILLS = [
    "MongoDB",
    "Express",
    "React",
    "Node.js",
    "Next.js",
    "TypeScript",
    "JavaScript",
    "Python",
    "Django",
    "Tailwind CSS",
    "LLM APIs",
    "MySQL",
    "Redux",
    "Git",
    "Azure",
    "AWS",
]

# ---------------------------------------------------------------------------
# What I focus on — three short cards under About
# ---------------------------------------------------------------------------

FOCUS_AREAS = [
    {
        "icon": "layout",
        "title": "Full-stack development",
        "body": (
            "MERN applications end to end — component-driven React and Next.js "
            "interfaces, built mobile-first, accessible and fast."
        ),
    },
    {
        "icon": "server",
        "title": "Scalable back-ends & APIs",
        "body": (
            "REST APIs and data models with Node.js, Express and Django, with "
            "real validation, error handling and sensible caching."
        ),
    },
    {
        "icon": "sparkles",
        "title": "AI engineering",
        "body": (
            "Generative AI and LLM APIs integrated into production web features "
            "rather than demos, with graceful failure handling."
        ),
    },
]

# ---------------------------------------------------------------------------
# Experience — leave the list empty to hide the section entirely
#
# Example entry:
#   {
#       "role": "Software Engineer",
#       "company": "Company Name",
#       "url": "https://example.com",
#       "location": "Mumbai, India",
#       "start": "Jun 2025",
#       "end": "Aug 2025",
#       "summary": "One line on what the team did.",
#       "highlights": ["Shipped X, cutting Y by Z%."],
#       "stack": ["React", "Node.js"],
#   }
# ---------------------------------------------------------------------------

EXPERIENCE: list[dict] = []

# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

EDUCATION = [
    {
        "degree": "Master of Computer Applications (MCA) — Distance Learning",
        "institution": "Manipal University Jaipur",
        "location": "",
        "period": "In progress",
        "details": "",
    },
    {
        "degree": "Bachelor of Science and Information Technology (B.Sc-IT)",
        "institution": "Matrushri Kashiben Motilal Patel College",
        "location": "Padmakar Colony, Near Thakurli Railway Station, Dombivli East, Kalyan, Thane, Maharashtra 421201",
        "period": "2018 - 2021",
        "details": "",
    },
]

# ---------------------------------------------------------------------------
# Certifications — add entries as {"name", "issuer", "year", "url"}
# ---------------------------------------------------------------------------

CERTIFICATIONS: list[dict] = []

# ---------------------------------------------------------------------------
# Achievements — add entries as {"title", "detail", "year"}
# ---------------------------------------------------------------------------

ACHIEVEMENTS: list[dict] = []

# ---------------------------------------------------------------------------
# Hand-picked projects.
#
# These render above the live GitHub feed. Leave the list empty and the
# Projects section falls back entirely to your curated GitHub repositories.
#
#   {
#       "name": "Project name",
#       "description": "What it does and why it exists.",
#       "stack": ["Django", "SQLite"],
#       "repo": "https://github.com/user/repo",
#       "demo": "https://example.com",
#       "featured": True,
#   }
# ---------------------------------------------------------------------------

FEATURED_PROJECTS: list[dict] = []

# ---------------------------------------------------------------------------
# SEO
# ---------------------------------------------------------------------------

SEO = {
    "title": "Pratham Jaiswal — Full-Stack AI Engineer | MERN Stack Developer",
    "description": (
        "Pratham Jaiswal is a software developer in Mumbai building scalable "
        "full-stack applications with the MERN stack, Next.js and Django, and "
        "engineering AI-powered features with generative AI and LLM APIs."
    ),
    "keywords": (
        "Pratham Jaiswal, full stack AI engineer, MERN stack developer, "
        "software developer, software engineer, MongoDB, Express, React, "
        "Node.js, Next.js, TypeScript, Python, Django, generative AI, LLM, "
        "Mumbai"
    ),
    "locale": "en_IN",
    "theme_color_dark": "#08090c",
    "theme_color_light": "#f7f8fa",
}

# ---------------------------------------------------------------------------
# Navigation — id must match a section id in the template
# ---------------------------------------------------------------------------

NAV_LINKS = [
    {"id": "about", "label": "About"},
    {"id": "skills", "label": "Skills"},
    {"id": "projects", "label": "Projects"},
    {"id": "experience", "label": "Experience"},
    {"id": "education", "label": "Education"},
    {"id": "contact", "label": "Contact"},
]


def nav_links(context: dict) -> list[dict]:
    """Drop nav entries whose section will not be rendered."""
    present = {
        "about": True,
        "skills": bool(SKILL_GROUPS),
        "projects": bool(FEATURED_PROJECTS) or context.get("has_github", False),
        "experience": bool(EXPERIENCE),
        "education": bool(EDUCATION) or bool(CERTIFICATIONS) or bool(ACHIEVEMENTS),
        "contact": True,
    }
    return [link for link in NAV_LINKS if present.get(link["id"], True)]
