from django.urls import path
from gyms.views import GymHomeView, GymDetailView

urlpatterns = [
    path("home/", GymHomeView.as_view(), name="gyms-home"),
    path("<slug:slug>/", GymDetailView.as_view(), name="gyms-detail"),
]