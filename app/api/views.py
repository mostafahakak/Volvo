from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import app.messages as response_message
from app.models import MyHistory, MaintenanceSchedule, Branches, BranchSlot, Services, Accessories, UsedCarsImage, \
    UsedCar, AboutUS, Timing, Booking, TechnicalAssistant
from app.serializers import *
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
        maintenace = MaintenanceSchedule.objects.all()
        serializer = MaintenanceScheduleSerializer(maintenace, many=True)
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


class ListUserCars(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cars = UserCars.objects.filter(user=request.user)
        serializer = UserCarsSerializer(cars, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListBranches(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        branch = Branches.objects.all()
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
        service = Services.objects.all()
        serializer = ServicesSerializer(service, many=True)
        return Response(response_message.success(serializer.data, success_key="success"), status=status.HTTP_200_OK)


class ListAccessories(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        accessory = Accessories.objects.filter(discount=0)
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
        accessory = Accessories.objects.filter(~Q(discount=0))
        serializer = AccessoriesSerializer(accessory, many=True)
        data = []
        for access in serializer.data:
            access['price_after'] = access.get("price") - (access.get("price") * (access.get("discount") / 100))
            data.append(access)
        return Response(response_message.success(data, success_key="success"), status=status.HTTP_200_OK)


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
        branch = Branches.objects.filter(id=request.query_params.get('branch_id')).first()
        slots = BranchSlot.objects.filter(branch=branch)
        timing = Timing.objects.filter(branch=branch)
        booked = Booking.objects.filter(branch=branch, time__in=timing, date=request.query_params.get("date"),
                                        status=False)
        serializer = TimingSerializer(timing, many=True).data
        data = []
        if booked:
            for book in serializer:
                count = 0
                for b in booked:
                    if b.time.id == book.get('id'):
                        count += 1
                if count == slots.count():
                    book['available'] = False
                else:
                    book['available'] = True
                data.append(book)
        else:
            for book in serializer:
                book['available'] = True
                data.append(book)
        return Response(response_message.success(data, success_key="success"), status=status.HTTP_200_OK)


class BookAService(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        services = Services.objects.filter(id__in=request.data.get("services"))
        time = Timing.objects.filter(id=request.data.get("time_id")).first()
        user_car = UserCars.objects.filter(id=request.data.get("user_car")).first()
        branch = Branches.objects.filter(id=request.data.get("branch_id")).first()
        date = request.data.get("date")
        booking = Booking.objects.create(user_car=user_car, branch=branch, time=time, date=date)
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
