from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework import serializers

from gyms.models import Gym, GymAnnouncement, Municipality, Province
from gyms.services.occupancy import (
    get_best_time_today,
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


class GymAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymAnnouncement
        fields = (
            "id",
            "kind",
            "title",
            "content",
            "created_at",
        )


class GymAnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymAnnouncement
        fields = ("kind", "title", "content")

    def create(self, validated_data):
        gym = self.context["gym"]
        return GymAnnouncement.objects.create(gym=gym, **validated_data)


class GymBaseReadSerializer(serializers.ModelSerializer):
    province_id = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    municipality_id = serializers.SerializerMethodField()
    municipality = serializers.SerializerMethodField()

    current_occupancy = serializers.SerializerMethodField()
    current_status = serializers.SerializerMethodField()
    confidence = serializers.SerializerMethodField()
    best_time_today = serializers.SerializerMethodField()

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


class GymHomeSerializer(GymBaseReadSerializer):
    pass


class GymDetailSerializer(GymBaseReadSerializer):
    today_timeline = serializers.SerializerMethodField()
    announcements = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)

    class Meta(GymBaseReadSerializer.Meta):
        fields = GymBaseReadSerializer.Meta.fields + (
            "today_timeline",
            "announcements",
            "owner_id",
        )

    def get_today_timeline(self, obj):
        return get_today_timeline(obj)

    def get_announcements(self, obj):
        announcements = obj.announcements.filter(is_active=True).order_by("-created_at")
        return GymAnnouncementSerializer(announcements, many=True).data


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

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["owner"] = request.user
        validated_data["slug"] = build_unique_slug(Gym, validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "name" in validated_data and validated_data["name"] != instance.name:
            instance.slug = build_unique_slug(Gym, validated_data["name"], instance_id=instance.id)

        return super().update(instance, validated_data)