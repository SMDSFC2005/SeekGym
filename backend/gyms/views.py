from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils import timezone

from gyms.models import Gym, GymAnnouncement, GymFollower, Municipality, Province
from gyms.permissions import CanManageGym, IsGymApprovedOrSuperuser
from gyms.services.profile_seed import seed_gym_occupancy_profiles
from gyms.serializers import (
    GymAnnouncementCreateSerializer,
    GymCreateUpdateSerializer,
    GymDetailSerializer,
    GymHomeSerializer,
    MunicipalitySerializer,
    PostalCodeOptionSerializer,
    ProvinceSerializer,
)


# listado de gyms para la home, acepta filtros de provincia, municipio y búsqueda
class GymHomeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        province_id = request.query_params.get("province_id")
        municipality_id = request.query_params.get("municipality_id")
        search = request.query_params.get("search", "").strip()

        # pillamos solo gyms activos con sus relaciones para no matar la BBDD
        gyms = Gym.objects.filter(is_active=True).select_related(
            "province",
            "municipality",
        ).prefetch_related("announcements").order_by("name")

        if province_id:
            gyms = gyms.filter(province_id=province_id)

        if municipality_id:
            gyms = gyms.filter(municipality_id=municipality_id)

        # búsqueda por nombre, sin distinguir mayúsculas
        if search:
            gyms = gyms.filter(name__icontains=search)

        serializer = GymHomeSerializer(gyms, many=True, context={"request": request})

        return Response(
            {
                "filters": {
                    "province_id": province_id,
                    "municipality_id": municipality_id,
                    "search": search,
                },
                "count": len(serializer.data),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# devuelve todas las provincias para los filtros del front
class ProvinceListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        provinces = Province.objects.order_by("name")
        serializer = ProvinceSerializer(provinces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# devuelve municipios, opcionalmente filtrados por provincia
class MunicipalityListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        province_id = request.query_params.get("province_id")

        municipalities = Municipality.objects.all().order_by("name")

        if province_id:
            municipalities = municipalities.filter(province_id=province_id)

        serializer = MunicipalitySerializer(municipalities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# códigos postales únicos de los gyms activos, para el filtro del front
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


# detalle completo de un gym por su slug, incluye horario, anuncios y ocupación
class GymDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug, *args, **kwargs):
        # pillamos el gym por su slug, si no existe pues 404
        gym = get_object_or_404(
            Gym.objects.select_related("province", "municipality", "owner").prefetch_related("announcements", "schedules", "followers"),
            slug=slug,
            is_active=True,
        )
        serializer = GymDetailSerializer(gym, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# para que el dueño vea su propio gym
class MyGymView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        gym = Gym.objects.select_related("province", "municipality").filter(owner=request.user).first()

        # si no tiene gym todavía, devolvemos exists: false para que el front lo sepa
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


# crea un gym nuevo, solo usuarios aprobados pueden hacer esto
class GymCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsGymApprovedOrSuperuser]

    def post(self, request, *args, **kwargs):
        # un usuario normal solo puede tener un gym, el superuser puede crear más
        if not request.user.is_superuser and Gym.objects.filter(owner=request.user).exists():
            return Response(
                {"detail": "Ya tienes un gimnasio creado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = GymCreateUpdateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        gym = serializer.save()

        # generamos los perfiles de ocupación automáticamente al crear el gym
        seed_gym_occupancy_profiles(gym)

        response_serializer = GymDetailSerializer(gym)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# actualizar o borrar un gym existente, solo el dueño o el admin
class GymUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsGymApprovedOrSuperuser, CanManageGym]

    def patch(self, request, slug, *args, **kwargs):
        gym = get_object_or_404(
            Gym.objects.select_related("province", "municipality", "owner"),
            slug=slug,
        )
        # comprobamos que el que edita es el dueño del gym
        self.check_object_permissions(request, gym)

        serializer = GymCreateUpdateSerializer(
            gym,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        gym = serializer.save()

        response_serializer = GymDetailSerializer(gym, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slug, *args, **kwargs):
        gym = get_object_or_404(
            Gym.objects.select_related("owner"),
            slug=slug,
        )
        self.check_object_permissions(request, gym)
        gym.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# el dueño publica un anuncio en su gym (promo, oferta o novedad)
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


# devuelve los gyms que sigue el usuario logueado
class FollowedGymsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # primero pillamos los IDs de los gyms que sigue y luego los gyms activos de esos IDs
        followed_ids = GymFollower.objects.filter(user=request.user).values_list("gym_id", flat=True)
        gyms = (
            Gym.objects.filter(id__in=followed_ids, is_active=True)
            .select_related("province", "municipality")
            .prefetch_related("announcements")
            .order_by("name")
        )
        serializer = GymHomeSerializer(gyms, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# toggle para seguir o dejar de seguir un gym
class GymFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, *args, **kwargs):
        gym = get_object_or_404(Gym, slug=slug, is_active=True)
        # si ya existe el follow lo borramos (dejar de seguir), si no lo creamos
        follower, created = GymFollower.objects.get_or_create(user=request.user, gym=gym)

        if not created:
            follower.delete()
            return Response({"following": False}, status=status.HTTP_200_OK)

        return Response({"following": True}, status=status.HTTP_201_CREATED)


# notificaciones: el admin ve solicitudes pendientes, los usuarios ven anuncios nuevos de sus gyms seguidos
class NotificationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # para el admin mostramos cuántas solicitudes de gym están pendientes
        if user.is_superuser:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            count = User.objects.filter(estado_gym="PENDIENTE").count()
            return Response({"pending_requests": count, "unread_announcements": []})

        followed = GymFollower.objects.filter(user=user).select_related("gym")
        items = []
        for f in followed:
            # pillamos los anuncios más recientes que el usuario aún no ha visto
            announcements = GymAnnouncement.objects.filter(
                gym=f.gym,
                is_active=True,
                created_at__gt=f.last_read_at,
            ).order_by("-created_at")[:5]
            for a in announcements:
                items.append({
                    "gym_name": f.gym.name,
                    "gym_slug": f.gym.slug,
                    "title": a.title,
                    "kind": a.kind,
                    "created_at": a.created_at,
                })

        # ordenamos todos los anuncios por fecha, los más nuevos primero
        items.sort(key=lambda x: x["created_at"], reverse=True)

        return Response({
            "pending_requests": 0,
            "unread_announcements": items[:10],
        })

    # marcar todas las notificaciones como leídas
    def post(self, request):
        GymFollower.objects.filter(user=request.user).update(last_read_at=timezone.now())
        return Response({"ok": True})


# para subir o cambiar la imagen de portada del gym
class GymImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsGymApprovedOrSuperuser, CanManageGym]
    parser_classes = [MultiPartParser]

    def post(self, request, slug, *args, **kwargs):
        gym = get_object_or_404(Gym, slug=slug)
        self.check_object_permissions(request, gym)

        image = request.FILES.get("image")
        if not image:
            return Response({"detail": "No se proporcionó imagen."}, status=status.HTTP_400_BAD_REQUEST)

        # si ya tenía imagen la borramos antes de poner la nueva
        if gym.image:
            gym.image.delete(save=False)

        gym.image = image
        gym.save(update_fields=["image"])

        return Response(
            {"image_url": request.build_absolute_uri(gym.image.url)},
            status=status.HTTP_200_OK,
        )