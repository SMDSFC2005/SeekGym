from django.core.management.base import BaseCommand
from django.db import transaction

from gyms.models import Gym, Province, Municipality


class Command(BaseCommand):
    help = "Asigna province y municipality a los gimnasios existentes"

    def handle(self, *args, **options):
        try:
            sevilla = Province.objects.get(slug="sevilla")
        except Province.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("No existe la provincia Sevilla. Ejecuta primero seed_locations.")
            )
            return

        municipality_map = {
            "sevilla": [
                "Basic-Fit Palacio de Congresos",
                "Areafit Sevilla Este",
                "Supera Entrepuentes",
                "VivaGym Sevilla Este",
            ],
            "alcala-de-guadaira": [
                "Enjoy! Alcalá",
            ],
            "dos-hermanas": [
                "Fitness Park Dos Hermanas",
            ],
            "mairena-del-aljarafe": [
                "Go Fit Mairena",
            ],
            "utrera": [
                "Gym Utrera Center",
            ],
            "la-rinconada": [
                "Box La Rinconada",
            ],
        }

        with transaction.atomic():
            for municipality_slug, gym_names in municipality_map.items():
                try:
                    municipality = Municipality.objects.get(
                        province=sevilla,
                        slug=municipality_slug
                    )
                except Municipality.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No existe el municipio con slug '{municipality_slug}'. Se omite."
                        )
                    )
                    continue

                gyms = Gym.objects.filter(name__in=gym_names)

                for gym in gyms:
                    gym.province = sevilla
                    gym.municipality = municipality
                    gym.save(update_fields=["province", "municipality"])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Asignado {gym.name} -> {municipality.name}, {sevilla.name}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Asignación de ubicaciones completada."))