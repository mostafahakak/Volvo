from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import app.messages as response_message
from app.models import SiteContactSettings
from user.api.serializer import RegisterSerializer, LoginSerializer, UserCarsSerializer, UserSerializer, \
    LoyaltySerializer, UserSerializer2
from user.firebase_auth import verify_firebase_id_token
from user.admin_notify import notify_all_staff_fcm
from user.models import User, LoyaltyPoints, UserRequests, UserCars


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class CheckMobileRegisteredView(APIView):
    """
    Public: whether an E.164 mobile is already registered (before Firebase OTP on sign-up).
    Query: ?mobile=%2B2010...
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        raw = request.query_params.get("mobile") or request.query_params.get("phone") or ""
        mobile = _normalize_phone_e164(raw)
        if not mobile or len(mobile) < 8:
            return Response(
                response_message.error("error", "mobile query parameter is required"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        exists = User.objects.filter(mobile=mobile).exists()
        return Response(
            response_message.success({"exists": exists}, success_key="success"),
            status=status.HTTP_200_OK,
        )


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


def _account_deactivated_response():
    return Response(
        {
            "error": (
                "This account was deactivated. Contact the dealer to restore access."
            ),
            "account_deactivated": True,
        },
        status=status.HTTP_403_FORBIDDEN,
    )


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
        email = (request.data.get("email") or "").strip().lower() or None

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
        created_pending_verification = False
        if user and not user.is_active:
            return _account_deactivated_response()
        if not user:
            user = User.objects.create_user(
                mobile=mobile,
                email=email,
                password=None,
                first_name=first_name,
                last_name=last_name,
            )
            user.is_verified = False
            SiteContactSettings.get_solo().apply_starting_points_to_user(user)
            user.save()
            UserRequests.objects.create(user=user)
            created_pending_verification = True
        elif email and not user.email:
            user.email = email
            user.save(update_fields=["email"])

        if created_pending_verification:
            try:
                notify_all_staff_fcm(
                    title="New registration pending verification",
                    body=(
                        f"{first_name} {last_name} ({mobile}) signed up and needs "
                        "admin approval."
                    ),
                    data={
                        "type": "user_pending_verification",
                        "user_id": str(user.pk),
                    },
                )
            except Exception:
                pass

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
        try:
            notify_all_staff_fcm(
                title="New registration pending verification",
                body=(
                    f"{user.first_name or ''} {user.last_name or ''} ({user.mobile}) "
                    "registered and needs admin approval."
                ),
                data={
                    "type": "user_pending_verification",
                    "user_id": str(user.pk),
                },
            )
        except Exception:
            pass
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
        car = serializer.save(user=request.user)
        try:
            u = request.user
            vin = (car.chassis_number or "").strip()
            plate = (car.plate_number or "").strip()
            notify_all_staff_fcm(
                title="Vehicle pending verification",
                body=(
                    f"{u.first_name or ''} {u.last_name or ''} ({u.mobile}) submitted a "
                    f"vehicle (VIN ending …{vin[-6:] if len(vin) >= 6 else vin}, plate {plate}) "
                    "for verification."
                ),
                data={
                    "type": "vehicle_pending_verification",
                    "user_id": str(u.pk),
                    "user_car_id": str(car.pk),
                },
            )
        except Exception:
            pass
        return Response(
            response_message.success(serializer.data, success_key="success"),
            status=status.HTTP_201_CREATED,
        )


def _user_may_modify_vehicle(car: UserCars) -> bool:
    if not car.is_verified:
        return True
    return bool(car.allow_user_edit)


class UserCarDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_car(self, request, pk: int) -> UserCars:
        return get_object_or_404(UserCars, pk=pk, user=request.user)

    def patch(self, request, pk, *args, **kwargs):
        car = self.get_car(request, pk)
        if not _user_may_modify_vehicle(car):
            return Response(
                response_message.error(
                    "error",
                    "This vehicle is verified. Ask the dealer for edit access, or use a vehicle that is not yet verified.",
                ),
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UserCarsSerializer(
            car,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            response_message.success(serializer.data, success_key="success"),
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk, *args, **kwargs):
        car = self.get_car(request, pk)
        if not _user_may_modify_vehicle(car):
            return Response(
                response_message.error(
                    "error",
                    "This vehicle is verified. Ask the dealer for access to remove it.",
                ),
                status=status.HTTP_403_FORBIDDEN,
            )
        car.delete()
        return Response(
            response_message.success({"deleted": True}, success_key="success"),
            status=status.HTTP_200_OK,
        )


class Profile(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = User.objects.select_related("user_type").filter(id=request.user.id).first()
        serializer = UserSerializer(user)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class UpdateNotificationTokenView(APIView):
    """
    Store the device FCM token for the current user. Call on app start / resume
    so booking notifications reach the right device.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        token = (
            (request.data.get("fcm_token") or request.data.get("notification_token") or "")
            .strip()
        )
        if not token:
            return Response(
                response_message.error("error", "fcm_token or notification_token is required"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(token) > 10000:
            return Response(
                response_message.error("error", "FCM token exceeds max length"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        user.notification_token = token
        user.save(update_fields=["notification_token"])
        return Response(
            response_message.success({"updated": True}, success_key="success"),
            status=status.HTTP_200_OK,
        )


class UpdateProfile(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = User.objects.select_related("user_type").filter(id=request.user.id).first()
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


class DeleteAccountView(APIView):
    """
    Soft-delete: deactivate the account but keep all user data in the database.
    The user cannot sign in again until an admin reactivates the account.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_staff or user.is_superuser:
            return Response(
                {"error": "Staff accounts cannot be deleted from the app."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.notification_token = ""
        user.save(update_fields=["is_active", "notification_token"])
        return Response(
            {
                "deleted": True,
                "message": "Your account has been deactivated.",
            },
            status=status.HTTP_200_OK,
        )


class SocialAuthCheckView(APIView):
    """
    Verify a Firebase ID token from Apple/Google Sign-In.
    If a user with the token's email exists, return JWT tokens (login).
    Otherwise return exists=false so the app can redirect to registration.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        id_token = request.data.get("id_token") or request.data.get("idToken")

        decoded = verify_firebase_id_token(id_token) if id_token else None
        if decoded is None:
            return Response(
                {"error": "Invalid or expired Firebase token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = (decoded.get("email") or "").strip().lower()
        name = decoded.get("name") or ""

        if not email:
            firebase_info = decoded.get("firebase", {})
            identities = firebase_info.get("identities", {})
            email_list = identities.get("email", [])
            if email_list:
                email = email_list[0].strip().lower()

        if not email:
            return Response(
                {"error": "No email associated with this account"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()
        if user:
            if not user.is_active:
                return _account_deactivated_response()
            refresh = RefreshToken.for_user(user)
            return Response({
                "exists": True,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_data": UserSerializer(user).data,
            }, status=status.HTTP_200_OK)

        return Response({
            "exists": False,
            "email": email,
            "name": name,
        }, status=status.HTTP_200_OK)
