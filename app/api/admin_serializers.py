from rest_framework import serializers

from app.models import (
    Accessories,
    Booking,
    MaintenanceSchedule,
    ServiceCategory,
    ServiceItem,
    Services,
    SiteContactSettings,
)
from user.models import Branches, CarModels, LoyaltyPoints, User, UserCars


class AdminUserSerializer(serializers.ModelSerializer):
    loyalty_type = serializers.CharField(source="user_type.type", read_only=True)
    loyalty_id = serializers.IntegerField(source="user_type_id", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "is_verified",
            "mypoints",
            "history_points",
            "next_service_km",
            "next_service_date",
            "user_type",
            "loyalty_type",
            "loyalty_id",
            "date_joined",
            "is_staff",
            "is_superuser",
        )
        read_only_fields = ("date_joined", "is_staff", "is_superuser")


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    next_service_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "is_verified",
            "user_type",
            "next_service_km",
            "next_service_date",
            "mypoints",
            "history_points",
            "is_staff",
            "is_superuser",
        )


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    next_service_km = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    next_service_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "mobile",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_staff",
            "is_superuser",
            "next_service_km",
            "next_service_date",
        )

    def validate_mobile(self, value):
        v = (value or "").strip()
        if User.objects.filter(mobile=v).exists():
            raise serializers.ValidationError("This mobile is already registered.")
        return v

    def create(self, validated_data):
        password = validated_data.pop("password")
        is_superuser = validated_data.pop("is_superuser", False)
        is_staff = validated_data.pop("is_staff", False)
        next_service_km = validated_data.pop("next_service_km", None)
        next_service_date = validated_data.pop("next_service_date", None)
        mobile = validated_data.pop("mobile")
        email = (validated_data.pop("email", None) or "").strip() or None
        first_name = (validated_data.pop("first_name", None) or "") or ""
        last_name = (validated_data.pop("last_name", None) or "") or ""

        extra = {}
        if next_service_km is not None:
            extra["next_service_km"] = next_service_km
        if next_service_date is not None:
            extra["next_service_date"] = next_service_date

        if is_superuser:
            user = User.objects.create_superuser(
                mobile=mobile,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                **extra,
            )
        else:
            user = User.objects.create_user(
                mobile=mobile,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                **extra,
            )
            if is_staff:
                user.is_staff = True
        SiteContactSettings.get_solo().apply_starting_points_to_user(user)
        user.save()
        return user


class AdminBookingSerializer(serializers.ModelSerializer):
    user_mobile = serializers.CharField(source="user_car.user.mobile", read_only=True)
    user_name = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    branch_id = serializers.IntegerField(source="branch.id", read_only=True, allow_null=True)
    time_id = serializers.IntegerField(source="time.id", read_only=True, allow_null=True)
    time_display = serializers.TimeField(source="time.time", format="%H:%M", read_only=True)
    services = serializers.SerializerMethodField()
    car_model = serializers.CharField(source="user_car.car_model.car_model", read_only=True)
    car_plate = serializers.CharField(source="user_car.plate_number", read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "user_mobile",
            "user_name",
            "branch_name",
            "branch_id",
            "time_id",
            "time_display",
            "date",
            "status",
            "slot_index",
            "customer_note",
            "workflow_status",
            "services",
            "car_model",
            "car_plate",
            "created_at",
        )

    def get_user_name(self, obj):
        u = obj.user_car.user if obj.user_car else None
        if not u:
            return ""
        parts = [u.first_name or "", u.last_name or ""]
        return " ".join(p for p in parts if p).strip() or (u.mobile or "")

    def get_services(self, obj):
        return [{"id": s.id, "name": s.name} for s in obj.service.all()]


class AdminBookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("workflow_status", "status", "branch", "time", "date", "slot_index")
        extra_kwargs = {
            "branch": {"required": False, "allow_null": True},
            "time": {"required": False, "allow_null": True},
            "date": {"required": False, "allow_null": True},
            "slot_index": {"required": False},
        }

    def validate(self, attrs):
        instance = self.instance
        if not instance:
            return attrs
        branch = attrs.get("branch", instance.branch)
        time = attrs.get("time", instance.time)
        if branch and time and getattr(time, "branch_id", None) and time.branch_id != branch.id:
            raise serializers.ValidationError(
                {"time": "The selected time slot does not belong to the selected branch."}
            )
        return attrs


class AdminServiceCategorySerializer(serializers.ModelSerializer):
    service_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "icon", "sort_order", "service_count")

    def get_service_count(self, obj):
        return obj.services.count()


class AdminServiceItemSerializer(serializers.ModelSerializer):
    service_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceItem
        fields = ("id", "name", "description", "service_count")

    def get_service_count(self, obj):
        return obj.services.count()


class AdminServiceSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.all(), required=False, allow_null=True
    )
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    branch_name = serializers.CharField(source="only_at_branch.name", read_only=True, allow_null=True)
    only_at_branch = serializers.PrimaryKeyRelatedField(
        queryset=Branches.objects.all(), required=False, allow_null=True
    )
    items = serializers.PrimaryKeyRelatedField(
        queryset=ServiceItem.objects.all(), many=True, required=False
    )
    compatible_with = serializers.PrimaryKeyRelatedField(
        queryset=CarModels.objects.all(), many=True, required=False
    )

    class Meta:
        model = Services
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["compatible_with_models"] = [
            {"id": c.id, "car_model": c.car_model} for c in instance.compatible_with.all()
        ]
        data["items_detail"] = [
            {"id": i.id, "name": i.name, "description": i.description}
            for i in instance.items.all()
        ]
        return data


class AdminAccessorySerializer(serializers.ModelSerializer):
    compatible_with = serializers.PrimaryKeyRelatedField(
        queryset=CarModels.objects.all(), many=True, required=False
    )

    class Meta:
        model = Accessories
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["compatible_with_models"] = [
            {"id": c.id, "car_model": c.car_model} for c in instance.compatible_with.all()
        ]
        return data


class AdminLoyaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyPoints
        fields = "__all__"


class AdminSiteContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteContactSettings
        fields = (
            "whatsapp_e164",
            "tech_hotline_e164",
            "winch_primary",
            "winch_secondary",
            "app_theme_default",
            "user_can_change_theme",
            "new_user_default_points",
        )


class AdminUserCarListSerializer(serializers.ModelSerializer):
    car_model_name = serializers.CharField(source="car_model.car_model", read_only=True)

    class Meta:
        model = UserCars
        fields = (
            "id",
            "user",
            "car_model",
            "car_model_name",
            "model_year",
            "plate_number",
            "chassis_number",
        )
