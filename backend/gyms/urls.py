from django.urls import path
from gyms.views import GymHomeView

urlpatterns = [
    path("home/", GymHomeView.as_view(), name="gyms-home"),
]