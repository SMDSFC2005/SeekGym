from django.core.management.base import BaseCommand
from gyms.models import Gym, GymOccupancyProfile


class Command(BaseCommand):
    help = "Seed gyms and occupancy data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding gyms...")

        gyms_data = [
            {
                "name": "Supera Entrepuentes",
                "slug": "supera-entrepuentes",
                "city": "Sevilla",
                "postal_code": "41020",
                "address": "Sevilla Este",
                "price_per_month": 45.00,
                "rating": 4.5,
                "reviews_count": 120,
            },
            {
                "name": "VivaGym Sevilla Este",
                "slug": "vivagym-sevilla-este",
                "city": "Sevilla",
                "postal_code": "41020",
                "address": "Sevilla Este",
                "price_per_month": 35.00,
                "rating": 4.2,
                "reviews_count": 98,
            },
            {
                "name": "Basic-Fit Palacio de Congresos",
                "slug": "basicfit-palacio-congresos",
                "city": "Sevilla",
                "postal_code": "41020",
                "address": "Sevilla Este",
                "price_per_month": 30.00,
                "rating": 4.0,
                "reviews_count": 200,
            },
            {
                "name": "Areafit Sevilla Este",
                "slug": "areafit-sevilla-este",
                "city": "Sevilla",
                "postal_code": "41019",
                "address": "Sevilla Este",
                "price_per_month": 40.00,
                "rating": 4.3,
                "reviews_count": 75,
            },
        ]

        gyms = []

        for data in gyms_data:
            gym, _ = Gym.objects.update_or_create(
                slug=data["slug"],
                defaults=data
            )
            gyms.append(gym)

        self.stdout.write("Creating occupancy profiles...")

        GymOccupancyProfile.objects.all().delete()

        for gym in gyms:
            for day in range(7):
                for hour in range(24):

                    occupancy = self.get_base_occupancy(hour)

                    # Ajuste por gym
                    if "Basic" in gym.name:
                        occupancy += 15
                    elif "VivaGym" in gym.name:
                        occupancy += 10
                    elif "Areafit" in gym.name:
                        occupancy -= 10

                    occupancy = max(0, min(100, occupancy))

                    GymOccupancyProfile.objects.create(
                        gym=gym,
                        day_of_week=day,
                        hour=hour,
                        occupancy_percent=occupancy,
                        confidence=70,
                    )

        self.stdout.write(self.style.SUCCESS("Seed completed"))

    def get_base_occupancy(self, hour):
        if 6 <= hour <= 8:
            return 50
        elif 9 <= hour <= 13:
            return 40
        elif 14 <= hour <= 16:
            return 25
        elif 17 <= hour <= 21:
            return 80
        elif 22 <= hour <= 23:
            return 50
        return 30