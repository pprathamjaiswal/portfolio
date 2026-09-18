# Pratham Jaiswal — Developer Portfolio

A single-page developer portfolio built with Django 5.2, served as a plain
server-rendered site: no build step, no npm, no JavaScript framework.
Repositories are pulled live from the GitHub API **on the server**, so the
access token never reaches the browser.

---

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit .env — see below
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000.

Generate a secret key for `.env`:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

To read contact messages in the admin:

```bash
python manage.py createsuperuser   # then visit /admin/
```

---

## Editing your content

**Everything written on the page lives in `base/content.py`.** Templates read
from it, so you never need to touch HTML to change a sentence.

| What you want to change | Where |
| --- | --- |
| Name, title, hero text, About paragraphs | `PROFILE` |
| Social links (an empty `url` hides the link) | `SOCIALS` |
| Skill groups and chips | `SKILL_GROUPS` |
| The scrolling technology strip | `MARQUEE_SKILLS` |
| The three cards under About | `FOCUS_AREAS` |
| Work history | `EXPERIENCE` |
| Degrees | `EDUCATION` |
| Certifications | `CERTIFICATIONS` |
| Awards, rankings, wins | `ACHIEVEMENTS` |
| Hand-picked projects shown above the GitHub feed | `FEATURED_PROJECTS` |
| Page title, meta description, keywords | `SEO` |

**Empty lists hide their section entirely.** `EXPERIENCE`, `CERTIFICATIONS`,
`ACHIEVEMENTS` and `FEATURED_PROJECTS` currently ship empty — fill any of them
in and the section appears, correctly numbered, with no other changes.

### Your photo

The hero uses your GitHub avatar by default. To use your own image, save it as
`static/img/profile.jpg` and set `USE_LOCAL_AVATAR = True` in `content.py`.

### Your résumé

Save the PDF as `static/docs/resume.pdf` and set `"resume_enabled": True` in
`PROFILE`. A Résumé button appears in the hero.

---

## GitHub integration

`base/github.py` talks to GitHub from the Django process only.

- **The token is read from the `GITHUB_TOKEN` environment variable.** It is
  never put in a template context, never serialised into JSON, and never
  logged — failures log the status code only.
- Responses are cached for `GITHUB_CACHE_SECONDS` (6 hours by default). A
  second copy is kept for two weeks as a **stale fallback**, so if GitHub is
  down, rate-limits you, or your token expires, the site keeps showing the last
  good data instead of an empty section.
- If there has never been a successful fetch, the Projects section shows a short
  notice with a link to your GitHub profile. The page itself still renders.
- Repositories are **curated, not dumped**: forks, archived, disabled, empty and
  excluded repos are dropped, and the rest are ranked by stars, forks, recency
  of the last push, and how complete the repo looks (description, homepage,
  topics, language). The top `GITHUB_MAX_REPOS` are shown.

A **fine-grained token with read-only access to public repositories** is all you
need. The site also works with no token at all — GitHub just applies its lower
unauthenticated rate limit.

`GET /api/github/repos/` returns the same curated list as JSON. It contains only
public repository fields.

---

## Contact form & notifications

Every message is **saved to the database first**, then emailed to you. That
order matters: if mail is misconfigured or your provider is down, the enquiry is
still safe at `/admin/` — you are never silently losing leads.

Set two things in `.env` to get notified:

```
CONTACT_NOTIFY_EMAIL=you@gmail.com
EMAIL_HOST_USER=you@gmail.com
EMAIL_HOST_PASSWORD=your16charapppassword
```

For Gmail that password must be an **App Password**, not your account password:
turn on 2-Step Verification, then create one at
<https://myaccount.google.com/apppasswords> and enter the 16 characters with no
spaces.

Check it works:

```bash
python manage.py testemail
```

The command prints exactly which setting is missing rather than an SMTP
traceback. With `EMAIL_HOST_USER` blank, mail is printed to the terminal instead
of sent, so you can test the flow with no credentials at all.

How the notification behaves:

