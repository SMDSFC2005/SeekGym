from django.core.management.base import BaseCommand
from django.utils.text import slugify

from gyms.models import Municipality, Province

LOCATIONS = [
    ("Álava", ["Vitoria-Gasteiz", "Llodio", "Amurrio", "Iruña de Oca"]),
    ("Albacete", ["Albacete", "Hellín", "Almansa", "Villarrobledo", "La Roda"]),
    ("Alicante", ["Alicante", "Elche", "Torrevieja", "Orihuela", "Benidorm", "Alcoy", "Villena", "Petrer"]),
    ("Almería", ["Almería", "El Ejido", "Roquetas de Mar", "Vícar", "Adra", "Níjar"]),
    ("Asturias", ["Oviedo", "Gijón", "Avilés", "Siero", "Langreo", "Mieres"]),
    ("Ávila", ["Ávila", "Arévalo", "Arenas de San Pedro"]),
    ("Badajoz", ["Badajoz", "Mérida", "Don Benito", "Villanueva de la Serena", "Almendralejo", "Zafra"]),
    ("Islas Baleares", ["Palma", "Calvià", "Manacor", "Ibiza", "Llucmajor", "Marratxí"]),
    ("Barcelona", ["Barcelona", "Hospitalet de Llobregat", "Badalona", "Terrassa", "Sabadell", "Mataró", "Santa Coloma de Gramenet", "Cornellà de Llobregat", "Sant Cugat del Vallès", "Rubí", "Castelldefels", "Viladecans"]),
    ("Burgos", ["Burgos", "Miranda de Ebro", "Aranda de Duero"]),
    ("Cáceres", ["Cáceres", "Plasencia", "Navalmoral de la Mata"]),
    ("Cádiz", ["Algeciras", "Jerez de la Frontera", "Cádiz", "San Fernando", "El Puerto de Santa María", "Chiclana de la Frontera", "La Línea de la Concepción"]),
    ("Cantabria", ["Santander", "Torrelavega", "Castro-Urdiales", "Camargo"]),
    ("Castellón", ["Castellón de la Plana", "Villarreal", "Burriana", "Benicasim"]),
    ("Ciudad Real", ["Ciudad Real", "Puertollano", "Valdepeñas", "Alcázar de San Juan", "Tomelloso"]),
    ("Córdoba", ["Córdoba", "Lucena", "Montilla", "Priego de Córdoba", "Puente Genil"]),
    ("La Coruña", ["A Coruña", "Santiago de Compostela", "Ferrol"]),
    ("Cuenca", ["Cuenca", "Tarancón"]),
    ("Gerona", ["Girona", "Blanes", "Lloret de Mar", "Olot", "Figueres", "Roses"]),
    ("Granada", ["Granada", "Motril", "Almuñécar", "Loja", "Guadix", "Maracena", "Armilla"]),
    ("Guadalajara", ["Guadalajara", "Azuqueca de Henares"]),
    ("Guipúzcoa", ["Donostia-San Sebastián", "Irun", "Errenteria", "Eibar", "Zarautz"]),
    ("Huelva", ["Huelva", "Lepe", "Almonte", "Isla Cristina"]),
    ("Huesca", ["Huesca", "Monzón", "Barbastro"]),
    ("Jaén", ["Jaén", "Linares", "Andújar", "Úbeda", "Baeza", "Alcalá la Real"]),
    ("León", ["León", "Ponferrada", "San Andrés del Rabanedo"]),
    ("Lérida", ["Lleida", "Mollerussa"]),
    ("La Rioja", ["Logroño", "Calahorra", "Arnedo", "Haro"]),
    ("Lugo", ["Lugo", "Viveiro", "Monforte de Lemos"]),
    ("Madrid", ["Madrid", "Móstoles", "Alcalá de Henares", "Fuenlabrada", "Leganés", "Getafe", "Alcorcón", "Torrejón de Ardoz", "Parla", "Alcobendas", "Pozuelo de Alarcón", "Las Rozas de Madrid", "Coslada", "Majadahonda"]),
    ("Málaga", ["Málaga", "Marbella", "Vélez-Málaga", "Mijas", "Fuengirola", "Torremolinos", "Benalmádena", "Estepona", "Ronda", "Antequera"]),
    ("Murcia", ["Murcia", "Cartagena", "Lorca", "Molina de Segura", "Alcantarilla", "Mazarrón"]),
    ("Navarra", ["Pamplona", "Tudela", "Barañáin", "Burlada", "Estella"]),
    ("Orense", ["Ourense", "O Barco de Valdeorras", "Verín"]),
    ("Palencia", ["Palencia", "Aguilar de Campoo"]),
    ("Las Palmas", ["Las Palmas de Gran Canaria", "Telde", "Santa Lucía de Tirajana", "San Bartolomé de Tirajana", "Arrecife", "Puerto del Rosario"]),
    ("Pontevedra", ["Vigo", "Pontevedra", "Vilagarcía de Arousa", "Marín", "O Grove"]),
    ("Salamanca", ["Salamanca", "Béjar"]),
    ("Santa Cruz de Tenerife", ["Santa Cruz de Tenerife", "San Cristóbal de La Laguna", "Arona", "Adeje", "La Orotava", "Los Realejos"]),
    ("Segovia", ["Segovia", "Cuéllar"]),
    ("Sevilla", ["Sevilla", "Dos Hermanas", "Alcalá de Guadaíra", "Écija", "La Rinconada", "Utrera", "Mairena del Aljarafe"]),
    ("Soria", ["Soria", "El Burgo de Osma"]),
    ("Tarragona", ["Tarragona", "Reus", "Tortosa", "Salou", "Cambrils"]),
    ("Teruel", ["Teruel", "Alcañiz"]),
    ("Toledo", ["Toledo", "Talavera de la Reina", "Illescas", "Torrijos"]),
    ("Valencia", ["Valencia", "Torrent", "Gandia", "Paterna", "Sagunto", "Burjassot", "Mislata", "Alzira"]),
    ("Valladolid", ["Valladolid", "Medina del Campo", "Laguna de Duero"]),
    ("Vizcaya", ["Bilbao", "Barakaldo", "Getxo", "Basauri", "Leioa", "Santurtzi"]),
    ("Zamora", ["Zamora", "Benavente"]),
    ("Zaragoza", ["Zaragoza", "Calatayud", "Ejea de los Caballeros", "Tarazona"]),
    ("Ceuta", ["Ceuta"]),
    ("Melilla", ["Melilla"]),
]


def _make_slug(name, existing_slugs):
    base = slugify(name)
    if not base:
        base = "municipio"
    slug = base
    counter = 2
    while slug in existing_slugs:
        slug = f"{base}-{counter}"
        counter += 1
    existing_slugs.add(slug)
    return slug


class Command(BaseCommand):
    help = "Seed all Spanish provinces and major municipalities"

    def handle(self, *args, **options):
        province_count = 0
        municipality_count = 0

        existing_province_slugs = set(Province.objects.values_list("slug", flat=True))

        for province_name, municipality_names in LOCATIONS:
            province_slug = _make_slug(province_name, existing_province_slugs)
            province, created = Province.objects.get_or_create(
                name=province_name,
                defaults={"slug": province_slug},
            )
            if created:
                province_count += 1

            existing_muni_slugs = set(
                Municipality.objects.filter(province=province).values_list("slug", flat=True)
            )

            for muni_name in municipality_names:
                muni_slug = _make_slug(muni_name, existing_muni_slugs)
                _, muni_created = Municipality.objects.get_or_create(
                    province=province,
                    name=muni_name,
                    defaults={"slug": muni_slug},
                )
                if muni_created:
                    municipality_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {province_count} provinces and {municipality_count} municipalities."
            )
        )
