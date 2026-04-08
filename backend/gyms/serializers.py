from rest_framework import serializers


class GymHomeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()

    province_id = serializers.IntegerField(allow_null=True)
    province = serializers.CharField(allow_null=True)
    municipality_id = serializers.IntegerField(allow_null=True)
    municipality = serializers.CharField(allow_null=True)

    postal_code = serializers.CharField()
    address = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    price_per_month = serializers.CharField()
    rating = serializers.CharField()
    reviews_count = serializers.IntegerField()
    image_url = serializers.CharField(allow_blank=True)

    current_occupancy = serializers.IntegerField(allow_null=True)
    current_status = serializers.CharField(allow_null=True)
    confidence = serializers.IntegerField(allow_null=True)

    best_time_today = serializers.DictField(allow_null=True)


class GymTimelineHourSerializer(serializers.Serializer):
    hour = serializers.IntegerField()
    label = serializers.CharField()
    occupancy_percent = serializers.IntegerField(allow_null=True)
    status = serializers.CharField(allow_null=True)
    confidence = serializers.IntegerField(allow_null=True)


class BestTimeSerializer(serializers.Serializer):
    hour = serializers.IntegerField()
    label = serializers.CharField()
    occupancy_percent = serializers.IntegerField(allow_null=True)
    confidence = serializers.IntegerField(allow_null=True)


class GymDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()

    province_id = serializers.IntegerField(allow_null=True)
    province = serializers.CharField(allow_null=True)
    municipality_id = serializers.IntegerField(allow_null=True)
    municipality = serializers.CharField(allow_null=True)

    postal_code = serializers.CharField()
    address = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    price_per_month = serializers.CharField()
    rating = serializers.CharField()
    reviews_count = serializers.IntegerField()
    image_url = serializers.CharField(allow_blank=True)

    current_occupancy = serializers.IntegerField(allow_null=True)
    current_status = serializers.CharField(allow_null=True)
    confidence = serializers.IntegerField(allow_null=True)

    best_time_today = BestTimeSerializer(allow_null=True)
    today_timeline = GymTimelineHourSerializer(many=True)


class ProvinceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class MunicipalitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    province_id = serializers.IntegerField()


class PostalCodeOptionSerializer(serializers.Serializer):
    postal_code = serializers.CharField()