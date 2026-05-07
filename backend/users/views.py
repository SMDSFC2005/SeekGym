from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol,
            "estado_gym": user.estado_gym,
            "is_superuser": user.is_superuser,
        })


class GymRequestListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
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


class GymRequestApproveView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, estado_gym="PENDIENTE")
        except User.DoesNotExist:
            return Response({"detail": "Solicitud no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        user.rol = User.Rol.GIMNASIO
        user.estado_gym = User.EstadoGym.APROBADO
        user.save(update_fields=["rol", "estado_gym"])
        return Response({"detail": "Aprobado."}, status=status.HTTP_200_OK)


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
