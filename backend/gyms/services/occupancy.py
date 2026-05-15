from datetime import date as date_type, timedelta, datetime as datetime_type

import holidays as holidays_lib
from django.utils import timezone

from gyms.models import GymOccupancyProfile


GOOD = "GOOD"
MEDIUM = "MEDIUM"
AVOID = "AVOID"

# cuántas horas hacia adelante miramos para recomendar
RECOMMENDATION_WINDOW_HOURS = 6
# necesitamos al menos 2h antes del cierre para recomendar una franja
MIN_TRAINING_HOURS = 2
CLOSING_HOUR_BONUS = 25  # Reducción de ocupación (puntos) en la última hora antes del cierre

# pesos para el scoring de la mejor hora: la ocupación manda más
OCCUPANCY_WEIGHT = 0.70
PROXIMITY_WEIGHT = 0.20
CONFIDENCE_WEIGHT = 0.10

# ---------------------------------------------------------------------------
# Contexto temporal
# ---------------------------------------------------------------------------

_SPAIN_HOLIDAYS = holidays_lib.Spain(years=range(2024, 2029))

# Días especiales que NO son festivos nacionales pero reducen claramente la afluencia.
# Jueves Santo, Viernes Santo, Navidad y Año Nuevo ya los cubre holidays.Spain.
SPECIAL_DAYS = {
    # 2025 — Carnaval
    (2025, 3, 3):  "Lunes de Carnaval",
    (2025, 3, 4):  "Martes de Carnaval",
    # 2025 — Semana Santa (festivos JU/VI ya en holidays.Spain)
    (2025, 4, 13): "Domingo de Ramos",
    (2025, 4, 15): "Martes Santo",
    (2025, 4, 16): "Miércoles Santo",
    (2025, 4, 19): "Sábado Santo",
    (2025, 4, 20): "Domingo de Resurrección",
    # 2025 — puentes / días de baja afluencia
    (2025, 12, 26): "Día después de Navidad",
    # 2026 — Carnaval
    (2026, 2, 16): "Lunes de Carnaval",
    (2026, 2, 17): "Martes de Carnaval",
    # 2026 — Semana Santa
    (2026, 3, 29): "Domingo de Ramos",
    (2026, 3, 31): "Martes Santo",
    (2026, 4, 1):  "Miércoles Santo",
    (2026, 4, 4):  "Sábado Santo",
    (2026, 4, 5):  "Domingo de Resurrección",
    # 2026 — puentes
    (2026, 12, 26): "Día después de Navidad",
}

