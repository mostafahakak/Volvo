import uuid

from rest_framework import serializers

from volvo.firebase_storage import FirebaseUploadError, upload_catalog_file

from app.models import MaintenanceSchedule, MyHistory, Branches, BranchSlot, Services, ServiceCategory, \
    ServiceItem, Accessories, UsedCar, UsedCarsImage, BookUsedCars, BookAccessories, AboutUS, FeedBack, ContactUS, \
    Timing, Booking, TechnicalAssistant, RoadAssistantRequest, SiteContactSettings, HomeBanner
from user.models import CarModels, UserCars, UserNotification


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "icon", "icon_url", "sort_order")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        url = (instance.icon_url or "").strip()
        if url:
            data["icon"] = url
        else:
            request = self.context.get("request")
            if request and instance.icon and getattr(instance.icon, "name", None):
                try:
                    data["icon"] = request.build_absolute_uri(instance.icon.url)
                except Exception:
                    pass
        return data


class ServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceItem
        fields = ("id", "name", "description", "price")


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
            {
                "id": i.id,
                "name": i.name,
                "description": i.description,
                "price": i.price,
            }
            for i in obj.items.all()
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        url = (instance.icons_url or "").strip()
        if url:
            data["icons"] = url
        else:
            request = self.context.get("request")
            if request and instance.icons and getattr(instance.icons, "name", None):
                try:
                    data["icons"] = request.build_absolute_uri(instance.icons.url)
                except Exception:
                    pass
        return data


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
            "service_item_selections",
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

    def create(self, validated_data):
        image = validated_data.pop("image", None)
        instance = super().create(validated_data)
        if image:
            try:
                instance.image_url = upload_catalog_file(
                    image, f"catalog/car_models/{instance.pk}/{uuid.uuid4().hex}"
                )
            except FirebaseUploadError as e:
                raise serializers.ValidationError({"image": str(e)})
            instance.save(update_fields=["image_url"])
        return instance

    def update(self, instance, validated_data):
        image = validated_data.pop("image", None)
        instance = super().update(instance, validated_data)
        if image:
            try:
                instance.image_url = upload_catalog_file(
                    image, f"catalog/car_models/{instance.pk}/{uuid.uuid4().hex}"
                )
            except FirebaseUploadError as e:
                raise serializers.ValidationError({"image": str(e)})
            instance.save(update_fields=["image_url"])
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        url = (instance.image_url or "").strip()
        if url:
            data["image"] = url
            return data
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

    def create(self, validated_data):
        description = validated_data.pop("description", None)
        instance = super().create(validated_data)
        if description:
            try:
                instance.description_url = upload_catalog_file(
                    description,
                    f"catalog/maintenance_schedules/{instance.pk}/{uuid.uuid4().hex}",
                )
            except FirebaseUploadError as e:
                raise serializers.ValidationError({"description": str(e)})
            instance.save(update_fields=["description_url"])
        return instance

    def update(self, instance, validated_data):
        description = validated_data.pop("description", None)
        instance = super().update(instance, validated_data)
        if description:
            try:
                instance.description_url = upload_catalog_file(
                    description,
                    f"catalog/maintenance_schedules/{instance.pk}/{uuid.uuid4().hex}",
                )
            except FirebaseUploadError as e:
                raise serializers.ValidationError({"description": str(e)})
            instance.save(update_fields=["description_url"])
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        url = (instance.description_url or "").strip()
        if url:
            data["description"] = url
            return data
        request = self.context.get("request")
        if request and instance.description and getattr(instance.description, "name", None):
            try:
                data["description"] = request.build_absolute_uri(instance.description.url)
            except Exception:
                pass
        return data


class MyHistorySerializer(serializers.ModelSerializer):
    service = ServicesSerializer(required=False, many=True)

    class Meta:
        model = MyHistory
        fields = "__all__"


class UserCarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCars
        fields = "__all__"
        read_only_fields = ("is_verified", "allow_user_edit")


class UserNotificationSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source="booking_id", read_only=True, allow_null=True)

    class Meta:
        model = UserNotification
        fields = ("id", "kind", "title", "body", "booking_id", "read_at", "created_at")


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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        gallery = instance.resolved_gallery_urls()
        data["gallery"] = gallery
        data["image"] = gallery[0] if gallery else data.get("image")
        vu = (instance.video_url or "").strip()
        data["video_url"] = vu or None
        return data


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


class HomeBannerPublicSerializer(serializers.ModelSerializer):
    """Active home promo slides for the mobile app (ordered)."""

    class Meta:
        model = HomeBanner
        fields = ("id", "label", "text", "image", "sort_order")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        url = (instance.image_url or "").strip()
        if url:
            data["image"] = url
        else:
            request = self.context.get("request")
            if request and instance.image and getattr(instance.image, "name", None):
                try:
                    data["image"] = request.build_absolute_uri(instance.image.url)
                except Exception:
                    pass
        return data


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
            "home_carousel_heading",
            "updated_at",
        )
