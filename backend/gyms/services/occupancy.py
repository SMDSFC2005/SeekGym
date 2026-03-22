from django.utils import timezone
from gyms.models import GymOccupancyProfile


GOOD = "GOOD"
MEDIUM = "MEDIUM"
AVOID = "AVOID"


def get_local_now(now=None):
    return timezone.localtime(now or timezone.now())


def get_day_and_hour(now=None):
    local_now = get_local_now(now)
    return local_now.weekday(), local_now.hour


def get_status_from_occupancy(occupancy_percent: int) -> str:
    if occupancy_percent < 40:
        return GOOD
    if occupancy_percent < 70:
        return MEDIUM
    return AVOID


def get_current_profile_for_gym(gym, now=None):
    day_of_week, hour = get_day_and_hour(now)

    return GymOccupancyProfile.objects.filter(
        gym=gym,
        day_of_week=day_of_week,
        hour=hour,
        zone=GymOccupancyProfile.Zone.GENERAL,
    ).first()


def get_current_occupancy_data(gym, now=None):
    profile = get_current_profile_for_gym(gym, now)

    if not profile:
        return {
            "current_occupancy": None,
            "current_status": None,
            "confidence": None,
        }

    return {
        "current_occupancy": profile.occupancy_percent,
        "current_status": get_status_from_occupancy(profile.occupancy_percent),
        "confidence": profile.confidence,
    }


def get_best_time_today(gym, now=None):
    day_of_week, current_hour = get_day_and_hour(now)

    profiles = GymOccupancyProfile.objects.filter(
        gym=gym,
        day_of_week=day_of_week,
        zone=GymOccupancyProfile.Zone.GENERAL,
        hour__gte=current_hour,
    ).order_by("occupancy_percent", "hour")

    best_profile = profiles.first()

    if not best_profile:
        return None

    return {
        "hour": best_profile.hour,
        "label": f"{best_profile.hour:02d}:00",
        "occupancy_percent": best_profile.occupancy_percent,
        "confidence": best_profile.confidence,
    }


def build_home_gym_payload(gym, now=None):
    current_data = get_current_occupancy_data(gym, now)
    best_time_today = get_best_time_today(gym, now)

    return {
        "id": gym.id,
        "name": gym.name,
        "slug": gym.slug,
        "city": gym.city,
        "postal_code": gym.postal_code,
        "address": gym.address,
        "description": gym.description,
        "price_per_month": str(gym.price_per_month),
        "rating": str(gym.rating),
        "reviews_count": gym.reviews_count,
        "image_url": gym.image_url,
        "current_occupancy": current_data["current_occupancy"],
        "current_status": current_data["current_status"],
        "confidence": current_data["confidence"],
        "best_time_today": best_time_today,
    }