# Volvo API

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.postman.com/import/url?url=https%3A%2F%2Fraw.githubusercontent.com%2Fmostafahakak%2FVolvo%2Fmain%2Fdocs%2FVolvo-API.postman_collection.json)

That button imports [Volvo-API.postman_collection.json](Volvo-API.postman_collection.json) into Postman. Run **Login** or **Admin login** first. Those requests save the JWT into collection variables, and the other requests send it for you.

## Base URL

| Server | Base URL |
|--------|----------|
| Live app (Render) | `https://volvo-bd1q.onrender.com` |
| Hetzner | `http://2.28.45.175` |
| Local | `http://127.0.0.1:8000` |

Every path below is added after that host. Example: `GET https://volvo-bd1q.onrender.com/api/list_car_model`.

In Postman, change the `baseUrl` collection variable if you are not calling Render.

## How to call it

Send JSON with `Content-Type: application/json`.

Protected routes need:

```http
Authorization: Bearer <access_token>
```

Most successful responses look like:

```json
{ "status": true, "data": {}, "message": "success" }
```

Errors use HTTP 4xx/5xx. Some use `{ "status": false, "message": "..." }`, others `{ "error": "..." }` or `{ "detail": "..." }`.

Two logins exist:

| Who | Request | Token variable in Postman |
|-----|---------|---------------------------|
| Mobile user | `POST /api/login` with `mobile` and `password` | `accessToken` |
| Dashboard staff | `POST /api/admin/login/` with `email` and `password` | `adminToken` |

A new signup is **not** verified. The user can log in, but `POST /api/book_a_service` stays blocked until a staff user sets `is_verified` to true.

Admin paths end with a slash (`/api/admin/users/`). Mobile paths usually do not (`/api/login`).

Image fields on create/update accept either a file (`multipart/form-data`) or an existing URL in the matching `*_url` field.

---

## Account

### POST `/api/signup`

No auth.

```json
{
  "mobile": "+201000000000",
  "email": "user@example.com",
  "password": "your-password",
  "password2": "your-password",
  "first_name": "First",
  "last_name": "Last"
}
```

`email` and password may be omitted. If you send a password, `password` and `password2` must match.

### POST `/api/login`

No auth. Body: `mobile`, `password`.

Response includes `access`, `refresh`, and `user_data`. Use `access` as the Bearer token. Login does not require `is_verified`.

### GET `/api/check_mobile`

No auth. Query: `mobile` (or `phone`). Tells you whether that number is already registered.

### POST `/api/firebase_login`

No auth. Body: `id_token` (Firebase ID token), `mobile`, optional `first_name`, `last_name`, `email`. Creates the user if needed and returns the same JWT payload as login.

### POST `/api/social_auth_check`

No auth. Body: `id_token`. If that Firebase email already has an account, returns JWT tokens. Otherwise returns `exists: false`.

### GET `/api/profile`

User token. Current user, including loyalty fields.

### POST `/api/update_profile`

User token. Body: `email`, `mobile`, `first_name`, `last_name`, optional `avatar`. Another user’s mobile cannot be taken.

### POST `/api/change_password`

User token. Body: `old_password`, `new_password`, `conf_password`.

### POST `/api/notification_token`

User token. Body: `fcm_token` or `notification_token`. Stored on the user and used for push.

### POST `/api/delete_account`

User token. Deactivates the account and clears the push token.

### POST `/api/admin/login/`

No auth. Body: `email`, `password`. The user must be staff. Response: `access`, `refresh`, `user_data`.

---

## Cars and loyalty

### GET `/api/list_car_model`

No auth. Car catalog ordered by `sort_order`, then id. Each row includes `car_model`, year range, `model_type`, `details`, and `image` (URL when one is set).

### POST `/api/add_user_car`

User token.

```json
{
  "car_model": 1,
  "model_year": 2022,
  "chassis_number": "VIN",
  "plate_number": "ABC123"
}
```

Optional registration photos: `car_document_front`, `car_document_back`, or the `*_url` fields. The car is unverified until staff approves it. Only verified cars can be used to book a service.

### GET `/api/list_user_cars`

User token. Cars belonging to the logged-in user.

### PATCH `/api/user_car/<id>`

User token. Update plate, chassis, year, or documents. Verified cars cannot be edited unless staff set `allow_user_edit`.

### DELETE `/api/user_car/<id>`

