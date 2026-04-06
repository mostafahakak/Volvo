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
            "mypoints"
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
            "mypoints"
        ]




class RegisterSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

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
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            mobile=validated_data["mobile"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
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
            if not user.is_verified:
                error = serializers.ValidationError(
                    {"error": "This User Is Not Verified"}
                )
                self.handel_error(error)
            # raise serializers.ValidationError({
            #     "error": "This User Is Not Verified"
            # })

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

class LoyaltySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyPoints
        fields = "__all__"