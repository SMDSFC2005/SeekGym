import random

from gyms.models import GymOccupancyProfile

WEEKDAY_PATTERN = {
    6:  38,
    7:  58,
    8:  68,
    9:  50,
    10: 42,
    11: 38,
    12: 42,
    13: 45,
    14: 28,
    15: 22,
    16: 45,
    17: 75,
    18: 82,
    19: 88,
    20: 78,
    21: 60,
    22: 38,
    23: 20,
}

# Viernes: mañana similar, tarde/noche bastante menos (gente sale)
FRIDAY_PATTERN = {
    6:  35,
    7:  55,
    8:  65,
    9:  48,
    10: 40,
    11: 36,
    12: 40,
    13: 42,
    14: 28,
    15: 22,
    16: 35,
    17: 58,
    18: 65,
    19: 70,
    20: 58,
    21: 42,
    22: 25,
    23: 12,
}

SATURDAY_PATTERN = {
    9:  42,
    10: 58,
    11: 65,
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

SUNDAY_PATTERN = {
    10: 25,
    11: 38,
    12: 40,
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
    0: WEEKDAY_PATTERN,  # Lunes
    1: WEEKDAY_PATTERN,  # Martes
    2: WEEKDAY_PATTERN,  # Miércoles
    3: WEEKDAY_PATTERN,  # Jueves
    4: FRIDAY_PATTERN,   # Viernes
    5: SATURDAY_PATTERN,
    6: SUNDAY_PATTERN,
}


# los gyms más caros suelen tener menos gente, esto lo refleja en los datos
def _price_adjustment(price_per_month) -> int:
    """Gimnasios más caros tienen menos afluencia."""
    try:
        price = float(price_per_month)
    except (TypeError, ValueError):
        return 0
    if price < 20:
        return 15
    if price < 35:
        return 5
    if price < 55:
        return 0
    if price < 75:
        return -15
    if price < 100:
        return -25
    return -35


# las horas punta tienen más confianza porque hay más datos históricos
def _get_confidence(hour: int, day_of_week: int) -> int:
    # fin de semana menos confianza, los patrones son más variables
    if day_of_week >= 5:
        return 60
    if 17 <= hour <= 21:
        return 88
    if 7 <= hour <= 9:
        return 78
    if 12 <= hour <= 14:
        return 70
    return 65


def seed_gym_occupancy_profiles(gym, gym_adjustment: int = 0, rng_seed: int = None):
    """
    Genera perfiles de ocupación por defecto para un gimnasio.
    Llamar al crear un gym nuevo para que tenga datos desde el primer momento.
    """
    if rng_seed is not None:
        random.seed(rng_seed)

    # borramos los perfiles anteriores si los había para empezar desde cero
    GymOccupancyProfile.objects.filter(gym=gym).delete()

    price_adj = _price_adjustment(gym.price_per_month)

    for day, pattern in DAY_PATTERNS.items():
        for hour, base_occupancy in pattern.items():
            # añadimos un pelín de aleatoriedad para que no todos los gyms sean iguales
            occupancy = base_occupancy + gym_adjustment + price_adj + random.randint(-5, 5)
            occupancy = max(5, min(95, occupancy))
            GymOccupancyProfile.objects.create(
                gym=gym,
                day_of_week=day,
                hour=hour,
                zone=GymOccupancyProfile.Zone.GENERAL,
                occupancy_percent=occupancy,
                confidence=_get_confidence(hour, day),
            )
