from django.contrib import admin

from user.models import CarModels, LoyaltyPoints, User, UserCars, UserRequests


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "mobile", "email", "first_name", "last_name", "is_verified", "is_staff")
    list_filter = ("is_verified", "is_staff", "is_superuser")
    search_fields = ("mobile", "first_name", "last_name", "email")
    ordering = ("-id",)


admin.site.register(UserCars)
admin.site.register(CarModels)
admin.site.register(LoyaltyPoints)
admin.site.register(UserRequests)
