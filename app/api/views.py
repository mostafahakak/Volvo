import datetime

from django.db.models import Q, Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
import app.messages as response_message
from app.models import MyHistory, MaintenanceSchedule, Branches, BranchSlot, Services, ServiceCategory, ServiceItem, \
    Accessories, UsedCarsImage, UsedCar, AboutUS, Timing, Booking, TechnicalAssistant, SiteContactSettings
from app.serializers import *
from app.serializers import ServiceCategorySerializer, ServiceItemSerializer
from user.models import CarModels, UserCars


# Create your views here.
class ListCarModel(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        car_model = CarModels.objects.all()
        serializer = CarModelSerializer(car_model, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListMaintenanceSchedule(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        qs = MaintenanceSchedule.objects.all().select_related("car_model")
        cm = request.query_params.get("car_model_id")
        if cm:
            qs = qs.filter(car_model_id=cm)
        serializer = MaintenanceScheduleSerializer(qs, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListMyHistory(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        histories = MyHistory.objects.filter(user=request.user)
        serializer = MyHistorySerializer(histories, many=True)
        data = []
        for history in serializer.data:
            points = 0
            history_data = MyHistory.objects.filter(id=history.get("id")).first()
            for service in history_data.service.all():
                points += service.points
            history['points'] = points
            data.append(history)
        return Response(response_message.success(data, success_key="success"), status=status.HTTP_200_OK)


class ListMyServiceBookings(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        qs = (
            Booking.objects.filter(user_car__user=request.user)
            .select_related("branch", "time", "user_car", "user_car__car_model")
            .prefetch_related("service")
            .order_by("-created_at")
        )
        serializer = BookingHistorySerializer(qs, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListUserCars(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cars = UserCars.objects.filter(user=request.user)
        serializer = UserCarsSerializer(cars, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListBranches(generics.ListAPIView):
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        # All branches are managed in the admin dashboard; apps use this list for
        # Book a service, Find us, etc. (book_service=1 only controls client query params.)
        branch = Branches.objects.all().order_by("name")
        serializer = BranchesSerializer(branch, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListBranchSlot(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        branch = BranchSlot.objects.all()
        serializer = BranchSlotSerializer(branch, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListServices(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        qs = (
            Services.objects.all()
            .select_related("category", "only_at_branch")
            .prefetch_related("items", "compatible_with")
        )
        cat = request.query_params.get("category_id")
        if cat:
            qs = qs.filter(category_id=cat)
        car_model_id = request.query_params.get("car_model_id")
        if car_model_id:
            # Include services with no compatibility set (universal) + those matching the car.
            qs = qs.filter(Q(compatible_with__isnull=True) | Q(compatible_with__id=car_model_id)).distinct()
        serializer = ServicesSerializer(qs, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListServiceCategories(generics.ListAPIView):
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        qs = ServiceCategory.objects.all().order_by("sort_order", "id")
        serializer = ServiceCategorySerializer(qs, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListServiceItems(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        qs = ServiceItem.objects.all().order_by("name")
        service_id = request.query_params.get("service_id")
        if service_id:
            qs = qs.filter(services__id=service_id).distinct()
        serializer = ServiceItemSerializer(qs, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListAccessories(generics.ListAPIView):
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        accessory = (
            Accessories.objects.filter(kind=Accessories.KIND_ACCESSORY)
            .order_by("id")
            .prefetch_related("compatible_with")
        )
        serializer = AccessoriesSerializer(accessory, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListUsedCars(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        used_car = UsedCar.objects.all()
        serializer = UsedCarSerializer(used_car, many=True)
        data = []
        for x in serializer.data:
            image = UsedCarsImage.objects.filter(used_car_id=x.get('id'))
            serializers = UsedCarsImageSerializer(image, many=True)
            x["images"] = serializers.data
            data.append(x)

        return Response(response_message.success(data, success_key="success"), status=status.HTTP_200_OK)


class BookUsedCarsRequest(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = BookUsedCarsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(response_message.success(serializer.data, "success"), status=status.HTTP_201_CREATED)


class BookAccessoriesRequest(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = BookAccessoriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(response_message.success(serializer.data, success_key="success"),
                        status=status.HTTP_201_CREATED)


class ListOffers(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        accessory = (
            Accessories.objects.filter(kind=Accessories.KIND_SPECIAL_OFFER)
            .order_by("id")
            .prefetch_related("compatible_with")
        )
        serializer = AccessoriesSerializer(accessory, many=True)
        data = []
        for access in serializer.data:
            price = access.get("price") or 0
            disc = access.get("discount") or 0
            access["price_after"] = price - (price * (disc / 100.0)) if disc else price
            data.append(access)
        return Response(response_message.success(data, success_key="success"), status=status.HTTP_200_OK)


class SiteContactSettingsPublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        s = SiteContactSettings.get_solo()
        from app.serializers import SiteContactSettingsSerializer

        return Response(
            response_message.success(SiteContactSettingsSerializer(s).data, success_key="success"),
            status=status.HTTP_200_OK,
        )


class ListAboutUs(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        about = AboutUS.objects.all()
        serializer = AboutUsSerializers(about, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class CreateFeedBack(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        car_model = CarModels.objects.filter(id=request.data.get('car_model')).first()
        serializer = FeedBackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(car_model=car_model)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class CreateContactUS(generics.CreateAPIView):
    def create(self, request, *args, **kwargs):
        car_model = CarModels.objects.filter(id=request.data.get('car_model')).first()
        serializer = ContactUSSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(car_model=car_model)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListTimeToBookService(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        branch = Branches.objects.filter(id=request.query_params.get("branch_id")).first()
        if not branch:
            return Response(
                response_message.error("error", "branch_id required"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        date_str = request.query_params.get("date")
        if date_str:
            try:
                d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if d.weekday() == 4:
                    return Response(
                        response_message.success([], success_key="success"),
                        status=status.HTTP_200_OK,
                    )
            except ValueError:
                pass
        timing = Timing.objects.filter(branch=branch)
        booked = Booking.objects.filter(
            branch=branch, time__in=timing, date=date_str, status=False
        ).exclude(workflow_status=Booking.WORKFLOW_CANCELLED)
        serializer = TimingSerializer(timing, many=True).data
        data = []
        for book in serializer:
            slots_out = []
            for slot_index in (0, 1, 2):
                taken = booked.filter(time_id=book.get('id'), slot_index=slot_index).exists()
                slots_out.append({"slot_index": slot_index, "available": not taken})
            book["slots"] = slots_out
            book["available"] = any(s["available"] for s in slots_out)
            data.append(book)
        return Response(response_message.success(data, success_key="success"), status=status.HTTP_200_OK)


class BookAService(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_verified:
            return Response(
                {
                    "status": False,
                    "error": "Your account is pending verification. Please wait for admin approval.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        service_ids = request.data.get("services") or []
        if not service_ids:
            return Response(
                {"error": "At least one service is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(service_ids) != len(set(service_ids)):
            return Response(
                {"error": "Duplicate service ids are not allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        services = Services.objects.filter(id__in=service_ids).prefetch_related("items")
        if services.count() != len(set(service_ids)):
            return Response(
                {"error": "Invalid service id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        time = Timing.objects.filter(id=request.data.get("time_id")).first()
        user_car = UserCars.objects.filter(id=request.data.get("user_car")).first()
        branch = Branches.objects.filter(id=request.data.get("branch_id")).first()
        date = request.data.get("date")
        if not all([time, user_car, branch, date]):
            return Response(
                {"error": "user_car, branch_id, time_id, and date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_car.user_id != request.user.id:
            return Response(
                {"error": "Car does not belong to this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            d = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if d.weekday() == 4:
                return Response(
                    {"error": "Fridays are closed for booking"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (TypeError, ValueError):
            return Response(
                {"error": "date must be YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for svc in services:
            if svc.only_at_branch_id and svc.only_at_branch_id != branch.id:
                return Response(
                    {
                        "error": f'Service "{svc.name}" is only available at branch {svc.only_at_branch.name}',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        slot_index = int(request.data.get("slot_index", 0))
        if slot_index not in (0, 1, 2):
            return Response(
                {"error": "slot_index must be 0, 1, or 2"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Booking.objects.filter(
            branch=branch, time=time, date=date, slot_index=slot_index, status=False
        ).exclude(workflow_status=Booking.WORKFLOW_CANCELLED).exists():
            return Response(
                {"error": "This time slot is already reserved"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        customer_note = (request.data.get("customer_note") or request.data.get("note") or "")
        if isinstance(customer_note, str):
            customer_note = customer_note.strip()[:5000]
        else:
            customer_note = ""

        raw_selections = request.data.get("service_item_selections")
        if raw_selections is None:
            raw_selections = []
        if not isinstance(raw_selections, list):
            return Response(
                {"error": "service_item_selections must be a list"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        selection_by_service = {}
        for entry in raw_selections:
            if not isinstance(entry, dict):
                return Response(
                    {"error": "Each service_item_selections entry must be an object"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                sid = int(entry.get("service_id"))
            except (TypeError, ValueError):
                return Response(
                    {"error": "service_id in service_item_selections must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            item_ids = entry.get("item_ids")
            if item_ids is None:
                item_ids = []
            if not isinstance(item_ids, list):
                return Response(
                    {"error": "item_ids must be a list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                parsed_ids = [int(x) for x in item_ids]
            except (TypeError, ValueError):
                return Response(
                    {"error": "item_ids must be a list of integers"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if len(parsed_ids) != len(set(parsed_ids)):
                return Response(
                    {"error": "Duplicate item_ids are not allowed for a service"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if sid in selection_by_service:
                return Response(
                    {"error": "Duplicate service_id in service_item_selections"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            selection_by_service[sid] = parsed_ids
        booked_service_ids = set(services.values_list("id", flat=True))
        extra_sids = set(selection_by_service.keys()) - booked_service_ids
        if extra_sids:
            return Response(
                {
                    "error": "service_item_selections includes a service_id that is not in this booking",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        normalized_selections = []
        for svc in services:
            linked_ids = set(svc.items.values_list("id", flat=True))
            chosen = selection_by_service.get(svc.id, [])
            if not linked_ids:
                if chosen:
                    return Response(
                        {
                            "error": f'Service "{svc.name}" has no line items; remove it from service_item_selections',
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                continue
            if not chosen:
                return Response(
                    {
                        "error": f'Choose at least one line item for service "{svc.name}"',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            invalid = [i for i in chosen if i not in linked_ids]
            if invalid:
                return Response(
                    {
                        "error": f"Invalid line item id(s) {invalid} for service \"{svc.name}\"",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            normalized_selections.append({"service_id": svc.id, "item_ids": chosen})
        booking = Booking.objects.create(
            user_car=user_car,
            branch=branch,
            time=time,
            date=date,
            slot_index=slot_index,
            customer_note=customer_note,
            service_item_selections=normalized_selections,
            workflow_status=Booking.WORKFLOW_PENDING,
        )
        for service in services:
            booking.service.add(service)
        booking.save()
        serializer = BookAServiceSerializer(booking)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListTechnicalAssistant(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        assistant = TechnicalAssistant.objects.filter(user=request.user)
        serializer = TechnicalAssistantSerializer(assistant, many=True)

        return Response(response_message.success(serializer.data, "success"), status=status.HTTP_200_OK)


class CreateTechnicalAssistant(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = TechnicalAssistantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(response_message.success("submited successfully", "success"), status=status.HTTP_201_CREATED)


class CreateRoadAssistantRequest(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_car = UserCars.objects.filter(id=request.data.get('car')).first()
        serializer = RoadAssistantRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, car=user_car)
        return Response(response_message.success(serializer.data, "success"), status=status.HTTP_200_OK)


class RedeemPoints(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        service = Services.objects.filter(id=request.data.get('service_id')).first()
        print(service)
        if not service:
            return Response(
                response_message.error("error", ""),
                status=status.HTTP_400_BAD_REQUEST,
            )
        ut = getattr(request.user, "user_type", None)
        if ut is None or not getattr(ut, "type", None):
            return Response(
                response_message.error("error", ""),
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "prime" in request.user.user_type.type:
            points = int(service.price / 20)
        elif "plus" in request.user.user_type.type:
            points = int(service.price / 10)
        else:
            points = int(service.price / (int(100 / 15) + 1))
        user_point = request.user.mypoints
        print("user_point", user_point)
        print("points", points)
        if user_point < points:
            return Response(response_message.error("not_enough_point", ""), status=status.HTTP_400_BAD_REQUEST)
        elif user_point > points:
            print("bef",user_point)
            user_point = user_point - points
            print("aft", user_point)
            user = request.user
            user.mypoints = user_point
            user.save()
        else:
            user = request.user
            user.mypoints = 0
            user.save()
        print(str(datetime.datetime.today()).split(' ')[0])
        my_history = MyHistory.objects.create(user=request.user, date=str(datetime.datetime.today()).split(' ')[0],
                                              price=request.data.get('price'), using_points=True)
        my_history.service.add(service)
        serializer = MyHistorySerializer(my_history)
        return Response(response_message.success(serializer.data, "success"), status=status.HTTP_200_OK)
