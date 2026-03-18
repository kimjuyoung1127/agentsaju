from __future__ import annotations

from datetime import UTC, datetime

from timezonefinder import TimezoneFinder

from .constants import HIDDEN_STEMS, SUPPORTED_YEAR_MAX, SUPPORTED_YEAR_MIN
from .errors import SajuValidationError
from .models import BirthInput, ChartCore, CompileChartResponse, FeatureVector, ValidationMeta
from .sexagenary import (
    compute_day_pillar,
    compute_element_balance,
    compute_hour_pillar,
    compute_month_pillar,
    compute_relations_matrix,
    compute_ten_god_weights,
    compute_year_pillar,
    convert_lunar_to_solar,
    dominant_elements,
)
from .solar_terms import find_solar_longitude_ingress, solar_longitude_degrees, solar_term_window_for_datetime
from .time_utils import apply_early_zi_policy, get_zoneinfo, normalize_birth_input


_timezone_finder = TimezoneFinder()


def _normalize_to_solar_datetime(birth_input: BirthInput) -> tuple[datetime, dict[str, object]]:
    zone = get_zoneinfo(birth_input.timezone)
    dt = birth_input.birth_datetime
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=zone)
    else:
        dt = dt.astimezone(zone)

    corrections: dict[str, object] = {}
    if birth_input.calendar == "lunar":
        solar_year, solar_month, solar_day = convert_lunar_to_solar(
            dt.year, dt.month, dt.day, birth_input.leap_month
        )
        dt = dt.replace(year=solar_year, month=solar_month, day=solar_day)
        corrections["lunar_source"] = {
            "year": birth_input.birth_datetime.year,
            "month": birth_input.birth_datetime.month,
            "day": birth_input.birth_datetime.day,
            "leap_month": birth_input.leap_month,
        }

    if birth_input.location and birth_input.location.latitude is not None:
        resolved = _timezone_finder.timezone_at(
            lng=birth_input.location.longitude,
            lat=birth_input.location.latitude,
        )
        if resolved:
            corrections["resolved_timezone_from_location"] = resolved

    normalized, normalized_corrections = normalize_birth_input(
        birth_input.model_copy(update={"birth_datetime": dt, "calendar": "solar"})
    )
    corrections.update(normalized_corrections)

    if not (SUPPORTED_YEAR_MIN <= normalized.year <= SUPPORTED_YEAR_MAX):
        raise SajuValidationError(
            f"supported year range is {SUPPORTED_YEAR_MIN}..{SUPPORTED_YEAR_MAX}"
        )
    return normalized, corrections


def compile_chart(birth_input: BirthInput) -> CompileChartResponse:
    normalized_dt, corrections = _normalize_to_solar_datetime(birth_input)
    day_reference_dt = apply_early_zi_policy(normalized_dt, birth_input.early_zi_time)

    ipchun = find_solar_longitude_ingress(normalized_dt.year, 315.0)
    year_reference = normalized_dt.year if normalized_dt.astimezone(UTC) >= ipchun else normalized_dt.year - 1
    year_pillar = compute_year_pillar(year_reference)

    solar_longitude = solar_longitude_degrees(normalized_dt)
    month_order = int(((solar_longitude - 315.0) % 360.0) // 30.0) % 12
    month_pillar = compute_month_pillar(year_pillar.stem, month_order)
    day_pillar = compute_day_pillar(day_reference_dt)
    hour_pillar = compute_hour_pillar(day_pillar.stem, normalized_dt.hour)

    pillars = {
        "year": year_pillar,
        "month": month_pillar,
        "day": day_pillar,
        "hour": hour_pillar,
    }
    hidden_stems = {name: HIDDEN_STEMS[pillar.branch] for name, pillar in pillars.items()}
    relations_matrix = compute_relations_matrix(pillars)
    element_balance = compute_element_balance(pillars)
    ten_gods = compute_ten_god_weights(day_pillar.stem, pillars)
    useful_signals, unfavorable_signals = dominant_elements(element_balance)

    policy_snapshot = {
        "calendar_engine_version": "chart-v1",
        "timezone_default": birth_input.timezone,
        "apply_local_mean_time": birth_input.apply_local_mean_time,
        "early_zi_time": birth_input.early_zi_time,
        "supported_year_min": SUPPORTED_YEAR_MIN,
        "supported_year_max": SUPPORTED_YEAR_MAX,
    }
    corrections["solar_term_window"] = solar_term_window_for_datetime(normalized_dt)

    chart_core = ChartCore(
        pillars=pillars,
        hidden_stems=hidden_stems,
        day_master=day_pillar.stem,
        corrections=corrections,
        policy_snapshot=policy_snapshot,
    )
    feature_vector = FeatureVector(
        element_balance=element_balance,
        yin_yang_balance=round(
            sum(1 if pillar.stem in {"Gap", "Byeong", "Mu", "Gyeong", "Im"} else -1 for pillar in pillars.values())
            / 4.0,
            4,
        ),
        ten_gods=ten_gods,
        relations_matrix=relations_matrix,
        useful_signals=useful_signals,
        unfavorable_signals=unfavorable_signals,
    )
    validation_meta = ValidationMeta(
        engine_version="chart-v1",
        policy_snapshot=policy_snapshot,
        normalized_birth_datetime=normalized_dt.isoformat(),
        kasi_comparison_status="not_checked_runtime",
    )
    return CompileChartResponse(
        chart_core=chart_core,
        feature_vector=feature_vector,
        validation_meta=validation_meta,
    )