- **Sent on a background thread** — SMTP takes a second or two, and the visitor
  should never wait for it.
- **`Reply-To` is the visitor's address**, so hitting Reply in your inbox answers
  them directly.
- **Failures are logged, never shown** — the visitor always sees a clean
  confirmation, and the message stays in the admin.
- Leave `CONTACT_NOTIFY_EMAIL` blank to switch notifications off entirely.

Spam protection: CSRF, a hidden honeypot field, server-side validation, a link
cap in the message body, and a per-IP limit of `CONTACT_RATE_LIMIT` submissions
per hour.

> **Deploying to a free host?** Outbound SMTP is blocked on some platforms. If
> mail works locally but not in production, switch `EMAIL_HOST` to a transactional
> provider (Resend, Brevo, Mailgun — all have free tiers) and use the SMTP
> credentials they give you. No code changes needed.

---

## Routes

| Route | Purpose |
| --- | --- |
| `/` | The portfolio |
| `/contact/` | `POST` only. CSRF protected, rate limited, honeypot-guarded |
| `/api/github/repos/` | Curated repositories as JSON |
| `/sitemap.xml`, `/robots.txt` | SEO |
| `/admin/` | Contact messages (read-only list) |

---

## Deploying free (Vercel + Neon) — recommended

Vercel has zero-configuration Django support: it finds `manage.py`, reads
`WSGI_APPLICATION`, runs `collectstatic` itself and serves static files from its
CDN. `vercel.json` is included.

Unlike a free container host, a Vercel Function does not sleep — no 15-minute
spin-down, no minute-long cold start for whoever opens your link.

### 1. Database (Neon — free, no expiry)

Vercel's filesystem is read-only, so SQLite cannot be used at all. Create a free
Postgres at <https://neon.com> and copy the connection string:

```
postgresql://user:password@ep-something.aws.neon.tech/neondb?sslmode=require
```

### 2. Run migrations against it, from your machine

Vercel does not run migrations. Do it once locally — add the Neon URL to `.env`,
then:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Repeat this step whenever you add a migration.

### 3. Push to GitHub

```bash
git init
git add .
git commit -m "Portfolio"
git branch -M main
git remote add origin https://github.com/pprathamjaiswal/portfolio.git
git push -u origin main
```

`.gitignore` already excludes `.env`, `db.sqlite3` and `staticfiles/`. Check
`git status` before pushing.

### 4. Import on Vercel

<https://vercel.com> → **Add New → Project** → import the repo. Vercel detects
Django automatically. Before clicking Deploy, add these environment variables:

| Key | Value |
| --- | --- |
| `DJANGO_SECRET_KEY` | run `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"` |
| `DJANGO_DEBUG` | `False` |
| `DATABASE_URL` | the Neon string |
| `SITE_URL` | `https://your-project.vercel.app` |
| `GITHUB_TOKEN` | fine-grained, read-only, public repositories |
| `CONTACT_NOTIFY_EMAIL` | your email |
| `EMAIL_HOST_USER` | your Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail App Password, 16 chars, no spaces |
| `DJANGO_TIME_ZONE` | `Asia/Kolkata` |

`ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` fill themselves from `VERCEL_URL` and
`VERCEL_PROJECT_PRODUCTION_URL`, so the first deploy cannot fail with
`DisallowedHost`.

### What the code does differently under serverless

`CONTACT_NOTIFY_SYNC` switches itself on when the `VERCEL` environment variable
is present, so the notification email is sent on the request thread. A Vercel
Function can be frozen the instant it returns a response, which would silently
kill the background thread used on a normal server and lose the email.

---

## Deploying free (Render + Neon) — alternative

`render.yaml` and `build.sh` are included, so Render configures the service
itself. Total time: about 20 minutes.

### 1. Database first (Neon — free, no expiry)

Free hosts wipe the filesystem on every redeploy, so SQLite there loses every
contact message. Create a free Postgres at <https://neon.com>, then copy the
connection string — it looks like:

```
postgresql://user:password@ep-something.aws.neon.tech/neondb?sslmode=require
```