User token. Deletes that user’s car, with the same verified-car restriction as update.

### GET `/api/loyalty_level`

User token. Loyalty tiers (`type`, `point`, `point_per_pound`).

### POST `/api/redeem_points`

User token. Body: `service_id`, `price`. Spends points for that service. The user must have a loyalty tier and enough points.

---

## Catalog

### GET `/api/home_banners`

No auth. Active home-screen slides: `label`, `text`, `image`, `sort_order`.

### GET `/api/maintenance_schedule_types`

No auth. Mileage types such as `10k`, `20K`, with `name`, `name_ar`, `sort_order`.

### GET `/api/maintenance_schedule`

No auth. Optional query:

| Query | Meaning |
|-------|---------|
| `car_model_id` | Only schedules for that car |
| `maintenance_type_id` | Only schedules that include that type |

Each schedule includes `approximate_price`, `maintenance_types_detail`, `compatible_car_models_detail`, and `service_items_detail` (the included parts, such as engine oil and filters).

### GET `/api/list_branches`

No auth. Branch `name`, `address`, phones, `maps_url`, and latitude/longitude. If the map link contains coordinates and the lat/lng fields are empty, the API fills them from the link.

### GET `/api/list_branches_slot`

User token. Slot configuration rows for branches.

### GET `/api/list_service_categories`

No auth. Book-a-service groups, for example Regular Maintenance. Fields: `name`, `name_ar`, `icon`, `sort_order`.

### GET `/api/list_services`

User token. Optional query: `category_id`, `car_model_id`.

Services linked to a maintenance schedule return that schedule’s price, compatible cars, and included items.

### GET `/api/list_service_items`

User token. Optional query: `service_id`. Parts catalog: `name`, `name_ar`, `description`, `price`.

### GET `/api/list_accessories`

No auth. Accessory products, including gallery and video URLs.

### GET `/api/list_offers`

User token. Special-offer products.

### GET `/api/list_used_cars`

User token. Used cars and their images.

### GET `/api/list_aboutus`

No auth. About-us text rows.

### GET `/api/site_contact_settings`

No auth. WhatsApp, technical hotline, tow-truck contacts (`winch_contacts` with `area` / `name` and `phone_e164`), theme defaults, starting points for new users, and the home carousel heading.

### GET `/api/list_available_times`

User token. Query: `branch_id`, `date` (`YYYY-MM-DD`). Returns time slots that are still open that day. The branch must be marked open for that date.

---

## Bookings and support

### POST `/api/book_a_service`

User token. The account must be verified, and the car must belong to that user and be verified.

```json
{
  "services": [1],
  "time_id": 1,
  "user_car": 1,
  "branch_id": 1,
  "date": "2026-10-20",
  "slot_index": 0,
  "customer_note": "",
  "service_item_selections": [{ "service_id": 1, "item_ids": [1] }]
}
```

`slot_index` is `0`, `1`, or `2` (three bookings can share one hour). `date` is `YYYY-MM-DD`. A service that is limited to one branch can only be booked there.

### GET `/api/my_service_bookings`

User token. The current user’s bookings, newest first.

### GET `/api/my_history`

User token. Past service history and points.

### POST `/api/book_used_cars`

User token. Body: `used_cars` (id), `date`.

### POST `/api/book_accessories`

User token. Body: `accessories` (id), `branch`, `date`.

### POST `/api/feedback`

No auth. Body: `fullname`, `email`, `phone_number`, `feedback_subject`, `car_model` (id), `feedback_details`.

### POST `/api/contact_us`

No auth. Body: `fullname`, `email`, `phone_number`, `car_model` (id), `inquiry_details`.

### POST `/api/create_technical_assistant`

User token. Body: `question`.

### GET `/api/list_technical_assistant`

User token. This user’s questions and answers.

### POST `/api/road_help`

User token. Body: `car` (user car id), `latitude`, `langtiude` (this spelling matches the API).

### GET `/api/my_notifications`

User token. In-app notification history.

### POST `/api/my_notifications/<id>/read`

User token. Marks that notification as read.

---

## Admin API

Every route below needs the staff token from `POST /api/admin/login/`, except the login itself.

List endpoints are `GET`. Create is `POST` on the collection URL. One record is `GET`, `PATCH` (or `PUT`), and `DELETE` on `/api/admin/<resource>/<id>/`.

