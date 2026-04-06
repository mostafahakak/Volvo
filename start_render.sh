#!/usr/bin/env bash
# Render: persistent disk is mounted at *runtime*, not during the build step.
# Run migrations here so DATABASE_PATH (e.g. /var/data/db.sqlite3) exists on the disk.
set -euo pipefail
cd "$(dirname "$0")"

if [[ -n "${DATABASE_PATH:-}" ]]; then
  mkdir -p "$(dirname "$DATABASE_PATH")"
fi
if [[ -n "${MEDIA_ROOT:-}" ]]; then
  mkdir -p "$MEDIA_ROOT"
fi

python manage.py migrate --noinput
exec gunicorn volvo.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
