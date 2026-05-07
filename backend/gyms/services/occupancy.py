from datetime import date as date_type

import holidays as holidays_lib
from django.utils import timezone

from gyms.models import GymOccupancyProfile


GOOD = "GOOD"
MEDIUM = "MEDIUM"
AVOID = "AVOID"

RECOMMENDATION_WINDOW_HOURS = 6
MIN_TRAINING_HOURS = 2
CLOSING_HOUR_BONUS = 25  # Reducción de ocupación (puntos) en la última hora antes del cierre

OCCUPANCY_WEIGHT = 0.70
PROXIMITY_WEIGHT = 0.20
CONFIDENCE_WEIGHT = 0.10

# ---------------------------------------------------------------------------
# Contexto temporal
# ---------------------------------------------------------------------------

_SPAIN_HOLIDAYS = holidays_lib.Spain(years=range(2024, 2029))

SPECIAL_DAYS = {
    (2025, 4, 13): "Domingo de Ramos",
    (2025, 4, 17): "Jueves Santo",
    (2025, 4, 18): "Viernes Santo",
    (2025, 4, 20): "Domingo de Resurrección",
    (2025, 12, 24): "Nochebuena",
    (2025, 12, 25): "Navidad",
    (2025, 12, 31): "Nochevieja",
    (2026, 1, 1): "Año Nuevo",
    (2026, 4, 2): "Jueves Santo",
    (2026, 4, 3): "Viernes Santo",
    (2026, 12, 24): "Nochebuena",
    (2026, 12, 25): "Navidad",
    (2026, 12, 31): "Nochevieja",
}

MONTHLY_OCCUPANCY_ADJUSTMENT = {
    1: 10,
    2: 5,
    3: 0,
    4: 0,
    5: -5,
    6: 5,
    7: -20,
    8: -25,
    9: 15,
    10: 0,
    11: 0,
    12: -10,
}

# Mapeo de weekday (0=lunes) a DayType del modelo GymSchedule
_WEEKDAY_TO_DAY_TYPE = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


def is_holiday(d: date_type) -> bool:
    return d in _SPAIN_HOLIDAYS


def is_special_day(d: date_type) -> bool:
    return (d.year, d.month, d.day) in SPECIAL_DAYS


# ---------------------------------------------------------------------------
# Núcleo de contexto
# ---------------------------------------------------------------------------

def get_local_now(now=None):
    return timezone.localtime(now or timezone.now())


def get_context(now=None) -> dict:
    local_now = get_local_now(now)
    today = local_now.date()
    actual_weekday = local_now.weekday()

    holiday = is_holiday(today)
    special = is_special_day(today)

    # Para los perfiles de ocupación usamos patrones de domingo en festivos
    effective_day = 6 if (holiday or special) else actual_weekday

    adjustment = MONTHLY_OCCUPANCY_ADJUSTMENT.get(today.month, 0)
    if special:
        adjustment -= 20
    elif holiday:
        adjustment -= 10

    return {
        "date": today,
        "hour": local_now.hour,
        "actual_weekday": actual_weekday,
        "effective_day": effective_day,
        "is_holiday": holiday,
        "is_special_day": special,
        "special_day_name": SPECIAL_DAYS.get((today.year, today.month, today.day)),
        "occupancy_adjustment": adjustment,
    }


def get_day_and_hour(now=None):
    ctx = get_context(now)
    return ctx["effective_day"], ctx["hour"]


# ---------------------------------------------------------------------------
# Horario del gimnasio
# ---------------------------------------------------------------------------

def _get_schedules_map(gym):
    if not hasattr(gym, "_cached_schedules"):
        gym._cached_schedules = {s.day_type: s for s in gym.schedules.all()}
    return gym._cached_schedules


def get_gym_schedule(gym, ctx):
    """
    Devuelve el GymSchedule que aplica hoy.
    En festivos busca primero la entrada HOL; si no existe, cae a SUN.
    """
    schedules = _get_schedules_map(gym)
    if not schedules:
        return None

    if ctx["is_holiday"] or ctx["is_special_day"]:
        return schedules.get("HOL") or schedules.get("SUN")

    day_type = _WEEKDAY_TO_DAY_TYPE[ctx["actual_weekday"]]
    return schedules.get(day_type)


