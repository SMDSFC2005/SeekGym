from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gyms.models import Gym, Province, Municipality
from gyms.serializers import (
    GymHomeSerializer,
    GymDetailSerializer,
    ProvinceSerializer,
    MunicipalitySerializer,
    PostalCodeOptionSerializer,
)
from gyms.services.occupancy import (
    build_home_gym_payload,
    build_gym_detail_payload,
)


class GymHomeView(APIView):
    def get(self, request, *args, **kwargs):
        province_id = request.query_params.get("province_id")
        municipality_id = request.query_params.get("municipality_id")
        postal_code = request.query_params.get("postal_code")

        gyms = Gym.objects.filter(is_active=True).select_related(
            "province",
            "municipality",
        ).order_by("name")

        if province_id:
            gyms = gyms.filter(province_id=province_id)

        if municipality_id:
            gyms = gyms.filter(municipality_id=municipality_id)

        if postal_code:
            gyms = gyms.filter(postal_code=postal_code.strip())

        results = [build_home_gym_payload(gym) for gym in gyms]

        serializer = GymHomeSerializer(results, many=True)

        return Response(
            {
                "filters": {
                    "province_id": province_id,
                    "municipality_id": municipality_id,
                    "postal_code": postal_code,
                },
                "count": len(serializer.data),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProvinceListView(APIView):
    def get(self, request, *args, **kwargs):
        provinces = Province.objects.order_by("name")
        data = [{"id": province.id, "name": province.name} for province in provinces]
        serializer = ProvinceSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MunicipalityListView(APIView):
    def get(self, request, *args, **kwargs):
        province_id = request.query_params.get("province_id")

        municipalities = Municipality.objects.all().order_by("name")

        if province_id:
            municipalities = municipalities.filter(province_id=province_id)

        data = [
            {
                "id": municipality.id,
                "name": municipality.name,
                "province_id": municipality.province_id,
            }
            for municipality in municipalities
        ]

        serializer = MunicipalitySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostalCodeListView(APIView):
    def get(self, request, *args, **kwargs):
        province_id = request.query_params.get("province_id")
        municipality_id = request.query_params.get("municipality_id")

        gyms = Gym.objects.filter(is_active=True)

        if province_id:
            gyms = gyms.filter(province_id=province_id)

        if municipality_id:
            gyms = gyms.filter(municipality_id=municipality_id)

        postal_codes = (
            gyms.values_list("postal_code", flat=True)
            .distinct()
            .order_by("postal_code")
        )

        data = [{"postal_code": postal_code} for postal_code in postal_codes]
        serializer = PostalCodeOptionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GymDetailView(APIView):
    def get(self, request, slug, *args, **kwargs):
        gym = get_object_or_404(
            Gym.objects.select_related("province", "municipality"),
            slug=slug,
            is_active=True,
        )

        payload = build_gym_detail_payload(gym)
        serializer = GymDetailSerializer(payload)

        return Response(serializer.data, status=status.HTTP_200_OK)