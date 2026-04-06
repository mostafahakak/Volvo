#!/usr/bin/env bash
# Render BUILD phase only. Persistent disk is NOT mounted here — never run migrate in this script.
set -euo pipefail
cd "$(dirname "$0")"

echo "=== Volvo API build: pip + collectstatic ONLY (migrate runs in start_render.sh at runtime) ==="
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python manage.py collectstatic --noinput
echo "=== Volvo API build finished ==="