Do **not** use Render's own free Postgres: it expires 30 days after creation.

### 2. Push this project to GitHub

```bash
git init
git add .
git commit -m "Portfolio"
git branch -M main
git remote add origin https://github.com/pprathamjaiswal/portfolio.git
git push -u origin main
```

`.gitignore` already excludes `.env`, `db.sqlite3` and `staticfiles/`, so no
secrets are committed. Verify with `git status` before pushing.

### 3. Create the service

On <https://render.com>: **New → Blueprint**, pick the repository. Render reads
`render.yaml` and fills in most settings, generating `DJANGO_SECRET_KEY` for you.

### 4. Add the five secrets

In the service's **Environment** tab:

| Key | Value |
| --- | --- |
| `DATABASE_URL` | the Neon string from step 1 |
| `SITE_URL` | `https://your-service.onrender.com` (no trailing slash) |
| `GITHUB_TOKEN` | fine-grained, read-only, public repositories |
| `EMAIL_HOST_USER` | your Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail App Password, 16 chars, no spaces |

`ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` are filled automatically from
Render's `RENDER_EXTERNAL_HOSTNAME`, so the first deploy cannot fail with
`DisallowedHost`.

### 5. Create your admin login

Once the deploy is green, open the **Shell** tab:

```bash
python manage.py createsuperuser
```

### What to expect on the free plan

- The service **sleeps after 15 minutes idle**; the next visitor waits roughly a
  minute. Paid plans remove this.
- 750 instance hours per month — enough for one always-available service, with
  no margin for keeping it awake artificially.
- Custom domains and TLS are included.

### Other hosts

`Procfile` and `build.sh` work on Railway, Fly.io, Koyeb and Heroku-style hosts
too. Anywhere else, the manual sequence is:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn portfolio.wsgi:application
```

With `DJANGO_DEBUG=False` the project enables HTTPS redirects, HSTS, secure
cookies and `SECURE_PROXY_SSL_HEADER` automatically. `python manage.py check
--deploy` passes clean.

> Some free hosts block outbound SMTP. If contact emails work locally but not in
> production, point `EMAIL_HOST` at a transactional provider (Resend, Brevo,
> Mailgun) — same settings, no code change.

---

## Security notes

- `.env` is git-ignored. `.env.example` documents the variables with no values.
- No secret is referenced anywhere in `template/`, `static/js/` or `static/css/`.
- The contact form uses Django's CSRF protection, validates on the server,
  rate-limits to `CONTACT_RATE_LIMIT` submissions per IP per hour, and carries a
  hidden honeypot field.
- Admin exposes contact messages as read-only; nothing can be created there.

---

## Project layout

```
portfolio/
├── base/
│   ├── content.py      ← all written content
│   ├── github.py       ← server-side GitHub client (token lives here only)
│   ├── forms.py        ← contact validation + honeypot
│   ├── views.py        ← home, contact, JSON feed, robots
│   └── sitemaps.py
├── portfolio/
│   ├── env.py          ← zero-dependency .env loader
│   └── settings.py     ← everything sensitive read from the environment
├── template/
│   ├── base.html       ← head, meta, SEO, theme bootstrap
│   ├── index.html      ← page shell + section includes
│   └── partials/       ← one file per section
└── static/
    ├── css/style.css   ← design tokens, both themes, all layout
    ├── js/main.js      ← theme, nav, reveals, form (no dependencies)
    ├── img/            ← favicon, OG image
    └── video/          ← dark/light background loops + poster frames
```

---

## Accessibility & performance

- Skip link, landmark elements, labelled controls, visible focus rings.
- `prefers-reduced-motion` disables the background video, the marquee, the
  typing caret and every reveal animation.
- Only the background video matching the active theme is downloaded, and only
  after the page is idle. It pauses when the tab is hidden.
- Fonts load non-blocking with a system-font fallback; icons are one inline SVG
  sprite; static files are compressed and fingerprinted by WhiteNoise.
- The page renders completely without JavaScript — the contact form falls back
  to a normal POST.
# portfolio
# portfolio
