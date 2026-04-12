from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.base64 import Base64FileField
from user.models import User, UserCars, LoyaltyPoints


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "mobile",
            "password",
            "email",
            "avatar",
            "mypoints",
            "is_verified",
            "next_service_km",
            "next_service_date",
        ]
        extra_kwargs = {"password": {"write_only": True}}

class UserSerializer2(serializers.ModelSerializer):
    avatar = Base64FileField(required=False)
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "mobile",
            "avatar",
            "mypoints",
            "is_verified",
            "next_service_km",
            "next_service_date",
        ]




class RegisterSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password2 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            "password",
            "password2",
            "email",
            "mobile",
            "first_name",
            "last_name",
            # "type",
        )
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
            # "type": {"required": True},
        }

    def validate(self, attrs):
        p1 = (attrs.get("password") or "").strip()
        p2 = (attrs.get("password2") or "").strip()
        if p1 or p2:
            if p1 != p2:
                raise serializers.ValidationError(
                    {"password": "Password fields didn't match."}
                )
            if p1:
                validate_password(p1)
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = (validated_data.pop("password", None) or "").strip()
        email = validated_data.get("email")
        if email == "":
            email = None
        user = User.objects.create_user(
            mobile=validated_data["mobile"],
            email=email,
            password=password if password else None,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.is_verified = False
        user.save()

        return user


class LoginSerializer(TokenObtainPairSerializer):
    mobile = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["user_id"] = str(user.id)
        return token

    def handel_error(self, error):
        if isinstance(error.detail, list) and len(error.detail) == 1:
            error.detail = error.detail[0]
        elif isinstance(error.detail, str):
            pass
            # error_response.data = get_response(
            #     message=error[0], status_code=error_response.status_code)
        elif isinstance(error, dict):
            pass
        raise error

    def validate(self, attrs):
        username = attrs.get("mobile")
        data = {}

        try:
            user = User.objects.get(mobile=username)
            # is_verified = admin approved for booking/maintenance; login is always allowed.

            data = super(LoginSerializer, self).validate(attrs)
            user_serializer = UserSerializer(user)
            data.update({"user_data": user_serializer.data})
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "user does not exist"})
            # data.update({"error": "user does not exist"})

        return data


class UserCarsSerializer(serializers.ModelSerializer):
    car_document_front = Base64FileField(required=False)
    car_document_back = Base64FileField(required=False)

    class Meta:
        model = UserCars
        fields = "__all__"

    def validate(self, attrs):
        chassis = (attrs.get("chassis_number") or "").strip()
        plate = (attrs.get("plate_number") or "").strip()
        if chassis:
            qs = UserCars.objects.filter(chassis_number__iexact=chassis)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"chassis_number": "This VIN is already registered."}
                )
        if plate:
            qs = UserCars.objects.filter(plate_number__iexact=plate)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"plate_number": "This plate number is already registered."}
                )
        return attrs

class LoyaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyPoints
        fields = "__all__"