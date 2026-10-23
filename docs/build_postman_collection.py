"""Build docs/Volvo-API.postman_collection.json. Not required at runtime."""
import json
from pathlib import Path

items = []


def request(name, method, path, auth=None, body=None, query=None, description=""):
    url = {
        "raw": "{{baseUrl}}" + path,
        "host": ["{{baseUrl}}"],
        "path": [p for p in path.split("/") if p],
    }
    if query:
        url["query"] = [{"key": k, "value": v} for k, v in query]
        url["raw"] += "?" + "&".join(f"{k}={v}" for k, v in query)
    req = {
        "name": name,
        "request": {
            "method": method,
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": url,
            "description": description,
        },
    }
    if auth == "user":
        req["request"]["auth"] = {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{accessToken}}", "type": "string"}],
        }
    elif auth == "admin":
        req["request"]["auth"] = {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{adminToken}}", "type": "string"}],
        }
    if body is not None:
        req["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, indent=2),
            "options": {"raw": {"language": "json"}},
        }
    if name == "Login":
        req["event"] = [{
            "listen": "test",
            "script": {
                "type": "text/javascript",
                "exec": [
                    "const json = pm.response.json();",
                    "if (json.access) pm.collectionVariables.set('accessToken', json.access);",
                ],
            },
        }]
    if name == "Admin login":
        req["event"] = [{
            "listen": "test",
            "script": {
                "type": "text/javascript",
                "exec": [
                    "const json = pm.response.json();",
                    "if (json.access) pm.collectionVariables.set('adminToken', json.access);",
                ],
            },
        }]
    return req


def folder(name, requests, description=""):
    return {"name": name, "description": description, "item": requests}


