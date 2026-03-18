from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        GIMNASIO = "GIMNASIO", "Gimnasio"
        ADMIN = "ADMIN", "Admin"

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.NORMAL
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuario"