from rest_framework import serializers


class GymHomeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    city = serializers.CharField()
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