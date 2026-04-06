from django.contrib import admin

from user.models import *

# class YourModelAdmin(admin.ModelAdmin):
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if not request.user.is_superuser:
#             # Filter the queryset based on the user's branch
#             qs = qs.filter(branch=request.user.branch)
#         return qs

# Register your models here.
admin.site.register(User)
admin.site.register(UserCars)
admin.site.register(CarModels)
admin.site.register(LoyaltyPoints)
admin.site.register(UserRequests)