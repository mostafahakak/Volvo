# Volvo API

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.postman.com/import/url?url=https%3A%2F%2Fraw.githubusercontent.com%2Fmostafahakak%2FVolvo%2Fmain%2Fdocs%2FVolvo-API.postman_collection.json)

Base URL for the live app: `https://volvo-bd1q.onrender.com`

Call `GET https://volvo-bd1q.onrender.com/api/list_car_model` with no body. Hetzner is `http://2.28.45.175`. Local is `http://127.0.0.1:8000`.

Send `Content-Type: application/json`. Protected calls also send `Authorization: Bearer <access_token>`.

List and save calls usually return:

```json
{ "status": true, "data": {}, "message": "تم بنجاح" }
```

`message` is Arabic for "done successfully". Login and admin login do **not** use this wrapper. They return `access`, `refresh`, and `user_data` at the top level.

A user object inside `user_data` looks like:

```json
{
  "id": 4,
  "first_name": "Sara",
  "last_name": "Ali",
  "username": "user_201000000000",
  "mobile": "+201000000000",
  "email": "sara@example.com",
  "avatar": null,
  "mypoints": 20,
  "is_verified": false,
  "next_service_km": 10000,
  "next_service_date": "2026-11-01",
  "user_type": 1,
  "loyalty_type": "silver",
  "loyalty_id": 1
}
```

`is_verified: false` means the customer can log in but cannot book a service until staff sets it to `true`.

---

## POST `/api/signup`

No token.

```json
{
  "mobile": "+201000000000",
  "email": "sara@example.com",
  "password": "your-password",
  "password2": "your-password",
  "first_name": "Sara",
  "last_name": "Ali"
}
```

`201` response:

```json
{
  "status": true,
  "data": {
    "email": "sara@example.com",
    "mobile": "+201000000000",
    "first_name": "Sara",
    "last_name": "Ali"
  },
  "message": "تم بنجاح"
}
```

If the mobile already exists, `400`:

```json
{ "error": "This Mobile Used Before" }
```

## POST `/api/login`

No token. Body: `{ "mobile": "+201000000000", "password": "your-password" }`

