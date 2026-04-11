from django.urls import path
from .views import *

urlpatterns = [
    path('signup', SignUp.as_view(), name='signup'),
    path('firebase_login', FirebasePhoneAuthView.as_view(), name='firebase_login'),
    path('login', LoginView.as_view(), name='login'),
    path('add_user_car', AddUserCar.as_view(), name='add_user_car'),
    path('profile', Profile.as_view(), name='profile'),
    path('update_profile', UpdateProfile.as_view(), name='update_profile'),
    path('loyalty_level', LoyaltyLevel.as_view(), name='loyalty_level'),
    path('change_password', ChangePassword.as_view(), name='change_password'),
]
