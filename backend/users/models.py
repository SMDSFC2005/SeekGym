from django.contrib.auth.models import AbstractUser
from django.db import models


# modelo de usuario personalizado, extiende el de Django
class Usuario(AbstractUser):
    # los roles posibles: usuario normal o dueño de gym
    class Rol(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        GIMNASIO = "GIMNASIO", "Gimnasio"

    # estado de la solicitud para ser dueño de gym
    class EstadoGym(models.TextChoices):
        NONE = "NONE", "Sin solicitud"
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    # por defecto todo el mundo es usuario normal
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.NORMAL
    )

    # esto va cambiando según el admin apruebe o rechace la solicitud de gym
    estado_gym = models.CharField(
        max_length=20,
        choices=EstadoGym.choices,
        default=EstadoGym.NONE
    )

    # foto de perfil opcional, se guarda en la carpeta profiles/
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuario"