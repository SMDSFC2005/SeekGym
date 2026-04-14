from django.utils import timezone

from gyms.models import GymOccupancyProfile


GOOD = "GOOD"
MEDIUM = "MEDIUM"
AVOID = "AVOID"

RECOMMENDATION_WINDOW_HOURS = 6
MIN_TRAINING_HOURS = 2

OCCUPANCY_WEIGHT = 0.70
PROXIMITY_WEIGHT = 0.20
CONFIDENCE_WEIGHT = 0.10


def get_local_now(now=None):
    return timezone.localtime(now or timezone.now())


def get_day_and_hour(now=None):
    local_now = get_local_now(now)
    return local_now.weekday(), local_now.hour


def get_status_from_occupancy(occupancy_percent):
    if occupancy_percent is None:
        return None

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


def get_effective_closing_hour(profiles):
    """
    Infiere la hora de cierre a partir del último bloque horario disponible.
    Si el último profile es hour=22, se entiende como bloque 22:00-23:00,
    así que el cierre efectivo es 23.
    """
    if not profiles:
        return None

    last_hour = max(profile.hour for profile in profiles)
    return last_hour + 1


def get_latest_recommendable_hour(profiles, min_training_hours=MIN_TRAINING_HOURS):
    """
    Calcula la última hora de inicio que sigue dejando tiempo útil para entrenar.
    """
    closing_hour = get_effective_closing_hour(profiles)
    if closing_hour is None:
        return None

    return closing_hour - min_training_hours


def calculate_score(profile, current_hour):
    """
    Score más alto = mejor recomendación.
    """
    occupancy_score = 1 - (profile.occupancy_percent / 100)
    hours_ahead = profile.hour - current_hour

    if hours_ahead <= 0:
        return None

    proximity_score = 1 / hours_ahead
    confidence_score = profile.confidence / 100

    score = (
        occupancy_score * OCCUPANCY_WEIGHT
        + proximity_score * PROXIMITY_WEIGHT
        + confidence_score * CONFIDENCE_WEIGHT
    )

    return round(score, 4)


def build_recommendation_reason(profile, current_hour, latest_recommendable_hour):
    hours_ahead = profile.hour - current_hour

    if profile.occupancy_percent < 40:
        occupancy_text = "ocupación baja"
    elif profile.occupancy_percent < 70:
        occupancy_text = "ocupación moderada"
    else:
        occupancy_text = "ocupación alta, pero es la mejor opción disponible"

    if hours_ahead == 1:
        proximity_text = "es la siguiente franja útil"
    else:
        proximity_text = f"queda a {hours_ahead} horas"

    if profile.confidence >= 80:
        confidence_text = "dato con alta confianza"
    elif profile.confidence >= 60:
        confidence_text = "dato con confianza aceptable"
    else:
        confidence_text = "dato con confianza limitada"

    closing_text = (
        f"se evita recomendar horas demasiado cercanas al cierre "
        f"(última hora recomendable: {latest_recommendable_hour:02d}:00)"
    )

    return f"{occupancy_text}, {proximity_text}, {confidence_text}. {closing_text}."


def get_best_time_today(gym, now=None):
    day_of_week, current_hour = get_day_and_hour(now)

    all_profiles = list(
        GymOccupancyProfile.objects.filter(
            gym=gym,
            day_of_week=day_of_week,
            zone=GymOccupancyProfile.Zone.GENERAL,
        ).order_by("hour")
    )

    if not all_profiles:
        return None

    latest_recommendable_hour = get_latest_recommendable_hour(all_profiles)

    if latest_recommendable_hour is None:
        return None

    future_profiles = [
        profile
        for profile in all_profiles
        if current_hour < profile.hour <= latest_recommendable_hour
    ]

    if not future_profiles:
        return None

    window_profiles = [
        profile
        for profile in future_profiles
        if profile.hour <= current_hour + RECOMMENDATION_WINDOW_HOURS
    ]

    candidate_profiles = window_profiles if window_profiles else future_profiles

    scored_profiles = []
    for profile in candidate_profiles:
        score = calculate_score(profile, current_hour)
        if score is not None:
            scored_profiles.append((profile, score))

    if not scored_profiles:
        return None

    best_profile, best_score = max(
        scored_profiles,
        key=lambda item: (
            item[1],
            -item[0].occupancy_percent,
            item[0].confidence,
            -item[0].hour,
        ),
    )

    end_hour = (best_profile.hour + 1) % 24

    return {
        "hour": best_profile.hour,
        "label": f"{best_profile.hour:02d}:00 - {end_hour:02d}:00",
        "occupancy_percent": best_profile.occupancy_percent,
        "confidence": best_profile.confidence,
        "score": best_score,
        "reason": build_recommendation_reason(
            best_profile,
            current_hour,
            latest_recommendable_hour,
        ),
    }


def build_timeline_hour(hour, profile=None):
    occupancy = profile.occupancy_percent if profile else None

    return {
        "hour": hour,
        "label": f"{hour:02d}:00",
        "occupancy_percent": occupancy,
        "status": get_status_from_occupancy(occupancy),
        "confidence": profile.confidence if profile else None,
    }


def get_today_timeline(gym, now=None):
    day_of_week, _ = get_day_and_hour(now)

    profiles = GymOccupancyProfile.objects.filter(
        gym=gym,
        day_of_week=day_of_week,
        zone=GymOccupancyProfile.Zone.GENERAL,
    ).order_by("hour")

    profiles_by_hour = {profile.hour: profile for profile in profiles}

    timeline = []
    for hour in range(24):
        timeline.append(build_timeline_hour(hour, profiles_by_hour.get(hour)))

    return timeline