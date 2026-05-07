from django.core.management.base import BaseCommand

from gyms.models import Gym, GymOccupancyProfile, GymSchedule
from gyms.services.profile_seed import seed_gym_occupancy_profiles

GYM_SLUG_ADJUSTMENTS = {
    "basicfit-palacio-congresos": 18,
    "vivagym-sevilla-este":       12,
    "supera-entrepuentes":         0,
    "areafit-sevilla-este":      -12,
}


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
        gyms = Gym.objects.filter(is_active=True)
        if options["gym"]:
            gyms = gyms.filter(slug=options["gym"])

        if not gyms.exists():
            self.stdout.write(self.style.ERROR("No se encontraron gimnasios."))
            return

        self.stdout.write(f"Generando perfiles para {gyms.count()} gimnasio(s)...")

        created_total = 0
        base_seed = options["seed"]

        for i, gym in enumerate(gyms):
            gym_adjustment = GYM_SLUG_ADJUSTMENTS.get(gym.slug, 0)
            seed_gym_occupancy_profiles(gym, gym_adjustment=gym_adjustment, rng_seed=base_seed + i)
            count = GymOccupancyProfile.objects.filter(gym=gym).count()
            created_total += count
            self._seed_schedule(gym)
            self.stdout.write(f"  {gym.name}: {count} perfiles + horario")

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
