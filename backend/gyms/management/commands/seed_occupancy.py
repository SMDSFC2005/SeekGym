import random

from django.core.management.base import BaseCommand

from gyms.models import Gym, GymOccupancyProfile, GymSchedule


# ---------------------------------------------------------------------------
# Patrones de ocupación base por hora
# Solo se definen las horas en que el gimnasio está abierto.
# ---------------------------------------------------------------------------

# Lunes a Viernes: pico fuerte en tarde, moderado en mañana
WEEKDAY_PATTERN = {
    6:  38,
    7:  58,
    8:  68,  # pico mañana
    9:  50,
    10: 42,
    11: 38,
    12: 42,
    13: 45,
    14: 28,  # bajada mediodía
    15: 22,
    16: 45,  # empieza a subir: primeras llegadas post-trabajo
    17: 75,  # rush de tarde, ya bastante lleno
    18: 82,
    19: 88,  # pico tarde (máximo del día)
    20: 78,
    21: 60,
    22: 38,
    23: 20,
}

# Sábado: ocupación media, sin el pico de tarde tan marcado
SATURDAY_PATTERN = {
    9:  42,
    10: 58,
    11: 65,  # pico mañana sábado
    12: 58,
    13: 48,
    14: 38,
    15: 28,
    16: 25,
    17: 42,
    18: 48,
    19: 45,
    20: 35,
    21: 22,
    22: 12,
}

# Domingo: ocupación baja, solo mañana y algo de tarde
SUNDAY_PATTERN = {
    10: 25,
    11: 38,
    12: 40,  # pico domingo
    13: 32,
    14: 22,
    15: 18,
    16: 15,
    17: 25,
    18: 30,
    19: 28,
    20: 18,
    21: 10,
}

DAY_PATTERNS = {
    0: WEEKDAY_PATTERN,
    1: WEEKDAY_PATTERN,
    2: WEEKDAY_PATTERN,
    3: WEEKDAY_PATTERN,
    4: WEEKDAY_PATTERN,
    5: SATURDAY_PATTERN,
    6: SUNDAY_PATTERN,
}

# Ajuste fijo por slug de gimnasio (puntos de ocupación sobre la base)
GYM_SLUG_ADJUSTMENTS = {
    "basicfit-palacio-congresos": 18,   # muy popular, siempre lleno
    "vivagym-sevilla-este":       12,
    "supera-entrepuentes":         0,
    "areafit-sevilla-este":      -12,   # menos afluencia
}


def _get_confidence(hour: int, day_of_week: int) -> int:
    """Más confianza en horas pico entre semana donde hay más datos históricos."""
    if day_of_week >= 5:
        return 60
    if 17 <= hour <= 21:
        return 88
    if 7 <= hour <= 9:
        return 78
    if 12 <= hour <= 14:
        return 70
    return 65


class Command(BaseCommand):
    help = "Pobla GymOccupancyProfile con datos realistas diferenciados por día"

    def add_arguments(self, parser):
        parser.add_argument(
            "--gym",
            type=str,
            help="Slug del gimnasio. Si no se indica, se procesan todos los activos.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Semilla aleatoria para reproducibilidad (default: 42).",
        )

    def handle(self, *args, **options):
        random.seed(options["seed"])

        gyms = Gym.objects.filter(is_active=True)
        if options["gym"]:
            gyms = gyms.filter(slug=options["gym"])

        if not gyms.exists():
            self.stdout.write(self.style.ERROR("No se encontraron gimnasios."))
            return

        self.stdout.write(f"Generando perfiles para {gyms.count()} gimnasio(s)...")

        created_total = 0

        for gym in gyms:
            GymOccupancyProfile.objects.filter(gym=gym).delete()

            gym_adjustment = GYM_SLUG_ADJUSTMENTS.get(gym.slug, 0)
            created = 0

            for day, pattern in DAY_PATTERNS.items():
                for hour, base_occupancy in pattern.items():
                    occupancy = base_occupancy + gym_adjustment + random.randint(-5, 5)
                    occupancy = max(5, min(95, occupancy))

                    GymOccupancyProfile.objects.create(
                        gym=gym,
                        day_of_week=day,
                        hour=hour,
                        zone=GymOccupancyProfile.Zone.GENERAL,
                        occupancy_percent=occupancy,
                        confidence=_get_confidence(hour, day),
                    )
                    created += 1

            created_total += created
            self._seed_schedule(gym)
            self.stdout.write(f"  {gym.name}: {created} perfiles + horario")

        self.stdout.write(
            self.style.SUCCESS(f"\nTotal: {created_total} perfiles creados.")
        )

    def _seed_schedule(self, gym):
        DEFAULT_SCHEDULE = [
            {"day_type": "MON", "opening_hour": 7,  "closing_hour": 22, "is_closed": False},
            {"day_type": "TUE", "opening_hour": 7,  "closing_hour": 22, "is_closed": False},
            {"day_type": "WED", "opening_hour": 7,  "closing_hour": 22, "is_closed": False},
            {"day_type": "THU", "opening_hour": 7,  "closing_hour": 22, "is_closed": False},
            {"day_type": "FRI", "opening_hour": 7,  "closing_hour": 22, "is_closed": False},
            {"day_type": "SAT", "opening_hour": 9,  "closing_hour": 20, "is_closed": False},
            {"day_type": "SUN", "opening_hour": 10, "closing_hour": 16, "is_closed": False},
            {"day_type": "HOL", "opening_hour": 10, "closing_hour": 16, "is_closed": False},
        ]
        for entry in DEFAULT_SCHEDULE:
            GymSchedule.objects.update_or_create(
                gym=gym,
                day_type=entry["day_type"],
                defaults={k: v for k, v in entry.items() if k != "day_type"},
            )
