from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


# modelo para las provincias de España
class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# municipios vinculados a una provincia
class Municipality(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="municipalities"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        unique_together = ("province", "slug")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.province.name})"


# el modelo principal del gym, con toda la info
class Gym(models.Model):
    # si el dueño se borra, el gym se queda sin dueño (SET_NULL) pero no desaparece
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_gyms",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name="gyms",
        null=True,
        blank=True,
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.PROTECT,
        related_name="gyms",
        null=True,
        blank=True,
    )

    postal_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    price_per_month = models.DecimalField(max_digits=6, decimal_places=2)

    # rating entre 0 y 5, empieza en 0
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0,
    )
    reviews_count = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to='gyms/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# anuncios que puede publicar el dueño del gym (promos, ofertas, novedades)
class GymAnnouncement(models.Model):
    class Kind(models.TextChoices):
        PROMOCION = "PROMOCION", "Promoción"
        OFERTA = "OFERTA", "Oferta"
        NOVEDAD = "NOVEDAD", "Novedad"

    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE,
        related_name="announcements"
    )
    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
    )
    title = models.CharField(max_length=150)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.gym.name} - {self.kind} - {self.title}"


# horario del gym por día de la semana, incluyendo festivos
class GymSchedule(models.Model):
    class DayType(models.TextChoices):
        MON = "MON", "Lunes"
        TUE = "TUE", "Martes"
        WED = "WED", "Miércoles"
        THU = "THU", "Jueves"
        FRI = "FRI", "Viernes"
        SAT = "SAT", "Sábado"
        SUN = "SUN", "Domingo"
        HOL = "HOL", "Festivo"

    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="schedules")
    day_type = models.CharField(max_length=3, choices=DayType.choices)
    opening_hour = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(23)],
        default=7,
    )
    closing_hour = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(24)],
        default=22,
    )
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("gym", "day_type")

    def __str__(self):
        if self.is_closed:
            return f"{self.gym.name} - {self.day_type}: Cerrado"
        return f"{self.gym.name} - {self.day_type}: {self.opening_hour:02d}:00–{self.closing_hour:02d}:00"


# perfil de ocupación por hora y día, esto es lo que alimenta las recomendaciones
class GymOccupancyProfile(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    class Zone(models.TextChoices):
        GENERAL = "GENERAL", "General"

    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE,
        related_name="occupancy_profiles"
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    hour = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(23)]
    )
    zone = models.CharField(
        max_length=20,
        choices=Zone.choices,
        default=Zone.GENERAL
    )
    # porcentaje de ocupación estimado para esa franja
    occupancy_percent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    # qué tan fiable es ese dato, de 0 a 100
    confidence = models.IntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ("gym", "day_of_week", "hour", "zone")
        indexes = [
            models.Index(fields=["gym", "day_of_week", "hour"]),
        ]

    def __str__(self):
        return f"{self.gym.name} - {self.day_of_week} - {self.hour}:00"


# relación entre usuario y gym que sigue, para notificaciones
class GymFollower(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_gyms",
    )
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)
    # cuando el usuario leyó los anuncios por última vez
    last_read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "gym")

    def __str__(self):
        return f"{self.user.username} → {self.gym.name}"