from django.urls import path

from app.api import admin_views

urlpatterns = [
    path("login/", admin_views.AdminLoginView.as_view(), name="admin_login"),
    path("users/create/", admin_views.AdminUserCreateView.as_view(), name="admin_users_create"),
    path("users/", admin_views.AdminUserListView.as_view(), name="admin_users"),
    path("users/<int:pk>/", admin_views.AdminUserDetailView.as_view(), name="admin_user_detail"),
    path("bookings/create/", admin_views.AdminBookingCreateView.as_view(), name="admin_booking_create"),
    path("bookings/", admin_views.AdminBookingListView.as_view(), name="admin_bookings"),
    path("bookings/<int:pk>/", admin_views.AdminBookingDetailView.as_view(), name="admin_booking_detail"),
    path("loyalty_levels/", admin_views.AdminLoyaltyListView.as_view(), name="admin_loyalty"),
    path("branches/", admin_views.AdminBranchesListView.as_view(), name="admin_branches"),
    path("car_models/<int:pk>/", admin_views.AdminCarModelDetailView.as_view(), name="admin_car_model_detail"),
    path("car_models/", admin_views.AdminCarModelsListCreateView.as_view(), name="admin_car_models"),
    path("user_cars/", admin_views.AdminUserCarsListView.as_view(), name="admin_user_cars"),
    path("services/", admin_views.AdminServicesListCreateView.as_view(), name="admin_services"),
    path("services/<int:pk>/", admin_views.AdminServiceDetailView.as_view(), name="admin_service_detail"),
    path("accessories/", admin_views.AdminAccessoriesListCreateView.as_view(), name="admin_accessories"),
    path("accessories/<int:pk>/", admin_views.AdminAccessoryDetailView.as_view(), name="admin_accessory_detail"),
    path(
        "maintenance_schedules/",
        admin_views.AdminMaintenanceListCreateView.as_view(),
        name="admin_maintenance",
    ),
    path(
        "maintenance_schedules/<int:pk>/",
        admin_views.AdminMaintenanceDetailView.as_view(),
        name="admin_maintenance_detail",
    ),
    path("site_contact/", admin_views.AdminSiteContactView.as_view(), name="admin_site_contact"),
]