# Días con patrón partido: mañana más lleno de lo normal (la gente va antes
# de la comida/cena familiar), tarde/noche prácticamente vacío.
SPLIT_DAYS = {
    (2025, 12, 24): "Nochebuena",
    (2025, 12, 31): "Nochevieja",
    (2026, 1, 5):   "Víspera de Reyes",
    (2026, 12, 24): "Nochebuena",
    (2026, 12, 31): "Nochevieja",
    (2027, 1, 5):   "Víspera de Reyes",
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


# comprueba si una fecha es festivo nacional en España
def is_holiday(d: date_type) -> bool:
    return d in _SPAIN_HOLIDAYS


# días especiales como Carnaval o Semana Santa que no son festivos oficiales
def is_special_day(d: date_type) -> bool:
    return (d.year, d.month, d.day) in SPECIAL_DAYS


# días con patrón partido: mañana lleno, tarde vacío (Nochebuena, Nochevieja...)
def is_split_day(d: date_type) -> bool:
    return (d.year, d.month, d.day) in SPLIT_DAYS


def get_split_day_hour_adjustment(hour: int, d: date_type) -> int:
    """
    Dec 24, Dec 31, Jan 5: la gente va por la mañana antes de la comida familiar.
    A partir de las 15h el gym se queda casi vacío.
    """
    if not is_split_day(d):
        return 0
    if hour <= 12:
        return 15   # mañana: más gente de lo normal
    if hour >= 15:
        return -30  # tarde/noche: casi nadie
    return 0


# ---------------------------------------------------------------------------
# Núcleo de contexto
# ---------------------------------------------------------------------------

# devuelve la hora local del servidor (importante para España con cambio horario)
def get_local_now(now=None):
    return timezone.localtime(now or timezone.now())


# arma el contexto temporal completo: día efectivo, ajustes de ocupación, festivos...
def get_context(now=None) -> dict:
    local_now = get_local_now(now)
    today = local_now.date()
    actual_weekday = local_now.weekday()
    key = (today.year, today.month, today.day)

    holiday = is_holiday(today)
    special = is_special_day(today)
    split = is_split_day(today)

    # Split days mantienen patrones de entre semana (mañana activa).
    # Días especiales normales y festivos usan patrones de domingo.
    effective_day = actual_weekday if split else (6 if (holiday or special) else actual_weekday)

    # ajuste mensual base más correcciones por tipo de día especial
    adjustment = MONTHLY_OCCUPANCY_ADJUSTMENT.get(today.month, 0)
    if split:
        adjustment -= 10  # ajuste plano moderado; el reparto mañana/tarde lo gestiona get_split_day_hour_adjustment
    elif special:
        adjustment -= 20
    elif holiday:
        adjustment -= 10

    return {
        "date": today,
        "hour": local_now.hour,
        "actual_weekday": actual_weekday,
        "effective_day": effective_day,
        "is_holiday": holiday,
        "is_special_day": special or split,
        "special_day_name": SPLIT_DAYS.get(key) or SPECIAL_DAYS.get(key),
        "occupancy_adjustment": adjustment,
    }


# atajo para pillar solo el día efectivo y la hora actual
def get_day_and_hour(now=None):
    ctx = get_context(now)
    return ctx["effective_day"], ctx["hour"]


# ---------------------------------------------------------------------------
# Horario del gimnasio
# ---------------------------------------------------------------------------

# cacheamos el horario del gym para no hacer múltiples queries por request
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

    # en festivos usamos HOL, y si no está configurado tiramos del domingo
    if ctx["is_holiday"] or ctx["is_special_day"]:
        return schedules.get("HOL") or schedules.get("SUN")

    day_type = _WEEKDAY_TO_DAY_TYPE[ctx["actual_weekday"]]
    return schedules.get(day_type)


# ---------------------------------------------------------------------------
# Ocupación
# ---------------------------------------------------------------------------

# convierte el porcentaje de ocupación en un estado legible: GOOD, MEDIUM o AVOID
def get_status_from_occupancy(occupancy_percent):
    if occupancy_percent is None:
        return None
    if occupancy_percent < 40:
        return GOOD
    if occupancy_percent < 70:
        return MEDIUM
    return AVOID


# aplica el ajuste y lo mantiene entre 0 y 100 siempre
def _apply_adjustment(occupancy_percent, adjustment):
    return max(0, min(100, occupancy_percent + adjustment))


def _closing_proximity_adjustment(hour, closing_hour):
    """La última hora antes del cierre el gym suele estar casi vacío."""
    if closing_hour is None:
        return 0
    return -CLOSING_HOUR_BONUS if (closing_hour - hour) <= 1 else 0


# pillamos el perfil de ocupación de la hora actual para ese gym
def get_current_profile_for_gym(gym, now=None):
    ctx = get_context(now)
    return GymOccupancyProfile.objects.filter(
        gym=gym,
        day_of_week=ctx["effective_day"],
        hour=ctx["hour"],
        zone=GymOccupancyProfile.Zone.GENERAL,
    ).first()


# devuelve la ocupación actual del gym con todos los ajustes aplicados
def get_current_occupancy_data(gym, now=None):
    ctx = get_context(now)

    schedule = get_gym_schedule(gym, ctx)
    if schedule:
        # si está cerrado o fuera de horario, no hay dato de ocupación
        if schedule.is_closed:
            return {"current_occupancy": None, "current_status": None, "confidence": None}
        if ctx["hour"] < schedule.opening_hour or ctx["hour"] >= schedule.closing_hour:
            return {"current_occupancy": None, "current_status": None, "confidence": None}

    profile = get_current_profile_for_gym(gym, now)
    if not profile:
        return {"current_occupancy": None, "current_status": None, "confidence": None}

    closing = schedule.closing_hour if schedule else None
    # sumamos todos los ajustes: mensual + proximidad cierre + día especial
    total_adj = (
        ctx["occupancy_adjustment"]
        + _closing_proximity_adjustment(ctx["hour"], closing)
        + get_split_day_hour_adjustment(ctx["hour"], ctx["date"])
    )
    adjusted = _apply_adjustment(profile.occupancy_percent, total_adj)
    return {
        "current_occupancy": adjusted,
        "current_status": get_status_from_occupancy(adjusted),
        "confidence": profile.confidence,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

# calcula la puntuación de una franja horaria para ver cuál es la mejor
def calculate_score(profile, current_hour, occupancy_adjustment=0, closing_hour=None, date=None):
    hours_ahead = profile.hour - current_hour
    # si la franja ya pasó no la puntuamos
    if hours_ahead <= 0:
        return None

    total_adj = (
        occupancy_adjustment
        + _closing_proximity_adjustment(profile.hour, closing_hour)
        + (get_split_day_hour_adjustment(profile.hour, date) if date else 0)
    )
    adjusted_occupancy = _apply_adjustment(profile.occupancy_percent, total_adj)
    # menos ocupación = mejor puntuación de ocupación
    occupancy_score = 1 - (adjusted_occupancy / 100)
    proximity_score = 1 / hours_ahead
    confidence_score = profile.confidence / 100

    return round(
        occupancy_score * OCCUPANCY_WEIGHT
        + proximity_score * PROXIMITY_WEIGHT
        + confidence_score * CONFIDENCE_WEIGHT,
        4,
    )


# arma el texto de explicación de por qué se recomienda esa hora
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

    # si es un día especial añadimos contexto al mensaje
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

# calcula la mejor hora para ir al gym hoy a partir de ahora mismo
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

    # solo las horas dentro del horario del gym
    valid_profiles = [p for p in all_profiles if opening <= p.hour < closing]
    if not valid_profiles:
        return None

    # no recomendamos las últimas horas si no da tiempo a entrenar bien
    latest_recommendable = closing - MIN_TRAINING_HOURS

    future_profiles = [
        p for p in valid_profiles
        if current_hour < p.hour <= latest_recommendable
    ]

    if not future_profiles:
        return None

    # preferimos recomendar dentro de la ventana próxima, pero si no hay, miramos más lejos
    window_profiles = [
        p for p in future_profiles
        if p.hour <= current_hour + RECOMMENDATION_WINDOW_HOURS
    ]

    candidate_profiles = window_profiles if window_profiles else future_profiles

    scored_profiles = [
        (p, calculate_score(p, current_hour, ctx["occupancy_adjustment"], closing, ctx["date"]))
        for p in candidate_profiles
    ]
    scored_profiles = [(p, s) for p, s in scored_profiles if s is not None]

    if not scored_profiles:
        return None

    # prioridad: primero GOOD, luego MEDIUM, nunca AVOID
    def _status_priority(occupancy_percent, hour):
        total_adj = (
            ctx["occupancy_adjustment"]
            + _closing_proximity_adjustment(hour, closing)
            + get_split_day_hour_adjustment(hour, ctx["date"])
        )
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

    total_adj_best = (
        ctx["occupancy_adjustment"]
        + _closing_proximity_adjustment(best_profile.hour, closing)
        + get_split_day_hour_adjustment(best_profile.hour, ctx["date"])
    )
    adjusted_best = _apply_adjustment(best_profile.occupancy_percent, total_adj_best)
    # si la mejor opción disponible está muy llena, mejor no recomendar nada
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
# Mejor hora mañana
# ---------------------------------------------------------------------------

# igual que get_best_time_today pero calculado para mañana desde medianoche
def get_best_time_tomorrow(gym, now=None):
    local_now = get_local_now(now)
    tomorrow = local_now.date() + timedelta(days=1)

    # usamos medianoche de mañana como referencia temporal
    tomorrow_midnight = timezone.make_aware(
        datetime_type.combine(tomorrow, datetime_type.min.time())
    )
    ctx = get_context(tomorrow_midnight)

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

    valid_profiles = [p for p in all_profiles if opening <= p.hour < closing]
    if not valid_profiles:
        return None

    latest_recommendable = closing - MIN_TRAINING_HOURS

    candidate_profiles = [p for p in valid_profiles if p.hour <= latest_recommendable]
    if not candidate_profiles:
        return None

    # current_hour=-1 → todos los perfiles son "futuros"; horas_ahead = p.hour + 1
    scored_profiles = [
        (p, calculate_score(p, -1, ctx["occupancy_adjustment"], closing, ctx["date"]))
        for p in candidate_profiles
    ]
    scored_profiles = [(p, s) for p, s in scored_profiles if s is not None]

    if not scored_profiles:
        return None

    def _status_priority(occupancy_percent, hour):
        total_adj = (
            ctx["occupancy_adjustment"]
            + _closing_proximity_adjustment(hour, closing)
            + get_split_day_hour_adjustment(hour, ctx["date"])
        )
        adjusted = _apply_adjustment(occupancy_percent, total_adj)
        if adjusted < 40:
            return 2
        if adjusted < 70:
            return 1
        return 0

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

    total_adj_best = (
        ctx["occupancy_adjustment"]
        + _closing_proximity_adjustment(best_profile.hour, closing)
        + get_split_day_hour_adjustment(best_profile.hour, ctx["date"])
    )
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
            best_profile, -1, latest_recommendable, ctx
        ),
    }


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------

def build_timeline_hour(hour, profile=None, occupancy_adjustment=0, closing_hour=None, date=None):
    if profile:
        total_adj = (
            occupancy_adjustment
            + _closing_proximity_adjustment(hour, closing_hour)
            + (get_split_day_hour_adjustment(hour, date) if date else 0)
        )
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


# construye el timeline completo de las 24h para hoy
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

    # indexamos por hora para acceder rápido
    profiles_by_hour = {p.hour: p for p in profiles}

    result = []
    for hour in range(24):
        # las horas fuera del horario van vacías (sin dato de ocupación)
        if is_closed_today or hour < opening or hour >= closing:
            result.append(build_timeline_hour(hour))
        else:
            result.append(
                build_timeline_hour(hour, profiles_by_hour.get(hour), ctx["occupancy_adjustment"], closing, ctx["date"])
            )

    return result
