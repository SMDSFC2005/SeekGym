from django.contrib import admin
from .models import Gym, GymOccupancyProfile


@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "postal_code",
        "price_per_month",
        "rating",
        "is_active",
    )
    search_fields = ("name", "city", "postal_code")
    list_filter = ("city", "postal_code", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(GymOccupancyProfile)
class GymOccupancyProfileAdmin(admin.ModelAdmin):
    list_display = (
        "gym",
        "day_of_week",
        "hour",
        "zone",
        "occupancy_percent",
        "confidence",
    )
    list_filter = ("day_of_week", "zone", "gym")
    search_fields = ("gym__name",)