from rest_framework import serializers

from app.models import Accessories, Booking, MaintenanceSchedule, Services, SiteContactSettings
from user.models import CarModels, LoyaltyPoints, User


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
        mobile = validated_data.pop("mobile")
        email = (validated_data.pop("email", None) or "").strip() or None
        first_name = (validated_data.pop("first_name", None) or "") or ""
        last_name = (validated_data.pop("last_name", None) or "") or ""

        if is_superuser:
            return User.objects.create_superuser(
                mobile=mobile,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        user = User.objects.create_user(
            mobile=mobile,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        if is_staff:
            user.is_staff = True
            user.save(update_fields=["is_staff"])
        return user


class AdminBookingSerializer(serializers.ModelSerializer):
    user_mobile = serializers.CharField(source="user_car.user.mobile", read_only=True)
    user_name = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source="branch.name", read_only=True)
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
            "time_display",
            "date",
            "status",
            "slot_index",
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
        fields = ("workflow_status", "status")


class AdminAccessorySerializer(serializers.ModelSerializer):
    compatible_with = serializers.PrimaryKeyRelatedField(
        queryset=CarModels.objects.all(), many=True, required=False
    )

    class Meta:
        model = Accessories
        fields = "__all__"


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
        )
