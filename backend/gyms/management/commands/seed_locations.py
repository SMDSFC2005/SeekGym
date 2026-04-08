from django.core.management.base import BaseCommand
from django.utils.text import slugify

from gyms.models import Province, Municipality


class Command(BaseCommand):
    help = "Crea provincias y municipios base para filtros"

    def handle(self, *args, **options):
        province_name = "Sevilla"

        municipality_names = [
            "Sevilla",
            "Alcalá de Guadaíra",
            "Dos Hermanas",
            "Mairena del Aljarafe",
            "Utrera",
            "La Rinconada",
        ]

        province, created = Province.objects.get_or_create(
            slug=slugify(province_name),
            defaults={"name": province_name},
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Provincia creada: {province.name}'))
        else:
            self.stdout.write(f'Provincia ya existente: {province.name}')

        for municipality_name in municipality_names:
            municipality, created = Municipality.objects.get_or_create(
                province=province,
                slug=slugify(municipality_name),
                defaults={"name": municipality_name},
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Municipio creado: {municipality.name}')
                )
            else:
                self.stdout.write(f'Municipio ya existente: {municipality.name}')

        self.stdout.write(self.style.SUCCESS("Seed de ubicaciones completado."))