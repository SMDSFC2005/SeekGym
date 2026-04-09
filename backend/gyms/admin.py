from django.contrib import admin

from .models import Gym, GymAnnouncement, GymOccupancyProfile, Province, Municipality


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "province", "slug")
    list_filter = ("province",)
    search_fields = ("name", "slug", "province__name")


class GymAnnouncementInline(admin.TabularInline):
    model = GymAnnouncement
    extra = 0


@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "municipality",
        "province",
        "postal_code",
        "price_per_month",
        "rating",
        "is_active",
    )
    search_fields = (
        "name",
        "owner__username",
        "address",
        "postal_code",
        "municipality__name",
        "province__name",
    )
    list_filter = ("province", "municipality", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [GymAnnouncementInline]


@admin.register(GymAnnouncement)
class GymAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "gym", "kind", "title", "is_active", "created_at")
    list_filter = ("kind", "is_active", "gym")
    search_fields = ("title", "content", "gym__name")


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