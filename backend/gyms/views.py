from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from gyms.models import Gym, Municipality, Province
from gyms.permissions import CanManageGym, IsGymApprovedOrSuperuser
from gyms.serializers import (
    GymAnnouncementCreateSerializer,
    GymCreateUpdateSerializer,
    GymDetailSerializer,
    GymHomeSerializer,
    MunicipalitySerializer,
    PostalCodeOptionSerializer,
    ProvinceSerializer,
)


class GymHomeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        province_id = request.query_params.get("province_id")
        municipality_id = request.query_params.get("municipality_id")
        postal_code = request.query_params.get("postal_code")

        gyms = Gym.objects.filter(is_active=True).select_related(
            "province",
            "municipality",
        ).prefetch_related("announcements").order_by("name")

        if province_id:
            gyms = gyms.filter(province_id=province_id)

        if municipality_id:
            gyms = gyms.filter(municipality_id=municipality_id)

        if postal_code:
            gyms = gyms.filter(postal_code=postal_code.strip())

        serializer = GymHomeSerializer(gyms, many=True)

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
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        provinces = Province.objects.order_by("name")
        serializer = ProvinceSerializer(provinces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MunicipalityListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        province_id = request.query_params.get("province_id")

        municipalities = Municipality.objects.all().order_by("name")

        if province_id:
            municipalities = municipalities.filter(province_id=province_id)

        serializer = MunicipalitySerializer(municipalities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostalCodeListView(APIView):
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug, *args, **kwargs):
        gym = get_object_or_404(
            Gym.objects.select_related("province", "municipality", "owner").prefetch_related("announcements"),
            slug=slug,
            is_active=True,
        )
        serializer = GymDetailSerializer(gym)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyGymView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        gym = Gym.objects.select_related("province", "municipality").filter(owner=request.user).first()

        if not gym:
            return Response(
                {
                    "exists": False,
                    "gym": None,
                },
                status=status.HTTP_200_OK,
            )

        serializer = GymDetailSerializer(gym)
        return Response(
            {
                "exists": True,
                "gym": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GymCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsGymApprovedOrSuperuser]

    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser and Gym.objects.filter(owner=request.user).exists():
            return Response(
                {"detail": "Ya tienes un gimnasio creado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = GymCreateUpdateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        gym = serializer.save()

        response_serializer = GymDetailSerializer(gym)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class GymUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsGymApprovedOrSuperuser, CanManageGym]

    def patch(self, request, slug, *args, **kwargs):
        gym = get_object_or_404(
            Gym.objects.select_related("province", "municipality", "owner"),
            slug=slug,
        )
        self.check_object_permissions(request, gym)

        serializer = GymCreateUpdateSerializer(
            gym,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        gym = serializer.save()

        response_serializer = GymDetailSerializer(gym)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class GymAnnouncementCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsGymApprovedOrSuperuser, CanManageGym]

    def post(self, request, slug, *args, **kwargs):
        gym = get_object_or_404(Gym, slug=slug)
        self.check_object_permissions(request, gym)

        serializer = GymAnnouncementCreateSerializer(
            data=request.data,
            context={"gym": gym},
        )
        serializer.is_valid(raise_exception=True)
        announcement = serializer.save()

        return Response(
            {
                "id": announcement.id,
                "kind": announcement.kind,
                "title": announcement.title,
                "content": announcement.content,
                "created_at": announcement.created_at,
            },
            status=status.HTTP_201_CREATED,
        )