from django.db.models import Q
from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

import app.messages as response_message
from app.api.admin_serializers import (
    AdminAccessorySerializer,
    AdminBookingSerializer,
    AdminBookingUpdateSerializer,
    AdminLoyaltySerializer,
    AdminSiteContactSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
)
from app.models import Accessories, Booking, MaintenanceSchedule, Services, SiteContactSettings
from app.serializers import CarModelSerializer, MaintenanceScheduleSerializer, ServicesSerializer, BranchesSerializer
from user.api.serializer import UserSerializer
from user.models import Branches, CarModels, LoyaltyPoints, User


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = (request.data.get("email") or "").strip()
        password = request.data.get("password") or ""
        if not email or not password:
            return Response(
                {"detail": "email and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(email__iexact=email, is_staff=True).first()
        if not user or not user.check_password(password):
            return Response(
                response_message.error("invalid_credentials", "Invalid credentials"),
                status=status.HTTP_401_UNAUTHORIZED,
            )
        refresh = RefreshToken.for_user(user)
        payload = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_data": UserSerializer(user).data,
        }
        return Response(payload, status=status.HTTP_200_OK)


class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        q = (self.request.query_params.get("q") or "").strip()
        qs = User.objects.all().select_related("user_type").order_by("-id")
        if q:
            qs = qs.filter(
                Q(mobile__icontains=q)
                | Q(email__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
            )
        return qs

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().select_related("user_type")
    serializer_class = AdminUserSerializer

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return AdminUserUpdateSerializer
        return AdminUserSerializer

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        user = self.get_object()
        return Response(
            response_message.success(AdminUserSerializer(user).data, "success"),
            status=status.HTTP_200_OK,
        )


class AdminBookingListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminBookingSerializer

    def get_queryset(self):
        qs = (
            Booking.objects.all()
            .select_related("branch", "time", "user_car", "user_car__user", "user_car__car_model")
            .prefetch_related("service")
            .order_by("-created_at")
        )
        wf = self.request.query_params.get("workflow_status")
        if wf:
            qs = qs.filter(workflow_status=wf)
        return qs

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )


class AdminBookingDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = (
        Booking.objects.all()
        .select_related("branch", "time", "user_car", "user_car__user", "user_car__car_model")
        .prefetch_related("service")
    )
    serializer_class = AdminBookingSerializer

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return AdminBookingUpdateSerializer
        return AdminBookingSerializer

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        booking = (
            Booking.objects.filter(pk=self.kwargs["pk"])
            .select_related("branch", "time", "user_car", "user_car__user", "user_car__car_model")
            .prefetch_related("service")
            .first()
        )
        return Response(
            response_message.success(AdminBookingSerializer(booking).data, "success"),
            status=status.HTTP_200_OK,
        )


class AdminLoyaltyListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = LoyaltyPoints.objects.all().order_by("id")
    serializer_class = AdminLoyaltySerializer

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )


class AdminBranchesListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        data = BranchesSerializer(Branches.objects.all().order_by("name"), many=True).data
        return Response(response_message.success(data, "success"), status=status.HTTP_200_OK)


class AdminCarModelsListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        data = CarModelSerializer(CarModels.objects.all().order_by("car_model"), many=True).data
        return Response(response_message.success(data, "success"), status=status.HTTP_200_OK)


class AdminServicesListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Services.objects.all().order_by("name")
    serializer_class = ServicesSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_201_CREATED,
        )


class AdminServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            response_message.success({"deleted": True}, "success"),
            status=status.HTTP_200_OK,
        )


class AdminAccessoriesListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Accessories.objects.all().order_by("-id")
    serializer_class = AdminAccessorySerializer

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_201_CREATED,
        )


class AdminAccessoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Accessories.objects.all().prefetch_related("compatible_with")
    serializer_class = AdminAccessorySerializer

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            response_message.success({"deleted": True}, "success"),
            status=status.HTTP_200_OK,
        )


class AdminMaintenanceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = MaintenanceSchedule.objects.all().order_by("-id")
    serializer_class = MaintenanceScheduleSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_201_CREATED,
        )


class AdminMaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = MaintenanceSchedule.objects.all()
    serializer_class = MaintenanceScheduleSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            response_message.success({"deleted": True}, "success"),
            status=status.HTTP_200_OK,
        )


class AdminSiteContactView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        s = SiteContactSettings.get_solo()
        data = AdminSiteContactSerializer(s).data
        return Response(response_message.success(data, "success"), status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        s = SiteContactSettings.get_solo()
        ser = AdminSiteContactSerializer(s, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(
            response_message.success(AdminSiteContactSerializer(s).data, "success"),
            status=status.HTTP_200_OK,
        )
