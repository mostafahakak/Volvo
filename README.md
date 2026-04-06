# Volvo Django API

REST API for the Volvo mobile app: JWT authentication, cars, branches, bookings, loyalty, and content. Built with **Django 4.x**, **Django REST Framework**, and **Simple JWT**.

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

| Render setting | Use this |
|----------------|----------|
| **Root Directory** | **Leave empty** (or `.`). Do **not** set `volvo-master` — the build will fail with `cd: .../volvo-master: No such file or directory`. |
| **Build Command** | `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && python manage.py collectstatic --noinput` — **no `migrate` here**: the persistent disk is not mounted during build. |
| **Start Command** | Leave **empty** to use `Procfile`, or set: `bash start_render.sh` (runs `migrate` then Gunicorn). |
| **Python version** | Match `PYTHON_VERSION` (e.g. `3.12.0`) if you set it. |

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

Typical **build**:

```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Do **not** run `migrate` in the build step if `DATABASE_PATH` points at a persistent disk — use `start_render.sh` / `Procfile` instead.

`requirements.txt` is a **minimal** production set (Django, DRF, JWT, Gunicorn, **`django-import-export`** for `app/admin.py`, etc.). The previous large export is kept as `requirements-legacy.txt` for reference only.

Typical **start** (see `Procfile` → `start_render.sh`):

```bash
bash start_render.sh
```

On boot, **Gunicorn** loads `volvo/wsgi.py`, which prints a line like:

`[Volvo API] WSGI loaded — deploy active | <UTC time> | RENDER=True | service=<name> | url=https://...`

That line appears in **Render → Logs** so you can confirm a new deploy is live. (Each worker may log once.)

Use a persistent disk and set `DATABASE_PATH` (and optionally `MEDIA_ROOT`) to paths **on that disk** so SQLite and uploads survive restarts.

## API overview

All app routes are under **`/api/`**. Responses usually wrap payloads as:

```json
{ "status": true, "data": ..., "message": "..." }
```

Errors may use `status: false` and HTTP 4xx/5xx. The mobile client uses **`Authorization: Bearer <access_token>`** for protected endpoints.

### Authentication (`user/api/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/signup` | No | Register: `email`, `mobile`, `password`, `password2`, `first_name`, `last_name`. New users are created **verified** so they can log in immediately. |
| POST | `/api/login` | No | JWT login: `mobile`, `password`. Returns `access`, `refresh`, `user_data`. Requires `is_verified=True`. |
| GET | `/api/profile` | Yes | Current user profile. |
| POST | `/api/update_profile` | Yes | Update profile: `email`, `mobile`, `first_name`, `last_name`, optional `avatar`. Another user’s mobile cannot be taken. |
| POST | `/api/change_password` | Yes | `old_password`, `new_password`, `conf_password`. |
| POST | `/api/add_user_car` | Yes | Add a car: `car_model`, `model_year`, `chassis_number`, `plate_number`. |
| GET | `/api/loyalty_level` | Yes | Loyalty tiers configuration. |

### Application data (`app/api/`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/list_car_model` | No* | Car models (catalog). |
| GET | `/api/maintenance_schedule` | No* | Maintenance schedules. |
| GET | `/api/my_history` | Yes | User service history. |
| GET | `/api/list_user_cars` | Yes | Current user’s cars. |
| GET | `/api/list_branches` | No* | Branches. |
| GET | `/api/list_branches_slot` | Yes | Branch slot configuration. |
| GET | `/api/list_services` | Yes | Services. |
| GET | `/api/list_accessories` | Yes | Accessories (no discount). |
| GET | `/api/list_offers` | Yes | Discounted accessories (“offers”). |
| GET | `/api/list_used_cars` | Yes | Used cars (+ images). |
| POST | `/api/book_used_cars` | Yes | Book a used car. |
| POST | `/api/book_accessories` | Yes | Book accessories. |
| GET | `/api/list_aboutus` | No* | About us content. |
| POST | `/api/feedback` | No* | Feedback form. |
| POST | `/api/contact_us` | No* | Contact form. |
| GET | `/api/list_available_times` | Yes | Query: `branch_id`, `date` — available time slots. |
| POST | `/api/create_technical_assistant` | Yes | Technical assistant question. |
| GET | `/api/list_technical_assistant` | Yes | User’s technical assistant threads. |
| POST | `/api/road_help` | Yes | Road assistance: `langtiude`, `latitude`, `car` (user car id). |
| POST | `/api/book_a_service` | Yes | Book service: `services` (ids), `time_id`, `user_car`, `branch_id`, `date`. |
| POST | `/api/redeem_points` | Yes | Redeem points for a service: `service_id`, `price`. Requires `user.user_type` set. |

\* *Public in code today; tighten with `IsAuthenticated` if you need to hide catalog from anonymous clients.*

## Project layout (main Python modules)

| Path | Role |
|------|------|
| `manage.py` | Django entrypoint. |
| `volvo/settings.py` | Settings, DB, JWT, `REST_FRAMEWORK`, optional Firebase. |
| `volvo/urls.py` | Routes `/admin/`, `/api/` → `app.api.urls`, `user.api.urls`. |
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