`200` response. Copy `access` into the Authorization header.

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_data": {
    "id": 4,
    "first_name": "Sara",
    "last_name": "Ali",
    "mobile": "+201000000000",
    "email": "sara@example.com",
    "mypoints": 20,
    "is_verified": false,
    "loyalty_type": "silver",
    "loyalty_id": 1
  }
}
```

## GET `/api/check_mobile?mobile=%2B201000000000`

No token. `mobile` must be URL-encoded (`+` becomes `%2B`).

`200`:

```json
{ "status": true, "data": { "exists": true }, "message": "تم بنجاح" }
```

## POST `/api/firebase_login`

No token.

```json
{
  "id_token": "FIREBASE_ID_TOKEN",
  "mobile": "+201000000000",
  "first_name": "Sara",
  "last_name": "Ali",
  "email": "sara@example.com"
}
```

`200` is the same shape as login (`access`, `refresh`, `user_data`). `401` is `{ "error": "Invalid or expired Firebase token" }`.

## POST `/api/social_auth_check`

No token. Body: `{ "id_token": "FIREBASE_ID_TOKEN" }`

If the email already has an account, `200`:

```json
{
  "exists": true,
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user_data": { "id": 4, "email": "sara@example.com", "mobile": "+201000000000" }
}
```

If not, `200`:

```json
{ "exists": false, "email": "sara@example.com", "name": "Sara Ali" }
```

## GET `/api/profile`

User token. No body.

`200`:

```json
{
  "status": true,
  "data": {
    "id": 4,
    "first_name": "Sara",
    "last_name": "Ali",
    "mobile": "+201000000000",
    "email": "sara@example.com",
    "mypoints": 20,
    "is_verified": false,
    "loyalty_type": "silver",
    "loyalty_id": 1
  },
  "message": "تم بنجاح"
}
```

## POST `/api/update_profile`

User token.

```json
{
  "email": "sara@example.com",
  "mobile": "+201000000000",
  "first_name": "Sara",
  "last_name": "Ali"
}
```

`200` `data` is the same user object as profile. If the mobile belongs to someone else, `400` with `"message": "يوجد حساب مسجل برقم الموبايل هذا"`.

## POST `/api/change_password`

User token.

```json
{
  "old_password": "your-password",
  "new_password": "new-password",
  "conf_password": "new-password"
}
```

`200`: `{ "status": true, "data": "You Have Changed Your Password!!", "message": "تم بنجاح" }`

## POST `/api/notification_token`

User token. Body: `{ "fcm_token": "DEVICE_FCM_TOKEN" }`

`200`: `{ "status": true, "data": { "updated": true }, "message": "تم بنجاح" }`

## POST `/api/delete_account`

User token. No body.

`200`:

```json
{ "deleted": true, "message": "Your account has been deactivated." }
```

## POST `/api/admin/login/`

No token. The email must belong to a staff user.

```json
{ "email": "staff@example.com", "password": "your-password" }
```

`200`:

```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "user_data": { "id": 1, "email": "staff@example.com", "is_staff": true }
}
```

Wrong password is `401`:

```json
{ "status": false, "data": "Invalid credentials", "message": "لا يوجد حساب مسجل بهذه البيانات" }
```

---

## GET `/api/list_car_model`

No token. No body. Ordered by `sort_order`.

`200`:

```json
{
  "status": true,
  "data": [
    {
      "id": 1,
      "car_model": "XC90",
      "image": "https://example.com/xc90.png",
      "image_url": "https://example.com/xc90.png",
      "year_from": 2022,
      "year_to": 2025,
      "model_type": "SUV",
      "details": "",
      "sort_order": 0
    }
  ],
  "message": "تم بنجاح"
}
```

## POST `/api/add_user_car`

User token.

```json
{
  "car_model": 1,
  "model_year": 2022,
  "chassis_number": "YV1XXXXXXXXXXXXXX",
  "plate_number": "ABC123"
}
```

`200` `data` is the new car. `is_verified` starts as `false`.

```json
{
  "status": true,
  "data": {
    "id": 9,
    "user": 4,
    "car_model": 1,
    "model_year": 2022,
    "chassis_number": "YV1XXXXXXXXXXXXXX",
    "plate_number": "ABC123",
    "is_verified": false,
    "allow_user_edit": false
  },
  "message": "تم بنجاح"
}
```

## GET `/api/list_user_cars`

User token. `200` `data` is an array of the same car objects, only for the logged-in user.

## PATCH `/api/user_car/9`

User token. Body can include `plate_number`, `chassis_number`, `model_year`.

`200` `data` is the updated car. A verified car returns `400` until staff sets `allow_user_edit` to true.

## DELETE `/api/user_car/9`

User token. `200`: `{ "status": true, "data": null, "message": "تم بنجاح" }`

## GET `/api/loyalty_level`

User token.

`200`:

```json
{
  "status": true,
  "data": [
    { "id": 1, "type": "silver", "point": 0, "point_per_pound": 10 },
    { "id": 2, "type": "gold", "point": 2000, "point_per_pound": 15 },
    { "id": 3, "type": "platinum", "point": 5000, "point_per_pound": 20 }
  ],
  "message": "تم بنجاح"
}
```

## POST `/api/redeem_points`

User token. Body: `{ "service_id": 13, "price": 2500 }`

`200` `data` is the new history row. Not enough points is `400` with `"message": "Your Points Is Not Enough"`.

---

## GET `/api/home_banners`

No token.

`200`:

```json
{
  "status": true,
  "data": [
    { "id": 1, "label": "Offer", "text": "Winter service", "image": "https://example.com/banner.jpg", "sort_order": 0 }
  ],
  "message": "تم بنجاح"
}
```

An empty list is `"data": []`.

## GET `/api/maintenance_schedule_types`

No token.

`200`:

```json
{
  "status": true,
  "data": [
    { "id": 3, "name": "10k", "name_ar": "", "sort_order": 2 }
  ],
  "message": "تم بنجاح"
}
```

## GET `/api/maintenance_schedule`

No token. Optional query: `?car_model_id=1&maintenance_type_id=3`

`200`:

```json
{
  "status": true,
  "data": [
    {
      "id": 2,
      "approximate_price": null,
      "car_model": 1,
      "car_model_name": "XC90",
      "maintenance_type_ids": [3, 7],
      "maintenance_type_name": "10k, 50K",
      "maintenance_type_name_ar": "",
      "maintenance_types_detail": [
        { "id": 3, "name": "10k", "name_ar": "" }
      ],
      "compatible_car_model_ids": [1, 2],
      "compatible_car_models_detail": [
        { "id": 1, "car_model": "XC90" }
      ],
      "service_items_detail": [
        { "id": 3, "name": "Engine Oil 0W20", "name_ar": "زيت محرك 0W20", "price": null }
      ]
    }
  ],
  "message": "تم بنجاح"
}
```

## GET `/api/list_branches`

No token. Latitude and longitude are filled from `maps_url` when those fields are empty.

`200`:

```json
{
  "status": true,
  "data": [
    {
      "id": 4,
      "name": "Katameya",
      "address": "New Cairo",
      "description": "",
      "mobile1": 221298882,
      "mobile2": null,
      "latitude": "29.99",
      "langitude": "31.49",
      "maps_url": "https://maps.app.goo.gl/example"
    }
  ],
  "message": "تم بنجاح"
}
```

The longitude field name is `langitude`.

## GET `/api/list_branches_slot`

User token.

`200` `data`: `[{ "id": 1, "branch": 4, "slot_number": 3 }]`

## GET `/api/list_service_categories`

No token.

`200`:

```json
{
  "status": true,
  "data": [
    { "id": 1, "name": "Regular Maintenance", "name_ar": "صيانة دورية", "icon": null, "icon_url": null, "sort_order": 0 }
  ],
  "message": "تم بنجاح"
}
```

## GET `/api/list_services`

User token. Optional query: `?category_id=1&car_model_id=1`

`200`:

```json
{
  "status": true,
  "data": [
    {
      "id": 13,
      "name": "10k, 50K",
      "name_ar": null,
      "price": null,
      "points": 10,
      "category": 1,
      "category_name": "Regular Maintenance",
      "category_name_ar": "صيانة دورية",
      "only_at_branch": null,
      "branch_name": null,
      "source_maintenance": 2,
      "items_detail": [
        { "id": 3, "name": "Engine Oil 0W20", "name_ar": "زيت محرك 0W20", "description": "", "price": null }
      ],
      "compatible_with_models": [
        { "id": 1, "car_model": "XC90" }
      ]
    }
  ],
  "message": "تم بنجاح"
}
```

When `source_maintenance` is set, `price`, `items_detail`, and `compatible_with_models` come from that maintenance schedule.

## GET `/api/list_service_items`

User token. Optional query: `?service_id=13`

`200` `data`: `[{ "id": 3, "name": "Engine Oil 0W20", "name_ar": "زيت محرك 0W20", "description": "", "price": null }]`

## GET `/api/list_accessories`

No token.

`200`:

```json
{
  "status": true,
  "data": [
    {
      "id": 1,
      "title": "Floor mats",
      "about": "",
      "price": 3500,
      "discount": 0,
      "kind": "accessory",
      "image": "https://example.com/mats.jpg",
      "gallery": ["https://example.com/mats.jpg"],
      "video_url": null,
      "compatible_with": [{ "id": 1, "car_model": "XC90" }]
    }
  ],
  "message": "تم بنجاح"
}
```

## GET `/api/list_offers`

User token. Same object as accessories, with `"kind": "special_offer"`.

## GET `/api/list_used_cars`

User token.

`200` `data`: `[{ "id": 1, "title": "XC60 2019", "description": "", "price": 1500000, "car_model": 5, "branch": 4 }]`

## GET `/api/list_aboutus`

No token. `200` `data`: `[{ "id": 1, "about": "About the dealer." }]`

## GET `/api/site_contact_settings`

No token.

`200`:

```json
{
  "status": true,
  "data": {
    "id": 1,
    "whatsapp_e164": "+201000000000",
    "tech_hotline_e164": "+201000000000",
    "winch_primary": "+201000000001",
    "winch_secondary": "",
    "winch_contacts": [
      { "name": "Cairo", "area": "Cairo", "phone_e164": "+201000000001" }
    ],
    "app_theme_default": "light",
    "user_can_change_theme": true,
    "new_user_default_points": 20,
    "home_carousel_heading": "OFFERS"
  },
  "message": "تم بنجاح"
}
```

## GET `/api/list_available_times?branch_id=4&date=2026-10-20`

User token. `date` is `YYYY-MM-DD`.

`200`:

```json
{
  "status": true,
  "data": [
    { "id": 12, "time": "09:00:00", "branch": 4 },
    { "id": 13, "time": "10:00:00", "branch": 4 }
  ],
  "message": "تم بنجاح"
}
```

Use `id` as `time_id` when booking.

---

## POST `/api/book_a_service`

User token. The account and the car must both be verified.

```json
{
  "services": [13],
  "time_id": 12,
  "user_car": 9,
  "branch_id": 4,
  "date": "2026-10-20",
  "slot_index": 0,
  "customer_note": "Please call when ready",
  "service_item_selections": [{ "service_id": 13, "item_ids": [3, 5] }]
}
```

`slot_index` is `0`, `1`, or `2`.

`200` `data` is the booking:

```json
{
  "id": 2,
  "user_car": 9,
  "branch": 4,
  "time": 12,
  "date": "2026-10-20",
  "slot_index": 0,
  "customer_note": "Please call when ready",
  "service_item_selections": [{ "service_id": 13, "item_ids": [3, 5] }],
  "workflow_status": "pending_confirmation",
  "status": false
}
```

Unverified account is `403`:

```json
{ "status": false, "error": "Your account is pending verification. Please wait for admin approval." }
```

A taken slot is `400`: `{ "error": "This time slot is already reserved" }`

## GET `/api/my_service_bookings`

User token.

`200`:

```json
{
  "status": true,
  "data": [
    {
      "id": 2,
      "date": "2026-10-20",
      "time_display": "09:00",
      "branch_name": "Katameya",
      "workflow_status": "pending_confirmation",
      "slot_index": 0,
      "customer_note": "",
      "services": [{ "id": 13, "name": "10k, 50K", "name_ar": "" }],
      "car_model": "XC90",
      "car_plate": "ABC123"
    }
  ],
  "message": "تم بنجاح"
}
```

## GET `/api/my_history`

User token. `200` `data` is an array of history rows. Each row includes `price`, `date`, `using_points`, `service` (service objects), and `points`.

## POST `/api/book_used_cars`

User token. Body: `{ "used_cars": 1, "date": "2026-10-20" }`

`200` `data`: `{ "id": 1, "user": 4, "used_cars": 1, "date": "2026-10-20" }`

## POST `/api/book_accessories`

User token. Body: `{ "accessories": 1, "branch": 4, "date": "2026-10-20" }`

`200` `data`: `{ "id": 1, "user": 4, "accessories": 1, "branch": 4, "date": "2026-10-20" }`

## POST `/api/feedback`

No token.

```json
{
  "fullname": "Sara Ali",
  "email": "sara@example.com",
  "phone_number": "+201000000000",
  "feedback_subject": "Service",
  "car_model": 1,
  "feedback_details": "Great visit"
}
```

`200` `data` is the saved row, including `"id"`.

## POST `/api/contact_us`

No token.

```json
{
  "fullname": "Sara Ali",
  "email": "sara@example.com",
  "phone_number": "+201000000000",
  "car_model": 1,
  "inquiry_details": "Do you service XC90?"
}
```

`200` `data` is the saved row, including `"id"`.

## POST `/api/create_technical_assistant`

User token. Body: `{ "question": "Which oil does my car use?" }`

`200` `data`: `{ "id": 1, "user": 4, "question": "Which oil does my car use?", "answer": null, "read": false }`

## GET `/api/list_technical_assistant`

User token. `200` `data` is an array of those question objects for the logged-in user.

## POST `/api/road_help`

User token.

```json
{ "car": 9, "latitude": "29.99", "langtiude": "31.49" }
```

The longitude key is spelled `langtiude`.

`200` `data`: `{ "id": 1, "user": 4, "car": 9, "latitude": "29.99", "langtiude": "31.49", "valid": false }`

## GET `/api/my_notifications`

User token.

`200`:

```json
{
  "status": true,
  "data": [
    {
      "id": 1,
      "kind": "admin_message",
      "title": "Message from Volvo",
      "body": "Your car is verified.",
      "booking_id": null,
      "read_at": null,
      "created_at": "2026-10-23T12:00:00Z"
    }
  ],
  "message": "تم بنجاح"
}
```

`kind` is `admin_message`, `booking_moved`, or `booking_status`.

## POST `/api/my_notifications/1/read`

User token. No body. `200` `data` is the same notification with `read_at` filled in.

---

## Admin API

Every call below needs the token from `POST /api/admin/login/`.

Lists are `GET`. Creating a row is `POST`. One row is `GET`, `PATCH`, or `DELETE` on the URL with the id. A successful list or save is `{ "status": true, "data": ..., "message": "تم بنجاح" }`. `DELETE` returns `204` with an empty body.

### GET `/api/admin/users/`

Optional query: `?q=2010` searches mobile, email, and name.

`200` `data` item:

```json
{
  "id": 4,
  "first_name": "Sara",
  "last_name": "Ali",
  "email": "sara@example.com",
  "mobile": "+201000000000",
  "is_verified": false,
  "is_active": true,
  "mypoints": 20,
  "history_points": 20,
  "next_service_km": 10000,
  "next_service_date": "2026-11-01",
  "user_type": 1,
  "loyalty_type": "silver",
  "loyalty_id": 1,
  "is_staff": false,
  "is_superuser": false,
  "date_joined": "2026-10-01T10:00:00Z"
}
```

### POST `/api/admin/users/create/`

```json
{
  "mobile": "+201000000099",
  "email": "new@example.com",
  "first_name": "New",
  "last_name": "User",
  "password": "your-password",
  "is_staff": false
}
```

`201` `data` is the user object above. `password` is at least 8 characters and is not returned.

### PATCH `/api/admin/users/4/`

```json
{ "is_verified": true, "mypoints": 100, "user_type": 2 }
```

`200` `data` is the updated user. This is how staff lets a customer book.

### DELETE `/api/admin/users/4/`

`204` empty body.

### GET `/api/admin/bookings/`

Optional query: `workflow_status`, `user_id`, `date_from`, `date_to`, `phone`.

`workflow_status` is `pending_confirmation`, `confirmed`, `in_progress`, `completed`, or `cancelled`.

`200` `data` item:

```json
{
  "id": 2,
  "user_mobile": "+201000000000",
  "user_name": "Sara Ali",
  "branch_id": 4,
  "branch_name": "Katameya",
  "time_id": 12,
  "time_display": "09:00",
  "date": "2026-10-20",
  "status": false,
  "slot_index": 0,
  "customer_note": "",
  "workflow_status": "pending_confirmation",
  "services": [{ "id": 13, "name": "10k, 50K" }],
  "car_model": "XC90",
  "car_plate": "ABC123",
  "car_vin": "YV1XXXXXXXXXXXXXX"
}
```

### POST `/api/admin/bookings/create/`

```json
{
  "services": [13],
  "user_car": 9,
  "branch_id": 4,
  "time_id": 12,
  "date": "2026-10-20",
  "slot_index": 0
}
```

`201` `data` is the booking object above. This path does not require the customer to be verified.

### PATCH `/api/admin/bookings/2/`

```json
{ "workflow_status": "confirmed" }
```

`200` `data` is the updated booking.

### GET `/api/admin/user_cars/`

Optional query: `?user_id=4`

`200` `data` item:

```json
{
  "id": 9,
  "user": 4,
  "car_model": 1,
  "car_model_name": "XC90",
  "model_year": 2022,
  "plate_number": "ABC123",
  "chassis_number": "YV1XXXXXXXXXXXXXX",
  "is_verified": false,
  "allow_user_edit": false,
  "car_document_front_url": "https://example.com/front.jpg",
  "car_document_back_url": "https://example.com/back.jpg",
  "can_verify": true
}
```

### PATCH `/api/admin/user_cars/9/`

```json
{ "is_verified": true, "allow_user_edit": false }
```

`200` `data` is the car. Verification fails with `400` if both document sides are missing.

### POST `/api/admin/user_cars/9/notify/`

```json
{ "title": "Volvo", "body": "Your car is verified." }
```

`200`: `{ "status": true, "data": { "sent": true }, "message": "تم بنجاح" }`

### GET `/api/admin/loyalty_levels/`

`200` `data`: `[{ "id": 1, "type": "silver", "point": 0, "point_per_pound": 10 }]`

### PATCH `/api/admin/loyalty_levels/1/`

```json
{ "point": 0, "point_per_pound": 10 }
```

`200` `data` is the updated tier. `DELETE /api/admin/loyalty_levels/1/` returns `204`.

### GET `/api/admin/branches/` and POST `/api/admin/branches/`

Create body:

```json
{
  "name": "Katameya",
  "address": "New Cairo",
  "description": "",
  "mobile1": 221298882,
  "maps_url": "https://maps.app.goo.gl/example"
}
```

`200` list or `201` create. `data` is one branch or an array, same fields as `GET /api/list_branches`.

`PATCH /api/admin/branches/4/` updates those fields. `DELETE` returns `204`.

### GET `/api/admin/car_models/` and POST `/api/admin/car_models/`

Create body:

```json
{
  "car_model": "XC90",
  "year_from": 2022,
  "year_to": 2025,
  "model_type": "SUV",
  "details": "",
  "sort_order": 0,
  "image_url": "https://example.com/xc90.png"
}
```

`200` / `201` `data` matches `GET /api/list_car_model`. `PATCH` and `DELETE` use `/api/admin/car_models/1/`.

### POST `/api/admin/car_models/reorder/`

```json
{ "order": [3, 1, 2] }
```

`200`: `{ "status": true, "data": { "reordered": 3 }, "message": "تم بنجاح" }`

The app then shows models in that order.

### GET and POST `/api/admin/service_categories/`

```json
{ "name": "Regular Maintenance", "name_ar": "صيانة دورية", "sort_order": 0, "icon_url": null }
```

`200` `data` item adds `"id"` and `"service_count"`. One row: `/api/admin/service_categories/1/`.

### GET and POST `/api/admin/service_items/`

```json
{ "name": "Engine Oil 0W20", "name_ar": "زيت محرك 0W20", "description": "", "price": null }
```

`200` `data` item adds `"id"` and `"service_count"`. One row: `/api/admin/service_items/3/`.

### GET and POST `/api/admin/services/`

```json
{
  "name": "10k, 50K",
  "name_ar": "",
  "price": 2500,
  "points": 10,
  "category": 1,
  "only_at_branch": null,
  "source_maintenance": 2,
  "items": [3, 5],
  "compatible_with": [1, 2]
}
```

`200` `data` is the full service, including `items_detail` and `compatible_with_models`, same as `GET /api/list_services`. One row: `/api/admin/services/13/`.

Saving a maintenance schedule also creates or updates the matching service, so you usually edit the schedule instead of this row.

### GET and POST `/api/admin/accessories/`

```json
{
  "title": "Floor mats",
  "about": "",
  "price": 3500,
  "discount": 0,
  "kind": "accessory",
  "image_url": "https://example.com/mats.jpg",
  "gallery_urls": ["https://example.com/mats.jpg"],
  "video_url": null,
  "compatible_with": [1]
}
```

`kind` is `accessory` or `special_offer`. One row: `/api/admin/accessories/1/`.

### GET and POST `/api/admin/maintenance_schedule_types/`

```json
{ "name": "10k", "name_ar": "", "sort_order": 2 }
```

`200` `data` item: `{ "id": 3, "name": "10k", "name_ar": "", "sort_order": 2 }`

One row: `/api/admin/maintenance_schedule_types/3/`.

### GET and POST `/api/admin/maintenance_schedules/`

```json
{
  "car_model": 1,
  "approximate_price": 4500,
  "maintenance_types": [3, 7],
  "compatible_car_models": [1, 2],
  "service_items": [3, 5]
}
```

`201` `data` is the same object returned by `GET /api/maintenance_schedule` for that row, and a bookable service is created under Regular Maintenance. One row: `/api/admin/maintenance_schedules/2/`.

### GET and POST `/api/admin/home_banners/`

```json
{
  "label": "Offer",
  "text": "Winter service",
  "image_url": "https://example.com/banner.jpg",
  "sort_order": 0,
  "is_active": true
}
```

`200` `data` matches `GET /api/home_banners`, plus `is_active`. One row: `/api/admin/home_banners/1/`.

### GET `/api/admin/booking_open_days/?branch_id=4`

`200`:

```json
{
  "status": true,
  "data": [
    {
      "id": 8,
      "branch_id": 4,
      "branch_name": "Katameya",
      "date": "2026-10-20",
      "enabled_hours": [9, 10, 11, 12],
      "enabled_time_ids": [12, 13, 14, 15],
      "slots_label": "09:00, 10:00, 11:00, 12:00"
    }
  ],
  "message": "تم بنجاح"
}
```

### POST `/api/admin/booking_open_days/bulk/`

```json
{
  "branch_id": 4,
  "date_from": "2026-10-20",
  "date_to": "2026-10-24",
  "skip_fridays": true,
  "hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
}
```

`200`:

```json
{
  "status": true,
  "data": {
    "created": 4,
    "skipped": 1,
    "branch_id": 4,
    "date_from": "2026-10-20",
    "date_to": "2026-10-24",
    "hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
  },
  "message": "تم بنجاح"
}
```

`DELETE` on the same URL removes that range. Body: `branch_id`, `date_from`, `date_to`.

### PATCH `/api/admin/booking_open_days/8/`

```json
{ "hours": [9, 10, 11, 12] }
```

Hours are integers from 9 through 18. `200` `data` is one open-day object.

### GET `/api/admin/site_contact/` and PATCH `/api/admin/site_contact/`

PATCH body:

```json
{
  "whatsapp_e164": "+201000000000",
  "tech_hotline_e164": "+201000000000",
  "winch_contacts": [{ "area": "Cairo", "phone": "+201000000001" }],
  "app_theme_default": "light",
  "user_can_change_theme": true,
  "new_user_default_points": 20,
  "home_carousel_heading": "OFFERS"
}
```

`200` `data` matches `GET /api/site_contact_settings`. `area` can also be sent as `name`.

---

`/admin/` is the HTML admin site. Sign in there with the user's mobile number, not this JSON API.