# ---------------------------------------------------------------------------
# Ocupación
# ---------------------------------------------------------------------------

def get_status_from_occupancy(occupancy_percent):
    if occupancy_percent is None:
        return None
    if occupancy_percent < 40:
        return GOOD
    if occupancy_percent < 70:
        return MEDIUM
    return AVOID


def _apply_adjustment(occupancy_percent, adjustment):
    return max(0, min(100, occupancy_percent + adjustment))


def _closing_proximity_adjustment(hour, closing_hour):
    """La última hora antes del cierre el gym suele estar casi vacío."""
    if closing_hour is None:
        return 0
    return -CLOSING_HOUR_BONUS if (closing_hour - hour) <= 1 else 0


def get_current_profile_for_gym(gym, now=None):
    ctx = get_context(now)
    return GymOccupancyProfile.objects.filter(
        gym=gym,
        day_of_week=ctx["effective_day"],
        hour=ctx["hour"],
        zone=GymOccupancyProfile.Zone.GENERAL,
    ).first()


def get_current_occupancy_data(gym, now=None):
    ctx = get_context(now)

    schedule = get_gym_schedule(gym, ctx)
    if schedule:
        if schedule.is_closed:
            return {"current_occupancy": None, "current_status": None, "confidence": None}
        if ctx["hour"] < schedule.opening_hour or ctx["hour"] >= schedule.closing_hour:
            return {"current_occupancy": None, "current_status": None, "confidence": None}

    profile = get_current_profile_for_gym(gym, now)
    if not profile:
        return {"current_occupancy": None, "current_status": None, "confidence": None}

    closing = schedule.closing_hour if schedule else None
    total_adj = ctx["occupancy_adjustment"] + _closing_proximity_adjustment(ctx["hour"], closing)
    adjusted = _apply_adjustment(profile.occupancy_percent, total_adj)
    return {
        "current_occupancy": adjusted,
        "current_status": get_status_from_occupancy(adjusted),
        "confidence": profile.confidence,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def calculate_score(profile, current_hour, occupancy_adjustment=0, closing_hour=None):
    hours_ahead = profile.hour - current_hour
    if hours_ahead <= 0:
        return None

    total_adj = occupancy_adjustment + _closing_proximity_adjustment(profile.hour, closing_hour)
    adjusted_occupancy = _apply_adjustment(profile.occupancy_percent, total_adj)
    occupancy_score = 1 - (adjusted_occupancy / 100)
    proximity_score = 1 / hours_ahead
    confidence_score = profile.confidence / 100

    return round(
        occupancy_score * OCCUPANCY_WEIGHT
        + proximity_score * PROXIMITY_WEIGHT
        + confidence_score * CONFIDENCE_WEIGHT,
        4,
    )


def build_recommendation_reason(profile, current_hour, latest_recommendable_hour, ctx=None):
    hours_ahead = profile.hour - current_hour

    if profile.occupancy_percent < 40:
        occupancy_text = "ocupación baja"
    elif profile.occupancy_percent < 70:
        occupancy_text = "ocupación moderada"
    else:
        occupancy_text = "ocupación alta, pero es la mejor opción disponible"

    proximity_text = (
        "es la siguiente franja útil" if hours_ahead == 1
        else f"queda a {hours_ahead} horas"
    )

    if profile.confidence >= 80:
        confidence_text = "dato con alta confianza"
    elif profile.confidence >= 60:
        confidence_text = "dato con confianza aceptable"
    else:
        confidence_text = "dato con confianza limitada"

    reason = (
        f"{occupancy_text}, {proximity_text}, {confidence_text} "
        f"(última hora recomendable: {latest_recommendable_hour:02d}:00)."
    )

    if ctx:
        if ctx.get("is_special_day"):
            name = ctx.get("special_day_name", "Día especial")
            reason += f" {name}: se espera menos afluencia de lo habitual."
        elif ctx.get("is_holiday"):
            reason += " Festivo: se aplican patrones de domingo."

    return reason


# ---------------------------------------------------------------------------
# API principal
# ---------------------------------------------------------------------------

def get_best_time_today(gym, now=None):
    ctx = get_context(now)
    current_hour = ctx["hour"]

    schedule = get_gym_schedule(gym, ctx)

    if schedule and schedule.is_closed:
        return None

    opening = schedule.opening_hour if schedule else 0
    closing = schedule.closing_hour if schedule else 24

    all_profiles = list(
        GymOccupancyProfile.objects.filter(
            gym=gym,
            day_of_week=ctx["effective_day"],
            zone=GymOccupancyProfile.Zone.GENERAL,
        ).order_by("hour")
    )

    if not all_profiles:
        return None

    # Filtrar horas dentro del horario del gimnasio
    valid_profiles = [p for p in all_profiles if opening <= p.hour < closing]
    if not valid_profiles:
        return None

    latest_recommendable = closing - MIN_TRAINING_HOURS

    future_profiles = [
        p for p in valid_profiles
        if current_hour < p.hour <= latest_recommendable
    ]

    if not future_profiles:
        return None

    window_profiles = [
        p for p in future_profiles
        if p.hour <= current_hour + RECOMMENDATION_WINDOW_HOURS
    ]

    candidate_profiles = window_profiles if window_profiles else future_profiles

    scored_profiles = [
        (p, calculate_score(p, current_hour, ctx["occupancy_adjustment"], closing))
        for p in candidate_profiles
    ]
    scored_profiles = [(p, s) for p, s in scored_profiles if s is not None]

    if not scored_profiles:
        return None

    def _status_priority(occupancy_percent, hour):
        total_adj = ctx["occupancy_adjustment"] + _closing_proximity_adjustment(hour, closing)
        adjusted = _apply_adjustment(occupancy_percent, total_adj)
        if adjusted < 40:
            return 2  # GOOD
        if adjusted < 70:
            return 1  # MEDIUM
        return 0      # AVOID

    best_profile, best_score = max(
        scored_profiles,
        key=lambda item: (
            _status_priority(item[0].occupancy_percent, item[0].hour),
            item[1],
            -item[0].occupancy_percent,
            item[0].confidence,
            -item[0].hour,
        ),
    )

    total_adj_best = ctx["occupancy_adjustment"] + _closing_proximity_adjustment(best_profile.hour, closing)
    adjusted_best = _apply_adjustment(best_profile.occupancy_percent, total_adj_best)
    if adjusted_best >= 70:
        return None

    end_hour = (best_profile.hour + 1) % 24

    return {
        "hour": best_profile.hour,
        "label": f"{best_profile.hour:02d}:00 - {end_hour:02d}:00",
        "occupancy_percent": adjusted_best,
        "confidence": best_profile.confidence,
        "score": best_score,
        "reason": build_recommendation_reason(
            best_profile, current_hour, latest_recommendable, ctx
        ),
    }


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------

def build_timeline_hour(hour, profile=None, occupancy_adjustment=0, closing_hour=None):
    if profile:
        total_adj = occupancy_adjustment + _closing_proximity_adjustment(hour, closing_hour)
        occupancy = _apply_adjustment(profile.occupancy_percent, total_adj)
        confidence = profile.confidence
    else:
        occupancy = None
        confidence = None

    return {
        "hour": hour,
        "label": f"{hour:02d}:00",
        "occupancy_percent": occupancy,
        "status": get_status_from_occupancy(occupancy),
        "confidence": confidence,
    }


def get_today_timeline(gym, now=None):
    ctx = get_context(now)

    schedule = get_gym_schedule(gym, ctx)
    is_closed_today = schedule.is_closed if schedule else False
    opening = schedule.opening_hour if schedule else 0
    closing = schedule.closing_hour if schedule else 24

    profiles = GymOccupancyProfile.objects.filter(
        gym=gym,
        day_of_week=ctx["effective_day"],
        zone=GymOccupancyProfile.Zone.GENERAL,
    ).order_by("hour")

    profiles_by_hour = {p.hour: p for p in profiles}

    result = []
    for hour in range(24):
        if is_closed_today or hour < opening or hour >= closing:
            result.append(build_timeline_hour(hour))
        else:
            result.append(
                build_timeline_hour(hour, profiles_by_hour.get(hour), ctx["occupancy_adjustment"], closing)
            )

    return result
