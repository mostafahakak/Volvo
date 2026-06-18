import uuid

from rest_framework import serializers

from volvo.firebase_storage import FirebaseUploadError, upload_catalog_file

from app.models import MaintenanceSchedule, MaintenanceScheduleType, MyHistory, Branches, BranchSlot, Services, ServiceCategory, \
    ServiceItem, Accessories, UsedCar, UsedCarsImage, BookUsedCars, BookAccessories, AboutUS, FeedBack, ContactUS, \
    Timing, Booking, TechnicalAssistant, RoadAssistantRequest, SiteContactSettings, HomeBanner
from user.models import CarModels, UserCars, UserNotification


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "name_ar", "icon", "icon_url", "sort_order")

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
        fields = ("id", "name", "name_ar", "description", "price")


class ServicesSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    category_name_ar = serializers.CharField(source="category.name_ar", read_only=True, allow_null=True)
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
                "name_ar": getattr(i, "name_ar", "") or "",
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
        return [
            {"id": s.id, "name": s.name, "name_ar": getattr(s, "name_ar", None) or ""}
            for s in obj.service.all()
        ]


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


class MaintenanceScheduleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceScheduleType
        fields = ("id", "name", "name_ar", "sort_order")


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    car_model_name = serializers.CharField(source="car_model.car_model", read_only=True, allow_null=True)
    compatible_car_models = serializers.PrimaryKeyRelatedField(
        queryset=CarModels.objects.all(), many=True, required=False
    )
    service_items = serializers.PrimaryKeyRelatedField(
        queryset=ServiceItem.objects.all(), many=True, required=False
    )
    maintenance_types = serializers.PrimaryKeyRelatedField(
        queryset=MaintenanceScheduleType.objects.all(), many=True, required=False
    )
    maintenance_type = serializers.SerializerMethodField()
    maintenance_type_name = serializers.SerializerMethodField()
    maintenance_type_name_ar = serializers.SerializerMethodField()
    maintenance_types_detail = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceSchedule
        fields = "__all__"

    def _ordered_types(self, instance):
        return list(instance.maintenance_types.all().order_by("sort_order", "id"))

    def get_maintenance_type(self, instance):
        types = self._ordered_types(instance)
        return types[0].id if types else None

    def get_maintenance_type_name(self, instance):
        types = self._ordered_types(instance)
        if not types:
            return None
        return ", ".join(t.name for t in types)

    def get_maintenance_type_name_ar(self, instance):
        types = self._ordered_types(instance)
        names = [(t.name_ar or "").strip() for t in types if (t.name_ar or "").strip()]
        return ", ".join(names) if names else ""

    def get_maintenance_types_detail(self, instance):
        return [
            {"id": t.id, "name": t.name, "name_ar": (t.name_ar or "") or ""}
            for t in self._ordered_types(instance)
        ]

    def validate(self, attrs):
        types = attrs.get("maintenance_types")
        if types is not None and len(types) == 0:
            raise serializers.ValidationError(
                {"maintenance_types": "Select at least one maintenance type."}
            )
        if self.instance is None and not types:
            raise serializers.ValidationError(
                {"maintenance_types": "Select at least one maintenance type."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("description", None)
        compatible = validated_data.pop("compatible_car_models", None)
        items = validated_data.pop("service_items", None)
        types = validated_data.pop("maintenance_types", None)
        instance = super().create(validated_data)
        if compatible is not None:
            instance.compatible_car_models.set(compatible)
        if items is not None:
            instance.service_items.set(items)
        if types is not None:
            instance.maintenance_types.set(types)
        return instance

    def update(self, instance, validated_data):
        validated_data.pop("description", None)
        compatible = validated_data.pop("compatible_car_models", None)
        items = validated_data.pop("service_items", None)
        types = validated_data.pop("maintenance_types", None)
        instance = super().update(instance, validated_data)
        if compatible is not None:
            instance.compatible_car_models.set(compatible)
        if items is not None:
            instance.service_items.set(items)
        if types is not None:
            instance.maintenance_types.set(types)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["description"] = None
        data["maintenance_type_ids"] = list(
            instance.maintenance_types.values_list("id", flat=True)
        )
        data["compatible_car_model_ids"] = list(
            instance.compatible_car_models.values_list("id", flat=True)
        )
        data["compatible_car_models_detail"] = [
            {"id": c.id, "car_model": c.car_model} for c in instance.compatible_car_models.all()
        ]
        data["service_items_detail"] = [
            {
                "id": si.id,
                "name": si.name,
                "name_ar": (getattr(si, "name_ar", None) or "") or "",
                "price": si.price,
            }
            for si in instance.service_items.all().order_by("name")
        ]
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
    def _normalized_winch_contacts(self, raw):
        out = []
        if isinstance(raw, list):
            for row in raw:
                if not isinstance(row, dict):
                    continue
                name = (row.get("name") or "").strip()
                phone = (row.get("phone_e164") or row.get("phone") or "").strip()
                if phone:
                    out.append({"name": name, "phone_e164": phone})
        return out

    def validate(self, attrs):
        contacts = attrs.get("winch_contacts", serializers.empty)
        if contacts is not serializers.empty:
            attrs["winch_contacts"] = self._normalized_winch_contacts(contacts)
            rows = attrs["winch_contacts"]
            attrs["winch_primary"] = rows[0]["phone_e164"] if len(rows) > 0 else ""
            attrs["winch_secondary"] = rows[1]["phone_e164"] if len(rows) > 1 else ""
            return attrs

        legacy_touched = "winch_primary" in attrs or "winch_secondary" in attrs
        if legacy_touched:
            p1 = (attrs.get("winch_primary", getattr(self.instance, "winch_primary", "")) or "").strip()
            p2 = (attrs.get("winch_secondary", getattr(self.instance, "winch_secondary", "")) or "").strip()
            rows = []
            if p1:
                rows.append({"name": "Line 1", "phone_e164": p1})
            if p2:
                rows.append({"name": "Line 2", "phone_e164": p2})
            attrs["winch_contacts"] = rows
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        rows = self._normalized_winch_contacts(data.get("winch_contacts"))
        if not rows:
            p1 = (data.get("winch_primary") or "").strip()
            p2 = (data.get("winch_secondary") or "").strip()
            if p1:
                rows.append({"name": "Line 1", "phone_e164": p1})
            if p2:
                rows.append({"name": "Line 2", "phone_e164": p2})
        data["winch_contacts"] = rows
        return data

    class Meta:
        model = SiteContactSettings
        fields = (
            "id",
            "whatsapp_e164",
            "tech_hotline_e164",
            "winch_primary",
            "winch_secondary",
            "winch_contacts",
            "app_theme_default",
            "user_can_change_theme",
            "new_user_default_points",
            "home_carousel_heading",
            "updated_at",
        )
