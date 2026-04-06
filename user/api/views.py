from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import requests
from rest_framework_simplejwt.views import TokenObtainPairView
import app.messages as response_message
from app.models import MyHistory
from user.api.serializer import RegisterSerializer, LoginSerializer, UserCarsSerializer, UserSerializer, \
    LoyaltySerializer, UserSerializer2
from user.models import User, LoyaltyPoints, UserRequests


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class SignUp(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        user_exit = User.objects.filter(mobile=request.data.get('mobile')).first()
        if user_exit:
            return Response({"error": "This Mobile Used Before"}, status=status.HTTP_400_BAD_REQUEST)
        created_user = RegisterSerializer(data=request.data)
        created_user.is_valid(raise_exception=True)
        created_user.save()
        print(created_user.data)
        user = User.objects.filter(id=created_user.data.get('id')).first()
        UserRequests.objects.create(user=user).save()
        # user_data = {
        #     "mobile": created_user.data.get('mobile'),
        #     "password": request.data.get("password")
        # }
        # base_url = request.build_absolute_uri().split("/api")[0]
        # print(base_url)
        # login_serializer = requests.post(url=f"{base_url}/api/login", json=user_data).json()
        return Response(response_message.success(created_user.data, success_key="success"),
                        status=status.HTTP_201_CREATED)


class AddUserCar(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = UserCarsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_201_CREATED)


class Profile(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.user.id).first()
        histories = MyHistory.objects.filter(user=user)
        points = 0
        for history in histories:
            for service in history.service.all():
                points += service.points
        if user.mypoints != points:
            user.mypoints = points
            user.save()
        serializer = UserSerializer(user)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class UpdateProfile(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.user.id).first()
        new_mobile = request.data.get("mobile")
        mobile_check = User.objects.filter(mobile=new_mobile).first()
        if mobile_check and mobile_check.id != request.user.id:
            return Response(response_message.error("mobile_exist", ""), status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer2(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class LoyaltyLevel(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        loyalty_points = LoyaltyPoints.objects.all()
        serializer = LoyaltySerializer(loyalty_points, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ChangePassword(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id)
        old_password = request.data.get("old_password")
        print(old_password)
        if user.check_password(old_password):
            new_password = request.data.get("new_password")
            conf_password = request.data.get("conf_password")
            if new_password == conf_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)
                user.save()
                return Response(
                    response_message.success(
                        "You Have Changed Your Password!!", "success"
                    )
                )
            else:
                return Response(
                    response_message.error("error", ""),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response({"error": "error"})
