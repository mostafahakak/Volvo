from django.urls import path

from app.api.views import *

urlpatterns = [
    path("list_car_model", ListCarModel.as_view(), name="list_car_model"),
    path("maintenance_schedule", ListMaintenanceSchedule.as_view(), name="maintenance_schedule"),
    path("my_history", ListMyHistory.as_view(), name="my_history"),
    path("list_user_cars", ListUserCars.as_view(), name="list_user_cars"),
    path("list_branches", ListBranches.as_view(), name="list_branches"),
    path("list_branches_slot", ListBranchSlot.as_view(), name="list_branches_slot"),
    path("list_services", ListServices.as_view(), name="list_services"),
    path("list_accessories", ListAccessories.as_view(), name="list_accessories"),
    path("list_offers", ListOffers.as_view(), name="list_offers"),
    path("list_used_cars", ListUsedCars.as_view(), name="list_used_cars"),
    path("book_used_cars", BookUsedCarsRequest.as_view(), name="book_used_cars"),
    path("book_accessories", BookAccessoriesRequest.as_view(), name="book_accessories"),
    path("list_aboutus", ListAboutUs.as_view(), name="list_aboutus"),
    path("feedback", CreateFeedBack.as_view(), name="feedback"),
    path("contact_us", CreateContactUS.as_view(), name="contact_us"),
    path("list_available_times", ListTimeToBookService.as_view(), name="list_available_times"),
    path("create_technical_assistant", CreateTechnicalAssistant.as_view(), name="create_technical_assistant"),
    path("list_technical_assistant", ListTechnicalAssistant.as_view(), name="list_technical_assistant"),
    path("road_help", CreateRoadAssistantRequest.as_view(), name="road_help"),
    path("book_a_service", BookAService.as_view(), name="book_a_service"),
    path("redeem_points", RedeemPoints.as_view(), name="redeem_points"),

]
