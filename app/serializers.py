from rest_framework import serializers

from app.models import MaintenanceSchedule, MyHistory, Branches, BranchSlot, Services, Accessories, UsedCar, \
    UsedCarsImage, BookUsedCars, BookAccessories, AboutUS, FeedBack, ContactUS, Timing, Booking, TechnicalAssistant, \
    RoadAssistantRequest
from user.models import CarModels, UserCars


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = "__all__"


class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModels
        fields = "__all__"


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceSchedule
        fields = "__all__"


class MyHistorySerializer(serializers.ModelSerializer):
    service = ServicesSerializer(required=False, many=True)

    class Meta:
        model = MyHistory
        fields = "__all__"


class UserCarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCars
        fields = "__all__"


class BranchesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branches
        fields = "__all__"


class BranchSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchSlot
        fields = "__all__"


class TimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timing
        fields = "__all__"


class AccessoriesSerializer(serializers.ModelSerializer):
    compatible_with = CarModelSerializer(required=False, many=True)

    class Meta:
        model = Accessories
        fields = "__all__"


class UsedCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedCar
        fields = "__all__"


class UsedCarsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsedCarsImage
        fields = "__all__"


class BookUsedCarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookUsedCars
        fields = "__all__"


class BookAccessoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookAccessories
        fields = "__all__"


class AboutUsSerializers(serializers.ModelSerializer):
    class Meta:
        model = AboutUS
        fields = "__all__"


class FeedBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        fields = "__all__"


class ContactUSSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUS
        fields = "__all__"


class BookAServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"


class TechnicalAssistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalAssistant
        fields = "__all__"


class RoadAssistantRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadAssistantRequest
        fields = "__all__"
