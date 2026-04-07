from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from user.utils import upload_profile_picture


class TimestampedModel(models.Model):
    """
    Abstract model to contain information about creation/update time.

    :created_at: date and time of record creation.
    :updated_at: date and time of any update happends for the record.
    """

    created_at = models.DateTimeField(verbose_name="وقت الانشاء", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Update Date/Time", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]


class LoyaltyPoints(TimestampedModel):
    type = models.CharField(max_length=255, blank=True, null=True)
    point = models.IntegerField(blank=True, null=True)
    point_per_pound = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.type + "--" + str(self.point)


class Branches(TimestampedModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    mobile1 = models.IntegerField(null=True, blank=True)
    mobile2 = models.IntegerField(null=True, blank=True)
    latitude = models.CharField(max_length=255)
    langitude = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True, unique=True)
    email = models.EmailField(
        _("email address"),
        max_length=125,
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    mobile = models.CharField(_("mobile"), max_length=20, null=True, blank=True, unique=True)
    avatar = models.FileField(
        _("avatar"), null=True, blank=True, upload_to=upload_profile_picture
    )
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, blank=True, null=True)
    mypoints = models.IntegerField(default=20)
    history_points = models.IntegerField(default=20)
    user_type = models.ForeignKey(LoyaltyPoints, blank=True, null=True, on_delete=models.CASCADE)
    notification_token = models.CharField(max_length=10000, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "mobile"

    class Meta:
        ordering = ["-id"]
        verbose_name = _("User")
        verbose_name_plural = _("User")

    def __str__(self):
        return self.email


class CarModels(TimestampedModel):
    car_model = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to="Users Cars")

    def __str__(self):
        return self.car_model


class UserCars(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    car_model = models.ForeignKey(CarModels, on_delete=models.CASCADE, null=True, blank=True)
    model_year = models.IntegerField(blank=True, null=True)
    chassis_number = models.CharField(max_length=255, blank=True, null=True)
    plate_number = models.CharField(max_length=255, blank=True, null=True)
    car_document_front = models.ImageField(null=True, blank=True, upload_to="Car Document")
    car_document_back = models.ImageField(null=True, blank=True, upload_to="Car Document")
    # Firebase Storage (or CDN) URLs — optional when using remote uploads instead of ImageField.
    car_registration_front_url = models.URLField(max_length=2048, blank=True, null=True)
    car_registration_back_url = models.URLField(max_length=2048, blank=True, null=True)
    driver_license_front_url = models.URLField(max_length=2048, blank=True, null=True)
    driver_license_back_url = models.URLField(max_length=2048, blank=True, null=True)

    def __str__(self):
        return self.user.first_name + "-" + self.user.last_name + "-" + self.car_model.car_model


class UserRequests(TimestampedModel):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + "  " + self.user.last_name
