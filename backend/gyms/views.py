from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gyms.models import Gym
from gyms.serializers import GymHomeSerializer
from gyms.services.occupancy import build_home_gym_payload


class GymHomeView(APIView):
    def get(self, request, *args, **kwargs):
        city = request.query_params.get("city")
        postal_code = request.query_params.get("postal_code")

        gyms = Gym.objects.filter(is_active=True).order_by("name")

        if city:
            gyms = gyms.filter(city__iexact=city.strip())

        if postal_code:
            gyms = gyms.filter(postal_code=postal_code.strip())

        results = [build_home_gym_payload(gym) for gym in gyms]

        serializer = GymHomeSerializer(results, many=True)

        return Response(
            {
                "filters": {
                    "city": city,
                    "postal_code": postal_code,
                },
                "count": len(serializer.data),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )