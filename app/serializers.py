from rest_framework import serializers

from app.models import MaintenanceSchedule, MyHistory, Branches, BranchSlot, Services, ServiceCategory, \
    ServiceItem, Accessories, UsedCar, UsedCarsImage, BookUsedCars, BookAccessories, AboutUS, FeedBack, ContactUS, \
    Timing, Booking, TechnicalAssistant, RoadAssistantRequest, SiteContactSettings
from user.models import CarModels, UserCars


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "icon", "sort_order")


class ServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceItem
        fields = ("id", "name", "description")


class ServicesSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    branch_name = serializers.CharField(source="only_at_branch.name", read_only=True, allow_null=True)
    compatible_with_models = serializers.SerializerMethodField()
    items_detail = serializers.SerializerMethodField()

    class Meta:
        model = Services
        fields = "__all__"

    def get_compatible_with_models(self, obj):
        return [{"id": c.id, "car_model": c.car_model} for c in obj.compatible_with.all()]

    def get_items_detail(self, obj):
        return [
            {"id": i.id, "name": i.name, "description": i.description}
            for i in obj.items.all()
        ]


class BookingHistorySerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    time_display = serializers.TimeField(source="time.time", format="%H:%M", read_only=True)
    services = serializers.SerializerMethodField()
    car_model = serializers.CharField(source="user_car.car_model.car_model", read_only=True)
    car_plate = serializers.CharField(source="user_car.plate_number", read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "date",
            "time_display",
            "branch_name",
            "workflow_status",
            "slot_index",
            "customer_note",
            "services",
            "car_model",
            "car_plate",
            "created_at",
        )

    def get_services(self, obj):
        return [{"id": s.id, "name": s.name} for s in obj.service.all()]


class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModels
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and getattr(instance, "image", None) and instance.image:
            try:
                data["image"] = request.build_absolute_uri(instance.image.url)
            except Exception:
                pass
        return data


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    car_model_name = serializers.CharField(source="car_model.car_model", read_only=True, allow_null=True)

    class Meta:
        model = MaintenanceSchedule
        fields = "__all__"


class MyHistorySerializer(serializers.ModelSerializer):
    service = ServicesSerializer(required=False, many=True)

    class Meta:
        model = MyHistory
        fields = "__all__"


class UserCarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCars
        fields = "__all__"


class BranchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branches
        fields = "__all__"


class BranchSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchSlot
        fields = "__all__"


class TimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timing
        fields = "__all__"


class AccessoriesSerializer(serializers.ModelSerializer):
    compatible_with = CarModelSerializer(required=False, many=True)

    class Meta:
        model = Accessories
        fields = "__all__"


class UsedCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedCar
        fields = "__all__"


class UsedCarsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedCarsImage
        fields = "__all__"


class BookUsedCarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookUsedCars
        fields = "__all__"


class BookAccessoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookAccessories
        fields = "__all__"


class AboutUsSerializers(serializers.ModelSerializer):
    class Meta:
        model = AboutUS
        fields = "__all__"


class FeedBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = "__all__"


class ContactUSSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUS
        fields = "__all__"


class BookAServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"


class TechnicalAssistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalAssistant
        fields = "__all__"


class RoadAssistantRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadAssistantRequest
        fields = "__all__"


class SiteContactSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteContactSettings
        fields = (
            "id",
            "whatsapp_e164",
            "tech_hotline_e164",
            "winch_primary",
            "winch_secondary",
            "app_theme_default",
            "user_can_change_theme",
            "new_user_default_points",
            "updated_at",
        )
