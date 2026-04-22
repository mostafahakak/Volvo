import datetime

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
    AdminServiceCategorySerializer,
    AdminServiceItemSerializer,
    AdminServiceSerializer,
    AdminSiteContactSerializer,
    AdminUserCarListSerializer,
    AdminUserCreateSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
)
from app.models import (
    Accessories,
    Booking,
    MaintenanceSchedule,
    ServiceCategory,
    ServiceItem,
    Services,
    SiteContactSettings,
    Timing,
)
from app.serializers import CarModelSerializer, MaintenanceScheduleSerializer, BranchesSerializer
from user.api.serializer import UserSerializer
from user.models import Branches, CarModels, LoyaltyPoints, User, UserCars


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
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response(
                response_message.error("invalid_credentials", "Invalid credentials"),
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_staff:
            return Response(
                response_message.error(
                    "error",
                    "This email is not a staff account. On the server run: python manage.py create_dashboard_admin",
                ),
                status=status.HTTP_403_FORBIDDEN,
            )
        if not user.check_password(password):
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


class AdminUserCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserCreateSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(
            response_message.success(AdminUserSerializer(user).data, "success"),
            status=status.HTTP_201_CREATED,
        )


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


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
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

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.pk == request.user.pk:
            return Response(
                response_message.error("error", "You cannot delete your own account."),
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(user)
        return Response(
            response_message.success({"deleted": True}, "success"),
            status=status.HTTP_200_OK,
        )


class AdminBookingCreateView(APIView):
    """Create a service booking on behalf of any user (no is_verified / car-ownership checks)."""

    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        service_ids = request.data.get("services") or []
        if not service_ids:
            return Response(
                response_message.error("error", "At least one service is required"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(service_ids) != len(set(service_ids)):
            return Response(
                response_message.error("error", "Duplicate service ids are not allowed"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        services = Services.objects.filter(id__in=service_ids)
        if services.count() != len(set(service_ids)):
            return Response(
                response_message.error("error", "Invalid service id"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        time = Timing.objects.filter(id=request.data.get("time_id")).first()
        user_car = UserCars.objects.filter(id=request.data.get("user_car")).first()
        branch = Branches.objects.filter(id=request.data.get("branch_id")).first()
        date = request.data.get("date")
        if not all([time, user_car, branch, date]):
            return Response(
                response_message.error("error", "user_car, branch_id, time_id, and date are required"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if d.weekday() == 4:
                return Response(
                    response_message.error("error", "Fridays are closed for booking"),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (TypeError, ValueError):
            return Response(
                response_message.error("error", "date must be YYYY-MM-DD"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        for svc in services:
            if svc.only_at_branch_id and svc.only_at_branch_id != branch.id:
                return Response(
                    response_message.error(
                        "error",
                        f'Service "{svc.name}" is only available at branch {svc.only_at_branch.name}',
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:
            slot_index = int(request.data.get("slot_index", 0))
        except (TypeError, ValueError):
            return Response(
                response_message.error("error", "slot_index must be 0, 1, or 2"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        if slot_index not in (0, 1, 2):
            return Response(
                response_message.error("error", "slot_index must be 0, 1, or 2"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Booking.objects.filter(
            branch=branch, time=time, date=date, slot_index=slot_index, status=False
        ).exclude(workflow_status=Booking.WORKFLOW_CANCELLED).exists():
            return Response(
                response_message.error("error", "This time slot is already reserved"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking = Booking.objects.create(
            user_car=user_car,
            branch=branch,
            time=time,
            date=date,
            slot_index=slot_index,
            workflow_status=Booking.WORKFLOW_PENDING,
        )
        for service in services:
            booking.service.add(service)
        booking.save()
        booking = (
            Booking.objects.filter(pk=booking.pk)
            .select_related("branch", "time", "user_car", "user_car__user", "user_car__car_model")
            .prefetch_related("service")
            .first()
        )
        return Response(
            response_message.success(AdminBookingSerializer(booking).data, "success"),
            status=status.HTTP_201_CREATED,
        )


class AdminUserCarsListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserCarListSerializer

    def get_queryset(self):
        qs = UserCars.objects.all().select_related("car_model", "user").order_by("-id")
        uid = self.request.query_params.get("user_id")
        if uid:
            qs = qs.filter(user_id=uid)
        return qs

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(
            response_message.success(resp.data, "success"),
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


class AdminLoyaltyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = LoyaltyPoints.objects.all()
    serializer_class = AdminLoyaltySerializer

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


class AdminBranchesListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        data = BranchesSerializer(Branches.objects.all().order_by("name"), many=True).data
        return Response(response_message.success(data, "success"), status=status.HTTP_200_OK)


class AdminCarModelsListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = CarModels.objects.all().order_by("car_model")
    serializer_class = CarModelSerializer
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


class AdminCarModelDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = CarModels.objects.all()
    serializer_class = CarModelSerializer
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


class AdminServiceCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = ServiceCategory.objects.all().order_by("sort_order", "id")
    serializer_class = AdminServiceCategorySerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(response_message.success(resp.data, "success"), status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        return Response(response_message.success(resp.data, "success"), status=status.HTTP_201_CREATED)


class AdminServiceCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ServiceCategory.objects.all()
    serializer_class = AdminServiceCategorySerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        return Response(response_message.success(resp.data, "success"), status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        return Response(response_message.success(resp.data, "success"), status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(response_message.success({"deleted": True}, "success"), status=status.HTTP_200_OK)


class AdminServiceItemListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = ServiceItem.objects.all().order_by("name")
    serializer_class = AdminServiceItemSerializer

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        return Response(response_message.success(resp.data, "success"), status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        return Response(response_message.success(resp.data, "success"), status=status.HTTP_201_CREATED)


class AdminServiceItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ServiceItem.objects.all()
    serializer_class = AdminServiceItemSerializer

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        return Response(response_message.success(resp.data, "success"), status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        resp = super().update(request, *args, **kwargs)
        return Response(response_message.success(resp.data, "success"), status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(response_message.success({"deleted": True}, "success"), status=status.HTTP_200_OK)


class AdminServicesListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = (
        Services.objects.all()
        .select_related("category", "only_at_branch")
        .prefetch_related("items", "compatible_with")
        .order_by("category__sort_order", "name")
    )
    serializer_class = AdminServiceSerializer
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
    queryset = (
        Services.objects.all()
        .select_related("category", "only_at_branch")
        .prefetch_related("items", "compatible_with")
    )
    serializer_class = AdminServiceSerializer
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
    queryset = MaintenanceSchedule.objects.all().select_related("car_model").order_by("-id")
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
    queryset = MaintenanceSchedule.objects.all().select_related("car_model")
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
