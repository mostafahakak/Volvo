from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin, ImportExportModelAdmin

from app.models import *


class YourModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Filter the queryset based on the user's branch
            qs = qs.filter(branch=request.user.branch)
        return qs


class VideoResource(resources.ModelResource):
    class Meta:
        model = TechnicalAssistant
        fields = (
            "user",
            "question",
            "answer",
            "read"
        )


class CustomAssistantAdmin(
    ImportExportModelAdmin, ImportExportActionModelAdmin
):
    resource_class = VideoResource
    # form = UserChangeForm

    list_display = ["user",
                    "question",
                    "answer",
                    "read"
                    ]
    list_filter = ["read"]
    # fieldsets = (
    #     (None, {"fields": ("username", "password")}),
    #     (
    #         "Personal info",
    #         {
    #             "fields": (
    #                 "first_name",
    #                 "last_name",
    #                 "username",
    #                 "email",
    #                 "avatar",
    #             )
    #         },
    #     ),
    #     (
    #         "Permissions",
    #         {
    #             "fields": (
    #                 "is_active",
    #                 "is_staff",
    #                 "is_superuser",
    #                 "groups",
    #             ),
    #         },
    #     ),
    #     ("Important dates", {"fields": ("last_login", "date_joined")}),
    # )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user",
                           "question",
                           "answer",
                           "read"),
            },
        ),
    )
    # autocomplete_fields = ["type"]
    # search_fields = ["title"]
    list_per_page = 20


# Register your models here.
admin.site.register(Branches, YourModelAdmin)
admin.site.register(BranchSlot, YourModelAdmin)
admin.site.register(Timing, YourModelAdmin)
admin.site.register(Booking, YourModelAdmin)
admin.site.register(Services)
admin.site.register(Accessories)
admin.site.register(RoadAssistantRequest)
admin.site.register(UsedCar, YourModelAdmin)
admin.site.register(UsedCarsImage)
admin.site.register(MaintenanceSchedule)
admin.site.register(MyHistory)
admin.site.register(Notes)
admin.site.register(BookUsedCars, YourModelAdmin)
admin.site.register(BookAccessories, YourModelAdmin)
admin.site.register(AboutUS)
admin.site.register(FeedBack)
admin.site.register(ContactUS)
admin.site.register(TechnicalAssistant, CustomAssistantAdmin)
admin.site.register(SiteContactSettings)
