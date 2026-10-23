# Volvo Django API

REST API for the Volvo mobile app: JWT authentication, cars, branches, bookings, loyalty, and content. Built with **Django 4.x**, **Django REST Framework**, and **Simple JWT**.

**API guide:** [docs/API.md](docs/API.md)

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.postman.com/import/url?url=https%3A%2F%2Fraw.githubusercontent.com%2Fmostafahakak%2FVolvo%2Fmain%2Fdocs%2FVolvo-API.postman_collection.json)

## Requirements

- Python 3.10+ (match `PYTHON_VERSION` on your host, e.g. Render)
- pip

## Quick start (local)

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
# From this directory (where manage.py lives):
copy volvo\env.example .env   # optional; see Environment variables
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API base URL (local): `http://127.0.0.1:8000/api/`

## Environment variables

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret; **required in production** (generate a long random string). |
| `DEBUG` | `True` / `False`. Use `False` in production. |
| `ALLOWED_HOSTS` | Comma-separated hosts, e.g. `your-app.onrender.com` or `*` for dev only. |
| `DATABASE_PATH` | Optional. Path to SQLite file (e.g. `/var/data/db.sqlite3` on Render with a persistent disk). Default: `db.sqlite3` next to `manage.py`. |
| `MEDIA_ROOT` | Optional. Uploaded media directory. Default: `media/` under project root. |

Copy `volvo/env.example` to `.env` at the project root and adjust. Do **not** commit `.env`.

## Render.com (this repo)

The GitHub repo **`mostafahakak/Volvo`** has `manage.py` at the **repository root**. There is **no** `volvo-master/` folder on GitHub (that name is only the local folder on your PC).

### Critical: `migrate` must NOT run during Build

If your build log shows **`migrate.py`** or **`MigrationExecutor`**, your **Build Command in the Render dashboard still includes `migrate`**. Remove it. The **persistent disk is only mounted when the web process starts**, so `/var/data/db.sqlite3` cannot be opened during build — you will get `unable to open database file`.

**Use the script in this repo (recommended):**

| Render setting | Value |
|----------------|--------|
| **Root Directory** | **Empty** (not `volvo-master`). |
| **Build Command** | `bash build_render.sh` |
| **Start Command** | `bash start_render.sh` |

`build_render.sh` only runs **pip + collectstatic**. `start_render.sh` runs **`mkdir` → `migrate` → gunicorn** when the disk exists.

Alternative (same steps, no script): Build = `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && python manage.py collectstatic --noinput` — **must not** contain `migrate`. Start = `bash start_render.sh` or empty (uses `Procfile` → `start_render.sh`).

| Render setting | Notes |
|----------------|--------|
| **Python version** | e.g. `PYTHON_VERSION=3.12.0` in Environment. |
| **Procfile** | `web: bash start_render.sh` — if **Start Command** is empty, Render uses this. |

### Environment variables (important)

| Variable | Correct | Wrong |
|----------|---------|--------|
| `ALLOWED_HOSTS` | `volvo-bd1q.onrender.com` (hostname **only**) | `https://volvo-bd1q.onrender.com` — Django expects hostnames, not URLs. |
| `DEBUG` | `False` | — |
| `SECRET_KEY` | Long random string | Never commit or paste in public chats; rotate if leaked. |

Add a **persistent disk** mounted at `/var/data` if you use `DATABASE_PATH=/var/data/db.sqlite3` and `MEDIA_ROOT=/var/data/media`.

**SQLite on Render:** migrations must run **when the web process starts** (see `start_render.sh`), not in the build command — otherwise you get `unable to open database file` because `/var/data` is only available after the disk mounts at runtime. During **build**, `/var/data` may be missing or read-only — **`settings.py` does not create the SQLite directory**; only `start_render.sh` does, immediately before `migrate`.

After a successful deploy, **Logs** should show Gunicorn and a line starting with `[Volvo API] WSGI loaded`.

## Production (Render / similar)

Preferred **build** (same as `build_render.sh`):

```bash
bash build_render.sh
```

Or inline (never add `migrate` here):

```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

`requirements.txt` is a **minimal** production set (Django, DRF, JWT, Gunicorn, **`django-import-export`** for `app/admin.py`, etc.). The previous large export is kept as `requirements-legacy.txt` for reference only.

Typical **start** (see `Procfile` → `start_render.sh`):

```bash
bash start_render.sh
```

On boot, **Gunicorn** loads `volvo/wsgi.py`, which prints a line like:

`[Volvo API] WSGI loaded — deploy active | <UTC time> | RENDER=True | service=<name> | url=https://...`

That line appears in **Render → Logs** so you can confirm a new deploy is live. (Each worker may log once.)

Use a persistent disk and set `DATABASE_PATH` (and optionally `MEDIA_ROOT`) to paths **on that disk** so SQLite and uploads survive restarts.

## API

Every mobile and dashboard endpoint, with request bodies and auth, is in **[docs/API.md](docs/API.md)**.

Import the same requests into Postman with the button at the top of this file, or open `docs/Volvo-API.postman_collection.json`. The collection variable `baseUrl` defaults to `https://volvo-bd1q.onrender.com`.

## Project layout (main Python modules)

| Path | Role |
|------|------|
| `manage.py` | Django entrypoint. |
| `volvo/settings.py` | Settings, DB, JWT, `REST_FRAMEWORK`, optional Firebase. |
| `volvo/urls.py` | Routes `/admin/`, `/api/` → `app.api.urls`, `user.api.urls`, `app.api.admin_urls`. |
| `docs/API.md` | Full API reference. |
| `docs/Volvo-API.postman_collection.json` | Postman collection for every endpoint. |
| `user/models.py` | Custom `User` (`USERNAME_FIELD = mobile`), cars, loyalty, etc. |
| `user/api/views.py` | Signup, login, profile, cars, loyalty, password. |
| `user/api/serializer.py` | `RegisterSerializer`, `LoginSerializer` (JWT + `user_data`), user serializers. |
| `app/models.py` | Branches, bookings, services, used cars, accessories, etc. |
| `app/api/views.py` | List/create endpoints for catalog and bookings. |
| `app/serializers.py` | DRF serializers for app models. |
| `app/messages.py` | Standard success/error wrapper messages. |

## Firebase (optional)

If a service account JSON file is present at the project root (filename pattern ignored by git), Firebase Admin may initialize in `volvo/settings.py` for push-related features. For production, prefer mounting a secret file or secret env instead of committing keys.

## Tests & checks

```bash
python manage.py check
python manage.py test
```

### Manual API smoke test

With the dev server running (`python manage.py runserver`), in another terminal:

```bash
python manual_api_smoke_test.py
```

This script exercises signup, login, JWT calls, and main catalog/booking endpoints against `http://127.0.0.1:8000/api`. It is **not** part of `manage.py test`.

## Mobile app

The Flutter client calls these endpoints via `VolvoApiService` with a configurable base URL (e.g. `https://<your-host>/api`). Ensure `ALLOWED_HOSTS` and HTTPS match your deployment.
