from django.urls import path

from gyms.views import (
    GymAnnouncementCreateView,
    GymCreateView,
    GymDetailView,
    GymHomeView,
    GymUpdateView,
    MunicipalityListView,
    MyGymView,
    PostalCodeListView,
    ProvinceListView,
)

urlpatterns = [
    path("home/", GymHomeView.as_view(), name="gyms-home"),
    path("my-gym/", MyGymView.as_view(), name="gyms-my-gym"),
    path("create/", GymCreateView.as_view(), name="gyms-create"),

    path("filters/provinces/", ProvinceListView.as_view(), name="provinces-list"),
    path("filters/municipalities/", MunicipalityListView.as_view(), name="municipalities-list"),
    path("filters/postal-codes/", PostalCodeListView.as_view(), name="postal-codes-list"),

    path("<slug:slug>/", GymDetailView.as_view(), name="gyms-detail"),
    path("<slug:slug>/manage/", GymUpdateView.as_view(), name="gyms-update"),
    path("<slug:slug>/announcements/", GymAnnouncementCreateView.as_view(), name="gyms-announcement-create"),
]