from django.utils.text import slugify
from rest_framework import serializers

from gyms.models import Gym, GymAnnouncement, GymFollower, GymSchedule, Municipality, Province
from gyms.services.occupancy import (
    get_best_time_today,
    get_best_time_tomorrow,
    get_current_occupancy_data,
    get_today_timeline,
)


def build_unique_slug(model_class, value, instance_id=None):
    base_slug = slugify(value)
    slug = base_slug
    counter = 2

    queryset = model_class.objects.all()
    if instance_id:
        queryset = queryset.exclude(id=instance_id)

    while queryset.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# ---------------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------------

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ("id", "name")


class MunicipalitySerializer(serializers.ModelSerializer):
    province_id = serializers.IntegerField(source="province.id", read_only=True)

    class Meta:
        model = Municipality
        fields = ("id", "name", "province_id")


class PostalCodeOptionSerializer(serializers.Serializer):
    postal_code = serializers.CharField()


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------

class GymAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymAnnouncement
        fields = ("id", "kind", "title", "content", "created_at")


class GymAnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymAnnouncement
        fields = ("kind", "title", "content")

    def create(self, validated_data):
        gym = self.context["gym"]
        return GymAnnouncement.objects.create(gym=gym, **validated_data)


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

class GymScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymSchedule
        fields = ("day_type", "opening_hour", "closing_hour", "is_closed")


class GymScheduleWriteSerializer(serializers.Serializer):
    day_type = serializers.ChoiceField(choices=GymSchedule.DayType.choices)
    opening_hour = serializers.IntegerField(min_value=0, max_value=23, default=7)
    closing_hour = serializers.IntegerField(min_value=1, max_value=24, default=22)
    is_closed = serializers.BooleanField(default=False)

    def validate(self, attrs):
        if not attrs.get("is_closed") and attrs["closing_hour"] <= attrs["opening_hour"]:
            raise serializers.ValidationError(
                "La hora de cierre debe ser posterior a la de apertura."
            )
        return attrs


# ---------------------------------------------------------------------------
# Gym — read
# ---------------------------------------------------------------------------

class GymBaseReadSerializer(serializers.ModelSerializer):
    province_id = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    municipality_id = serializers.SerializerMethodField()
    municipality = serializers.SerializerMethodField()

    current_occupancy = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()
    confidence = serializers.SerializerMethodField()
    best_time_today = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Gym
        fields = (
            "id",
            "name",
            "slug",
            "province_id",
            "province",
            "municipality_id",
            "municipality",
            "postal_code",
            "address",
            "description",
            "price_per_month",
            "rating",
            "reviews_count",
            "image_url",
            "current_occupancy",
            "current_status",
            "confidence",
            "best_time_today",
            "is_following",
        )

    def _get_current_data(self, obj):
        if not hasattr(obj, "_cached_current_data"):
            obj._cached_current_data = get_current_occupancy_data(obj)
        return obj._cached_current_data

    def _get_best_time_data(self, obj):
        if not hasattr(obj, "_cached_best_time_data"):
            obj._cached_best_time_data = get_best_time_today(obj)
        return obj._cached_best_time_data

    def get_province_id(self, obj):
        return obj.province_id

    def get_province(self, obj):
        return obj.province.name if obj.province else None

    def get_municipality_id(self, obj):
        return obj.municipality_id

    def get_municipality(self, obj):
        return obj.municipality.name if obj.municipality else None

    def get_current_occupancy(self, obj):
        return self._get_current_data(obj)["current_occupancy"]

    def get_current_status(self, obj):
        return self._get_current_data(obj)["current_status"]

    def get_confidence(self, obj):
        return self._get_current_data(obj)["confidence"]

    def get_best_time_today(self, obj):
        return self._get_best_time_data(obj)

    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return GymFollower.objects.filter(user=request.user, gym=obj).exists()


class GymHomeSerializer(GymBaseReadSerializer):
    pass


class GymDetailSerializer(GymBaseReadSerializer):
    today_timeline = serializers.SerializerMethodField()
    best_time_tomorrow = serializers.SerializerMethodField()
    announcements = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)

    class Meta(GymBaseReadSerializer.Meta):
        fields = GymBaseReadSerializer.Meta.fields + (
            "today_timeline",
            "best_time_tomorrow",
            "announcements",
            "schedule",
            "owner_id",
        )

    def get_today_timeline(self, obj):
        return get_today_timeline(obj)

    def get_best_time_tomorrow(self, obj):
        if not hasattr(obj, "_cached_best_time_tomorrow"):
            obj._cached_best_time_tomorrow = get_best_time_tomorrow(obj)
        return obj._cached_best_time_tomorrow

    def get_announcements(self, obj):
        announcements = obj.announcements.filter(is_active=True).order_by("-created_at")
        return GymAnnouncementSerializer(announcements, many=True).data

    def get_schedule(self, obj):
        DAY_ORDER = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN", "HOL"]
        schedules = {s.day_type: s for s in obj.schedules.all()}
        ordered = [schedules[d] for d in DAY_ORDER if d in schedules]
        return GymScheduleSerializer(ordered, many=True).data


# ---------------------------------------------------------------------------
# Gym — write
# ---------------------------------------------------------------------------

class GymCreateUpdateSerializer(serializers.ModelSerializer):
    province_id = serializers.PrimaryKeyRelatedField(
        queryset=Province.objects.all(),
        source="province",
        write_only=True,
    )
    municipality_id = serializers.PrimaryKeyRelatedField(
        queryset=Municipality.objects.all(),
        source="municipality",
        write_only=True,
    )
    schedule = GymScheduleWriteSerializer(many=True, required=False)

    class Meta:
        model = Gym
        fields = (
            "name",
            "province_id",
            "municipality_id",
            "postal_code",
            "address",
            "description",
            "price_per_month",
            "image_url",
            "schedule",
        )

    def validate(self, attrs):
        province = attrs.get("province") or getattr(self.instance, "province", None)
        municipality = attrs.get("municipality") or getattr(self.instance, "municipality", None)

        if not province:
            raise serializers.ValidationError({"province_id": "La provincia es obligatoria."})

        if not municipality:
            raise serializers.ValidationError({"municipality_id": "El municipio es obligatorio."})

        if municipality.province_id != province.id:
            raise serializers.ValidationError({
                "municipality_id": "El municipio no pertenece a la provincia seleccionada."
            })

        return attrs

    def _save_schedule(self, gym, schedule_data):
        for entry in schedule_data:
            GymSchedule.objects.update_or_create(
                gym=gym,
                day_type=entry["day_type"],
                defaults={
                    "opening_hour": entry["opening_hour"],
                    "closing_hour": entry["closing_hour"],
                    "is_closed": entry.get("is_closed", False),
                },
            )

    def create(self, validated_data):
        schedule_data = validated_data.pop("schedule", [])
        request = self.context["request"]
        validated_data["owner"] = request.user
        validated_data["slug"] = build_unique_slug(Gym, validated_data["name"])
        gym = super().create(validated_data)
        self._save_schedule(gym, schedule_data)
        return gym

    def update(self, instance, validated_data):
        schedule_data = validated_data.pop("schedule", None)
        if "name" in validated_data and validated_data["name"] != instance.name:
            instance.slug = build_unique_slug(Gym, validated_data["name"], instance_id=instance.id)
        gym = super().update(instance, validated_data)
        if schedule_data is not None:
            self._save_schedule(gym, schedule_data)
        return gym
