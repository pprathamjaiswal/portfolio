"""
Django settings for the portfolio project.

All secrets and environment-specific values are read from environment
variables (optionally via a local .env file). Nothing sensitive is hardcoded
here and nothing sensitive is ever passed to a template.
"""

from pathlib import Path

from .env import env_bool, env_int, env_list, env_str

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Core
# --------------------------------------------------------------------------

# Never commit a real SECRET_KEY. Generate one with:
#   python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
SECRET_KEY = env_str(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-key-change-me-in-production",
)

DEBUG = env_bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    ["localhost", "127.0.0.1", "[::1]"] if DEBUG else [],
)

# Hosts allowed to submit the contact form (Django 4+ requires the scheme).
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])

# Hosting platforms inject the public hostname at runtime. Trust it
# automatically so a first deploy cannot fail with DisallowedHost, and so the
# contact form does not reject every submission with a CSRF error, before you
# have had a chance to set the URL by hand.
_PLATFORM_HOSTS = [
    env_str("RENDER_EXTERNAL_HOSTNAME", ""),  # Render
    env_str("VERCEL_PROJECT_PRODUCTION_URL", ""),  # Vercel — stable production URL
    env_str("VERCEL_URL", ""),  # Vercel — this specific deployment
]

for _host in _PLATFORM_HOSTS:
    _host = _host.replace("https://", "").replace("http://", "").strip("/")
    if not _host:
        continue
    if _host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_host)
    _origin = f"https://{_host}"
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_origin)

# True when running as a Vercel Function rather than a long-lived server.
IS_SERVERLESS = bool(env_str("VERCEL", ""))

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "base",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "portfolio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "template"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "portfolio.wsgi.application"

# SQLite locally; a managed Postgres in production.
#
# Free hosts (Render, Koyeb, Fly) give your app an EPHEMERAL disk — the file
# system is wiped on every redeploy and every spin-down. A SQLite file there
# means your contact messages disappear. Set DATABASE_URL to a managed Postgres
# (Neon's free tier works well) and the data survives.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASE_URL = env_str("DATABASE_URL", "")
if DATABASE_URL:
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        # Managed Postgres providers require TLS.
        ssl_require=not DATABASE_URL.startswith("sqlite"),
    )

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env_str("DJANGO_TIME_ZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Static files
# --------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Manifest storage fingerprints filenames so browsers can cache them
        # for a year. Our subclass sets manifest_strict = False, so a stale or
        # incomplete manifest degrades to an unhashed URL instead of raising
        # and 500-ing every page. In DEBUG, runserver serves the source files
        # directly and the manifest is not consulted at all.
        "BACKEND": "portfolio.storage.ResilientManifestStaticFilesStorage",
    },
}

WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365

# --------------------------------------------------------------------------
# Cache — backs the GitHub API layer so the site never hammers GitHub
# --------------------------------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "portfolio-cache",
        "TIMEOUT": 60 * 30,
        "OPTIONS": {"MAX_ENTRIES": 512},
    }
}

# --------------------------------------------------------------------------
# GitHub integration (server-side only — never exposed to the browser)
# --------------------------------------------------------------------------

GITHUB_USERNAME = env_str("GITHUB_USERNAME", "pprathamjaiswal")

# Read from the environment only. This value is used exclusively inside
# base/github.py, which runs on the server. It is never added to a template
# context, never serialised into JSON, and never logged.
GITHUB_TOKEN = env_str("GITHUB_TOKEN", "")

# How long repository data is cached before GitHub is queried again.
GITHUB_CACHE_SECONDS = env_int("GITHUB_CACHE_SECONDS", 60 * 60 * 6)

# Maximum number of repositories rendered in the GitHub section.
GITHUB_MAX_REPOS = env_int("GITHUB_MAX_REPOS", 6)

# Repositories that should never be shown (archived experiments, dotfiles,
# the profile README repo, etc.). Comma-separated in the environment.
GITHUB_EXCLUDE_REPOS = env_list(
    "GITHUB_EXCLUDE_REPOS",
    [GITHUB_USERNAME, "portfolio-old", "test", "demo"],
)

# --------------------------------------------------------------------------
# Site / SEO
# --------------------------------------------------------------------------

SITE_URL = env_str("SITE_URL", "http://127.0.0.1:8000").rstrip("/")

# --------------------------------------------------------------------------
# Contact form
# --------------------------------------------------------------------------

# Max contact submissions accepted from one IP per hour.
CONTACT_RATE_LIMIT = env_int("CONTACT_RATE_LIMIT", 5)

# Where new enquiries are emailed. Leave blank to turn notifications off —
# messages are still saved and readable in the admin.
CONTACT_NOTIFY_EMAIL = env_str("CONTACT_NOTIFY_EMAIL", "")

# Send on the request thread instead of in the background.
#
# Forced on under serverless (Vercel): the platform may freeze or discard the
# instance the moment the response is returned, which would silently kill a
# background thread and lose the notification. A long-lived server (Render,
# gunicorn, runserver) keeps the default background send.
CONTACT_NOTIFY_SYNC = env_bool("CONTACT_NOTIFY_SYNC", IS_SERVERLESS)

# --------------------------------------------------------------------------
# Email
#
# With no EMAIL_HOST_USER set, mail is printed to the console instead of sent,
# so the whole flow can be exercised locally without credentials.
# --------------------------------------------------------------------------

EMAIL_HOST = env_str("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = env_int("EMAIL_PORT", 587)
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_HOST_USER = env_str("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env_str("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = env_int("EMAIL_TIMEOUT", 15)

EMAIL_BACKEND = env_str(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST_USER
    else "django.core.mail.backends.console.EmailBackend",
)

DEFAULT_FROM_EMAIL = env_str(
    "DEFAULT_FROM_EMAIL",
    f"Portfolio <{EMAIL_HOST_USER}>" if EMAIL_HOST_USER else "portfolio@localhost",
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# --------------------------------------------------------------------------
# Security hardening (applied automatically when DEBUG is off)
# --------------------------------------------------------------------------

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env_int("DJANGO_HSTS_SECONDS", 60 * 60 * 24 * 365)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Behind a proxy (Render, Railway, Fly, Heroku, nginx) trust the header.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