| Resource | List / create | One record |
|----------|---------------|------------|
| Users | `GET /api/admin/users/` and `POST /api/admin/users/create/` | `/api/admin/users/<id>/` |
| Bookings | `GET /api/admin/bookings/` and `POST /api/admin/bookings/create/` | `/api/admin/bookings/<id>/` |
| User cars | `GET /api/admin/user_cars/` | `PATCH /api/admin/user_cars/<id>/` |
| Loyalty | `GET /api/admin/loyalty_levels/` | `/api/admin/loyalty_levels/<id>/` |
| Branches | `GET/POST /api/admin/branches/` | `/api/admin/branches/<id>/` |
| Car models | `GET/POST /api/admin/car_models/` | `/api/admin/car_models/<id>/` |
| Service categories | `GET/POST /api/admin/service_categories/` | `/api/admin/service_categories/<id>/` |
| Service items | `GET/POST /api/admin/service_items/` | `/api/admin/service_items/<id>/` |
| Services | `GET/POST /api/admin/services/` | `/api/admin/services/<id>/` |
| Accessories | `GET/POST /api/admin/accessories/` | `/api/admin/accessories/<id>/` |
| Maintenance types | `GET/POST /api/admin/maintenance_schedule_types/` | `/api/admin/maintenance_schedule_types/<id>/` |
| Maintenance schedules | `GET/POST /api/admin/maintenance_schedules/` | `/api/admin/maintenance_schedules/<id>/` |
| Home banners | `GET/POST /api/admin/home_banners/` | `/api/admin/home_banners/<id>/` |

### Users

Create body: `mobile`, `email`, `first_name`, `last_name`, `password` (at least 8 characters), optional `is_staff`, `is_superuser`, `next_service_km`, `next_service_date`.

Update body can set `is_verified`, `is_active`, `user_type`, points, and the next-service fields. Set `is_verified: true` so the customer can book.

### Bookings

`GET /api/admin/bookings/` filters: `workflow_status`, `user_id`, `date_from`, `date_to`, `phone`.

`workflow_status` is one of `pending_confirmation`, `confirmed`, `in_progress`, `completed`, `cancelled`.

Create body: `services` (list of ids), `user_car`, `branch_id`, `time_id`, `date`, optional `slot_index`.

Update body: `workflow_status`, `status`, `branch`, `time`, `date`, `slot_index`. The booking object includes the car VIN (`chassis_number`).

### User cars

`GET /api/admin/user_cars/?user_id=1` limits the list to one customer.

`PATCH` can set `is_verified` and `allow_user_edit`.

### POST `/api/admin/user_cars/<id>/notify/`

Body: `title`, `body` (or `message`). Saves an in-app notification and sends a push when the user has a device token.

### POST `/api/admin/car_models/reorder/`

Body: `{ "order": [3, 1, 2] }`. The list is every model id in the order the app should show them. This writes `sort_order`.

### Maintenance schedules

Create or update with `maintenance_types` (list of type ids), `compatible_car_models` (car model ids), `service_items` (item ids), `approximate_price`, and optional `car_model`. Saving a schedule also creates or updates the matching bookable service under Regular Maintenance.

### Open booking days

`GET /api/admin/booking_open_days/?branch_id=1` lists days that branch can take bookings.

`POST /api/admin/booking_open_days/bulk/`

```json
{
  "branch_id": 1,
  "date_from": "2026-10-20",
  "date_to": "2026-10-24",
  "skip_fridays": true,
  "hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
}
```

`DELETE` on that same URL removes the range. Body: `branch_id`, `date_from`, `date_to`.

`PATCH /api/admin/booking_open_days/<id>/` body: `hours`, integers from 9 through 18.

### GET and PATCH `/api/admin/site_contact/`

Fields: `whatsapp_e164`, `tech_hotline_e164`, `winch_primary`, `winch_secondary`, `winch_contacts`, `app_theme_default` (`light`, `dark`, or `system`), `user_can_change_theme`, `new_user_default_points`, `home_carousel_heading`.

Tow-truck rows:

```json
{ "winch_contacts": [{ "area": "Cairo", "phone": "+201000000000" }] }
```

`name` is accepted as an alias of `area`.

---

## Django admin site

`/admin/` is the HTML admin (Jazzmin), not this JSON API. Sign in there with the user’s mobile number, because `USERNAME_FIELD` is `mobile`.
