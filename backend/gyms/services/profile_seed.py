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
    0: WEEKDAY_PATTERN,
    1: WEEKDAY_PATTERN,
    2: WEEKDAY_PATTERN,
    3: WEEKDAY_PATTERN,
    4: WEEKDAY_PATTERN,
    5: SATURDAY_PATTERN,
    6: SUNDAY_PATTERN,
}


def _get_confidence(hour: int, day_of_week: int) -> int:
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

    GymOccupancyProfile.objects.filter(gym=gym).delete()

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
