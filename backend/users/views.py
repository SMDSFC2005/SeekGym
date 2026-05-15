from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer

User = get_user_model()


# registro abierto a cualquiera, sin autenticación
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# devuelve los datos del usuario que está logueado ahora mismo
class MeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # si tiene foto pillamos la URL absoluta, si no pues None
        photo_url = None
        if user.profile_photo:
            photo_url = request.build_absolute_uri(user.profile_photo.url)
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol,
            "estado_gym": user.estado_gym,
            "is_superuser": user.is_superuser,
            "profile_photo_url": photo_url,
        })


# para subir o cambiar la foto de perfil
class ProfilePhotoUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        image = request.FILES.get("photo")
        if not image:
            return Response({"detail": "No se proporcionó imagen."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        # si ya tenía foto la borramos antes de guardar la nueva
        if user.profile_photo:
            user.profile_photo.delete(save=False)

        user.profile_photo = image
        user.save(update_fields=["profile_photo"])

        return Response(
            {"profile_photo_url": request.build_absolute_uri(user.profile_photo.url)},
            status=status.HTTP_200_OK,
        )


# solo el admin puede ver las solicitudes pendientes de gym
class GymRequestListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # pillamos todos los usuarios con solicitud pendiente, ordenados por fecha
        pending = User.objects.filter(estado_gym="PENDIENTE").order_by("creado_en")
        data = [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "creado_en": u.creado_en,
            }
            for u in pending
        ]
        return Response(data, status=status.HTTP_200_OK)


# el admin aprueba a un usuario como dueño de gym
class GymRequestApproveView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, estado_gym="PENDIENTE")
        except User.DoesNotExist:
            return Response({"detail": "Solicitud no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # le damos el rol de GIMNASIO y marcamos como aprobado
        user.rol = User.Rol.GIMNASIO
        user.estado_gym = User.EstadoGym.APROBADO
        user.save(update_fields=["rol", "estado_gym"])
        return Response({"detail": "Aprobado."}, status=status.HTTP_200_OK)


# el admin rechaza la solicitud y el usuario se queda como NORMAL
class GymRequestRejectView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, estado_gym="PENDIENTE")
        except User.DoesNotExist:
            return Response({"detail": "Solicitud no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        user.estado_gym = User.EstadoGym.RECHAZADO
        user.save(update_fields=["estado_gym"])
        return Response({"detail": "Rechazado."}, status=status.HTTP_200_OK)
