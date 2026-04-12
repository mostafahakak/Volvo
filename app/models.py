from django.db import models

from user.models import TimestampedModel, UserCars, CarModels, User, Branches, LoyaltyPoints


# Create your models here.


class BranchSlot(TimestampedModel):
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, blank=True, null=True)
    slot_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.branch.name + "--" + str(self.slot_number)


class Timing(TimestampedModel):
    time = models.TimeField(null=True, blank=True)
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.branch.name + "--" + str(self.time)


class Services(TimestampedModel):
    price = models.IntegerField(null=True, blank=True)
    min_price = models.IntegerField(null=True, blank=True)
    max_price = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    icons = models.ImageField(upload_to="services", null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)
    # If set, this service can only be booked at this branch (e.g. سمكرة و دهان — Katameya only).
    only_at_branch = models.ForeignKey(
        Branches,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exclusive_services",
    )
    line_items_ar = models.TextField(blank=True, null=True)
    price_note_ar = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Booking(TimestampedModel):
    WORKFLOW_PENDING = "pending_confirmation"
    WORKFLOW_CONFIRMED = "confirmed"
    WORKFLOW_IN_PROGRESS = "in_progress"
    WORKFLOW_COMPLETED = "completed"
    WORKFLOW_CANCELLED = "cancelled"
    WORKFLOW_CHOICES = (
        (WORKFLOW_PENDING, "Pending confirmation"),
        (WORKFLOW_CONFIRMED, "Confirmed"),
        (WORKFLOW_IN_PROGRESS, "In progress"),
        (WORKFLOW_COMPLETED, "Completed"),
        (WORKFLOW_CANCELLED, "Cancelled"),
    )

    user_car = models.ForeignKey(UserCars, on_delete=models.CASCADE, blank=True, null=True)
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, blank=True, null=True)
    service = models.ManyToManyField(Services, related_name="book_a_service", blank=True)
    time = models.ForeignKey(Timing, on_delete=models.CASCADE, blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    status = models.BooleanField(default=False)
    # 0, 1, or 2 — three concurrent bookings per hour slot (12:00–18:00 flow).
    slot_index = models.PositiveSmallIntegerField(default=0)
    workflow_status = models.CharField(
        max_length=32,
        choices=WORKFLOW_CHOICES,
        default=WORKFLOW_PENDING,
        db_index=True,
    )

    def __str__(self):
        u = self.user_car.user.mobile if self.user_car and self.user_car.user else ""
        b = self.branch.name if self.branch else ""
        return f"{u} {b}"


class Accessories(TimestampedModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    about = models.TextField(blank=True, null=True)
    compatible_with = models.ManyToManyField(CarModels, related_name="accessories")
    price = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class RoadAssistantRequest(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    car = models.ForeignKey(UserCars, on_delete=models.CASCADE)
    langtiude = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    valid = models.BooleanField(default=False)

    def __str__(self):
        return self.user.mobile + "" + self.car.car_model.car_model


class UsedCar(TimestampedModel):
    car_model = models.ForeignKey(CarModels, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.car_model.car_model

    class Meta:
        verbose_name_plural = "Used Cars"


class UsedCarsImage(TimestampedModel):
    used_car = models.ForeignKey(UsedCar, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to="used_car_image")

    def __str__(self):
        return self.used_car.car_model.car_model


class MaintenanceSchedule(TimestampedModel):
    description = models.ImageField('images', null=True, blank=True)


class MyHistory(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    price = models.IntegerField(null=True, blank=True)
    service = models.ManyToManyField(Services, related_name="myhistory")
    date = models.DateTimeField(null=True, blank=True)
    file = models.FileField(upload_to="my_history", null=True, blank=True)
    using_points = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def save(self, *args, **kwargs):
        if not self.using_points:
            type = self.user.user_type.type
            if "prime" in type:
                lol_point = LoyaltyPoints.objects.filter(type='Prime').first()
                points = int(self.price / lol_point.point_per_pound)
            elif "plus" in type:
                lol_point = LoyaltyPoints.objects.filter(type='Plus').first()
                points = int(self.price / lol_point.point_per_pound)
            else:
                lol_point = LoyaltyPoints.objects.filter(type='Elite').first()
                points = int(self.price / lol_point.point_per_pound)
            self.user.mypoints = self.user.mypoints + points
            self.user.history_points = self.user.history_points + points
            prime = LoyaltyPoints.objects.filter(type='Prime').first()
            plus = LoyaltyPoints.objects.filter(type='Plus').first()
            elite = LoyaltyPoints.objects.filter(type='Elite').first()
            print("self.user.mypoints",self.user.mypoints)
            if self.user.mypoints > prime.point and self.user.mypoints < plus.point:
                self.user.user_type = prime
            elif self.user.mypoints > plus.point and self.user.mypoints < elite.point:
                self.user.user_type = plus
            elif self.user.mypoints > elite.point:
                self.user.user_type = elite
            self.user.save()
        return super(MyHistory, self).save(*args, **kwargs)


class Notes(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def save(self, *args, **kwargs):
        from firebase_admin import messaging
        if self.user.notification_token:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=self.title,
                    body=self.message
                ),
                token=self.user.notification_token  # User's device token
            )

            response = messaging.send(message)
            print(response)
        return super(Notes, self).save(*args, **kwargs)


class BookUsedCars(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    used_cars = models.ForeignKey(UsedCar, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.user.mobile) + "--" + str(self.date)


class BookAccessories(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    accessories = models.ForeignKey(Accessories, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.user.mobile) + "--" + str(self.date)


class AboutUS(TimestampedModel):
    about = models.TextField(blank=True, null=True)


class FeedBack(TimestampedModel):
    fullname = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    feedback_subject = models.CharField(max_length=255, blank=True, null=True)
    car_model = models.ForeignKey(CarModels, on_delete=models.CASCADE, blank=True, null=True)
    feedback_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fullname


class ContactUS(TimestampedModel):
    fullname = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    car_model = models.ForeignKey(CarModels, on_delete=models.CASCADE, blank=True, null=True)
    inquiry_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.fullname


class TechnicalAssistant(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    question = models.CharField(max_length=1000, blank=True, null=True)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + "  " + self.user.last_name


class SiteContactSettings(TimestampedModel):
    """
    Singleton row (pk=1) for hotline / WhatsApp / winch numbers editable from admin dashboard.
    Mobile app can read via public GET /api/site_contact_settings.
    """

    whatsapp_e164 = models.CharField(max_length=32, blank=True, default="")
    tech_hotline_e164 = models.CharField(max_length=32, blank=True, default="")
    winch_primary = models.CharField(max_length=64, blank=True, default="")
    winch_secondary = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        verbose_name = "Site contact settings"
        verbose_name_plural = "Site contact settings"

    def __str__(self):
        return "Site contact settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
