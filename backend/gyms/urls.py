from django.urls import path

from gyms.views import (
    GymAnnouncementCreateView,
    GymCreateView,
    GymDetailView,
    GymFollowView,
    GymHomeView,
    GymImageUploadView,
    GymUpdateView,
    FollowedGymsView,
    MunicipalityListView,
    MyGymView,
    NotificationsView,
    PostalCodeListView,
    ProvinceListView,
)

urlpatterns = [
    path("home/", GymHomeView.as_view(), name="gyms-home"),
    path("my-gym/", MyGymView.as_view(), name="gyms-my-gym"),
    path("create/", GymCreateView.as_view(), name="gyms-create"),
    path("seguidos/", FollowedGymsView.as_view(), name="gyms-followed"),
    path("notifications/", NotificationsView.as_view(), name="gyms-notifications"),

    path("filters/provinces/", ProvinceListView.as_view(), name="provinces-list"),
    path("filters/municipalities/", MunicipalityListView.as_view(), name="municipalities-list"),
    path("filters/postal-codes/", PostalCodeListView.as_view(), name="postal-codes-list"),

    path("<slug:slug>/", GymDetailView.as_view(), name="gyms-detail"),
    path("<slug:slug>/manage/", GymUpdateView.as_view(), name="gyms-update"),
    path("<slug:slug>/upload-image/", GymImageUploadView.as_view(), name="gym-upload-image"),
    path("<slug:slug>/follow/", GymFollowView.as_view(), name="gyms-follow"),
    path("<slug:slug>/announcements/", GymAnnouncementCreateView.as_view(), name="gyms-announcement-create"),
]