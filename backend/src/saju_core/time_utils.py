from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .constants import DEFAULT_TIMEZONE, SUPPORTED_YEAR_MAX, SUPPORTED_YEAR_MIN
from .errors import SajuValidationError
from .models import BirthInput


def get_zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name or DEFAULT_TIMEZONE)
    except ZoneInfoNotFoundError as exc:
        raise SajuValidationError("unsupported timezone string") from exc


def normalize_birth_input(birth_input: BirthInput) -> tuple[datetime, dict[str, object]]:
    zone = get_zoneinfo(birth_input.timezone)
    local_dt = birth_input.birth_datetime
    if local_dt.tzinfo is None:
        local_dt = local_dt.replace(tzinfo=zone)
    else:
        local_dt = local_dt.astimezone(zone)

    if not (SUPPORTED_YEAR_MIN <= local_dt.year <= SUPPORTED_YEAR_MAX):
        raise SajuValidationError(
            f"supported year range is {SUPPORTED_YEAR_MIN}..{SUPPORTED_YEAR_MAX}"
        )

    corrections: dict[str, object] = {
        "calendar_normalized": birth_input.calendar,
        "timezone_used": birth_input.timezone,
        "local_mean_time_applied": False,
        "early_zi_time": birth_input.early_zi_time,
    }

    if birth_input.apply_local_mean_time:
        if not birth_input.location or birth_input.location.longitude is None:
            raise SajuValidationError(
                "longitude is required when apply_local_mean_time is true"
            )
        offset_hours = local_dt.utcoffset().total_seconds() / 3600 if local_dt.utcoffset() else 0
        standard_meridian = offset_hours * 15
        correction_minutes = (birth_input.location.longitude - standard_meridian) * 4
        local_dt = local_dt + timedelta(minutes=correction_minutes)
        corrections["local_mean_time_applied"] = True
        corrections["standard_meridian_longitude"] = round(standard_meridian, 4)
        corrections["correction_minutes"] = round(correction_minutes, 4)

    return local_dt, corrections


def apply_early_zi_policy(dt: datetime, early_zi_time: bool) -> datetime:
    if early_zi_time and dt.hour == 23:
        return dt + timedelta(days=1)
    return dt


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))
