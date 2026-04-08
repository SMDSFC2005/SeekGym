from django.urls import path
from gyms.views import (
    GymHomeView,
    GymDetailView,
    ProvinceListView,
    MunicipalityListView,
    PostalCodeListView,
)

urlpatterns = [
    path("home/", GymHomeView.as_view(), name="gyms-home"),
    path("filters/provinces/", ProvinceListView.as_view(), name="provinces-list"),
    path("filters/municipalities/", MunicipalityListView.as_view(), name="municipalities-list"),
    path("filters/postal-codes/", PostalCodeListView.as_view(), name="postal-codes-list"),
    path("<slug:slug>/", GymDetailView.as_view(), name="gyms-detail"),
]