collection = {
    "info": {
        "name": "Volvo API",
        "description": "Mobile app and admin dashboard API. Set baseUrl, then run Login or Admin login. Tokens are saved automatically.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "variable": [
        {"key": "baseUrl", "value": "https://volvo-bd1q.onrender.com"},
        {"key": "accessToken", "value": ""},
        {"key": "adminToken", "value": ""},
    ],
    "item": [
        folder("Auth", [
            request("Sign up", "POST", "/api/signup", body={
                "mobile": "+201000000000", "email": "user@example.com",
                "password": "your-password", "password2": "your-password",
                "first_name": "First", "last_name": "Last",
            }, description="Creates an unverified user. Login still works. Booking stays blocked until staff sets is_verified."),
            request("Login", "POST", "/api/login", body={"mobile": "+201000000000", "password": "your-password"},
                    description="Returns access, refresh, and user_data. Saves access into {{accessToken}}."),
            request("Check mobile", "GET", "/api/check_mobile", query=[("mobile", "+201000000000")]),
            request("Firebase phone login", "POST", "/api/firebase_login", body={
                "id_token": "FIREBASE_ID_TOKEN", "mobile": "+201000000000",
                "first_name": "First", "last_name": "Last", "email": "user@example.com",
            }),
            request("Social auth check", "POST", "/api/social_auth_check", body={"id_token": "FIREBASE_ID_TOKEN"}),
            request("Profile", "GET", "/api/profile", auth="user"),
            request("Update profile", "POST", "/api/update_profile", auth="user", body={
                "email": "user@example.com", "mobile": "+201000000000",
                "first_name": "First", "last_name": "Last",
            }),
            request("Change password", "POST", "/api/change_password", auth="user", body={
                "old_password": "your-password", "new_password": "new-password", "conf_password": "new-password",
            }),
            request("Save notification token", "POST", "/api/notification_token", auth="user", body={"fcm_token": "DEVICE_FCM_TOKEN"}),
            request("Delete account", "POST", "/api/delete_account", auth="user"),
            request("Admin login", "POST", "/api/admin/login/", body={"email": "staff@example.com", "password": "your-password"},
                    description="Staff JWT. Saves access into {{adminToken}}."),
        ]),
        folder("Cars and loyalty", [
            request("List car models", "GET", "/api/list_car_model"),
            request("Add my car", "POST", "/api/add_user_car", auth="user", body={
                "car_model": 1, "model_year": 2022, "chassis_number": "VIN", "plate_number": "ABC123",
            }),
            request("List my cars", "GET", "/api/list_user_cars", auth="user"),
            request("Update my car", "PATCH", "/api/user_car/1", auth="user", body={"plate_number": "ABC123"}),
            request("Delete my car", "DELETE", "/api/user_car/1", auth="user"),
            request("Loyalty levels", "GET", "/api/loyalty_level", auth="user"),
            request("Redeem points", "POST", "/api/redeem_points", auth="user", body={"service_id": 1, "price": 1000}),
        ]),
        folder("Catalog", [
            request("Home banners", "GET", "/api/home_banners"),
            request("Maintenance types", "GET", "/api/maintenance_schedule_types"),
            request("Maintenance schedules", "GET", "/api/maintenance_schedule", query=[("car_model_id", "1"), ("maintenance_type_id", "1")]),
            request("Branches", "GET", "/api/list_branches"),
            request("Branch slots", "GET", "/api/list_branches_slot", auth="user"),
            request("Service categories", "GET", "/api/list_service_categories"),
            request("Services", "GET", "/api/list_services", auth="user", query=[("category_id", "1"), ("car_model_id", "1")]),
            request("Service items", "GET", "/api/list_service_items", auth="user", query=[("service_id", "1")]),
            request("Accessories", "GET", "/api/list_accessories"),
            request("Offers", "GET", "/api/list_offers", auth="user"),
            request("Used cars", "GET", "/api/list_used_cars", auth="user"),
            request("About us", "GET", "/api/list_aboutus"),
            request("Site contact", "GET", "/api/site_contact_settings"),
            request("Available times", "GET", "/api/list_available_times", auth="user", query=[("branch_id", "1"), ("date", "2026-10-20")]),
        ]),
        folder("Bookings and support", [
            request("Book a service", "POST", "/api/book_a_service", auth="user", body={
                "services": [1], "time_id": 1, "user_car": 1, "branch_id": 1,
                "date": "2026-10-20", "slot_index": 0, "customer_note": "",
                "service_item_selections": [{"service_id": 1, "item_ids": [1]}],
            }),
            request("My service bookings", "GET", "/api/my_service_bookings", auth="user"),
            request("My history", "GET", "/api/my_history", auth="user"),
            request("Book used car", "POST", "/api/book_used_cars", auth="user", body={"used_cars": 1, "date": "2026-10-20"}),
            request("Book accessories", "POST", "/api/book_accessories", auth="user", body={"accessories": 1, "branch": 1, "date": "2026-10-20"}),
            request("Feedback", "POST", "/api/feedback", body={
                "fullname": "Name", "email": "user@example.com", "phone_number": "+201000000000",
                "feedback_subject": "Service", "car_model": 1, "feedback_details": "Details",
            }),
            request("Contact us", "POST", "/api/contact_us", body={
                "fullname": "Name", "email": "user@example.com", "phone_number": "+201000000000",
                "car_model": 1, "inquiry_details": "Question",
            }),
            request("Ask technical assistant", "POST", "/api/create_technical_assistant", auth="user", body={"question": "How do I book?"}),
            request("My technical assistant threads", "GET", "/api/list_technical_assistant", auth="user"),
            request("Road help", "POST", "/api/road_help", auth="user", body={"car": 1, "latitude": "30.0", "langtiude": "31.0"}),
            request("My notifications", "GET", "/api/my_notifications", auth="user"),
            request("Mark notification read", "POST", "/api/my_notifications/1/read", auth="user"),
        ]),
        folder("Admin", [
            request("List users", "GET", "/api/admin/users/", auth="admin"),
            request("Create user", "POST", "/api/admin/users/create/", auth="admin", body={
                "mobile": "+201000000002", "email": "new@example.com", "first_name": "New",
                "last_name": "User", "password": "your-password", "is_staff": False,
            }),
            request("Get or update user", "PATCH", "/api/admin/users/1/", auth="admin", body={"is_verified": True}),
            request("Delete user", "DELETE", "/api/admin/users/1/", auth="admin"),
            request("List bookings", "GET", "/api/admin/bookings/", auth="admin", query=[("workflow_status", "pending_confirmation")]),
            request("Create booking", "POST", "/api/admin/bookings/create/", auth="admin", body={
                "services": [1], "user_car": 1, "branch_id": 1, "time_id": 1, "date": "2026-10-20", "slot_index": 0,
            }),
            request("Update booking", "PATCH", "/api/admin/bookings/1/", auth="admin", body={"workflow_status": "confirmed"}),
            request("List user cars", "GET", "/api/admin/user_cars/", auth="admin"),
            request("Update user car", "PATCH", "/api/admin/user_cars/1/", auth="admin", body={"is_verified": True}),
            request("Notify car owner", "POST", "/api/admin/user_cars/1/notify/", auth="admin", body={"title": "Hello", "body": "Your car is verified."}),
            request("Loyalty levels", "GET", "/api/admin/loyalty_levels/", auth="admin"),
            request("Update loyalty level", "PATCH", "/api/admin/loyalty_levels/1/", auth="admin", body={"point": 100, "point_per_pound": 10}),
            request("Branches", "GET", "/api/admin/branches/", auth="admin"),
            request("Create branch", "POST", "/api/admin/branches/", auth="admin", body={
                "name": "Branch", "address": "Address", "maps_url": "https://maps.app.goo.gl/example",
            }),
            request("Update branch", "PATCH", "/api/admin/branches/1/", auth="admin", body={"description": "Hours and notes"}),
            request("Car models", "GET", "/api/admin/car_models/", auth="admin"),
            request("Reorder car models", "POST", "/api/admin/car_models/reorder/", auth="admin", body={"order": [1, 2, 3]}),
            request("Service categories", "GET", "/api/admin/service_categories/", auth="admin"),
            request("Service items", "GET", "/api/admin/service_items/", auth="admin"),
            request("Services", "GET", "/api/admin/services/", auth="admin"),
            request("Accessories", "GET", "/api/admin/accessories/", auth="admin"),
            request("Maintenance types", "GET", "/api/admin/maintenance_schedule_types/", auth="admin"),
            request("Maintenance schedules", "GET", "/api/admin/maintenance_schedules/", auth="admin"),
            request("Home banners", "GET", "/api/admin/home_banners/", auth="admin"),
            request("Open booking days", "GET", "/api/admin/booking_open_days/", auth="admin", query=[("branch_id", "1")]),
            request("Bulk open days", "POST", "/api/admin/booking_open_days/bulk/", auth="admin", body={
                "branch_id": 1, "date_from": "2026-10-20", "date_to": "2026-10-24",
                "skip_fridays": True, "hours": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            }),
            request("Update one open day", "PATCH", "/api/admin/booking_open_days/1/", auth="admin", body={"hours": [9, 10, 11, 12]}),
            request("Site contact", "GET", "/api/admin/site_contact/", auth="admin"),
            request("Update site contact", "PATCH", "/api/admin/site_contact/", auth="admin", body={
                "whatsapp_e164": "+201000000000",
                "tech_hotline_e164": "+201000000000",
                "winch_contacts": [{"area": "Cairo", "phone": "+201000000000"}],
                "home_carousel_heading": "OFFERS",
            }),
        ]),
    ],
}

out = Path(__file__).with_name("Volvo-API.postman_collection.json")
out.write_text(json.dumps(collection, indent=2), encoding="utf-8")
print(out, "requests", sum(len(f["item"]) for f in collection["item"]))
