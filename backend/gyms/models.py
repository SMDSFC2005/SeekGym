from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Province(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


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


class Gym(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_gym",
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

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0,
    )
    reviews_count = models.PositiveIntegerField(default=0)

    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


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
    occupancy_percent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
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