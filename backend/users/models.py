from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        GIMNASIO = "GIMNASIO", "Gimnasio"

    class EstadoGym(models.TextChoices):
        NONE = "NONE", "Sin solicitud"
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.NORMAL
    )

    estado_gym = models.CharField(
        max_length=20,
        choices=EstadoGym.choices,
        default=EstadoGym.NONE
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuario"