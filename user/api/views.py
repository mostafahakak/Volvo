from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import app.messages as response_message
from app.models import MyHistory, SiteContactSettings
from user.api.serializer import RegisterSerializer, LoginSerializer, UserCarsSerializer, UserSerializer, \
    LoyaltySerializer, UserSerializer2
from user.firebase_auth import verify_firebase_id_token
from user.models import User, LoyaltyPoints, UserRequests


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


def _normalize_phone(s):
    if not s:
        return ""
    return "".join(s.split())


def _normalize_phone_e164(s):
    """
    Collapse whitespace then fix common Egypt typo: +2001... → +201...
    (leading0 after country code 20).
    """
    d = _normalize_phone(s)
    if d.startswith("+20") and len(d) > 4 and d[4] == "0":
        d = "+20" + d[5:]
    return d


class FirebasePhoneAuthView(APIView):
    """
    After Firebase Phone Auth on the client, send the Firebase ID token.
    Creates a local user if missing (pending admin verification: is_verified=False).
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        id_token = request.data.get("id_token") or request.data.get("idToken")
        mobile = _normalize_phone_e164(
            request.data.get("mobile") or request.data.get("phone") or ""
        )
        first_name = (request.data.get("first_name") or "").strip() or "User"
        last_name = (request.data.get("last_name") or "").strip() or ""

        if not mobile:
            return Response(
                {"error": "mobile is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        decoded = verify_firebase_id_token(id_token) if id_token else None
        phone_from_token = (decoded or {}).get("phone_number") or ""
        phone_from_token = _normalize_phone_e164(phone_from_token)

        if decoded is None:
            return Response(
                {"error": "Invalid or expired Firebase token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if phone_from_token and phone_from_token != mobile:
            return Response(
                {"error": "Phone number does not match Firebase token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(mobile=mobile).first()
        if not user:
            user = User.objects.create_user(
                mobile=mobile,
                email=None,
                password=None,
                first_name=first_name,
                last_name=last_name,
            )
            user.is_verified = False
            SiteContactSettings.get_solo().apply_starting_points_to_user(user)
            user.save()
            UserRequests.objects.create(user=user)

        refresh = RefreshToken.for_user(user)
        payload = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_data": UserSerializer(user).data,
        }
        return Response(payload, status=status.HTTP_200_OK)


class SignUp(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        user_exit = User.objects.filter(mobile=request.data.get('mobile')).first()
        if user_exit:
            return Response({"error": "This Mobile Used Before"}, status=status.HTTP_400_BAD_REQUEST)
        created_user = RegisterSerializer(data=request.data)
        created_user.is_valid(raise_exception=True)
        user = created_user.save()
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
