#!/usr/bin/env bash
# Build step run by Render (and usable on any host) on every deploy.
# `set -o errexit` makes the deploy fail loudly instead of shipping a broken
# build — a failed collectstatic must not reach production silently.
set -o errexit
set -o pipefail
set -o nounset

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files"
# Forced off here so the hashed manifest is always written, even if DJANGO_DEBUG
# is left on in the host's environment by mistake.
DJANGO_DEBUG=False python manage.py collectstatic --no-input

echo "==> Applying database migrations"
python manage.py migrate --no-input

echo "==> Build complete"
