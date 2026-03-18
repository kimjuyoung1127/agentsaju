from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path

from skyfield.api import Loader
from skyfield.framelib import ecliptic_frame

from .constants import SOLAR_TERM_BOUNDARIES


@lru_cache(maxsize=1)
def _skyfield_context() -> tuple[Loader, object, object, object]:
    cache_dir = Path(__file__).resolve().parents[2] / ".skyfield"
    cache_dir.mkdir(parents=True, exist_ok=True)
    loader = Loader(str(cache_dir))
    eph = loader("de421.bsp")
    ts = loader.timescale()
    return loader, ts, eph["earth"], eph["sun"]


@lru_cache(maxsize=4096)
def _solar_longitude_degrees_cached(iso_datetime: str) -> float:
    _, ts, earth, sun = _skyfield_context()
    aware = datetime.fromisoformat(iso_datetime).astimezone(UTC)
    t = ts.from_datetime(aware)
    _, longitude, _ = earth.at(t).observe(sun).apparent().frame_latlon(ecliptic_frame)
    return longitude.degrees % 360.0


def solar_longitude_degrees(dt: datetime) -> float:
    return _solar_longitude_degrees_cached(dt.astimezone(UTC).isoformat())


def _unwrap_longitudes(longitudes: list[float]) -> list[float]:
    unwrapped: list[float] = []
    offset = 0.0
    previous = None
    for longitude in longitudes:
        if previous is not None and longitude < previous:
            offset += 360.0
        unwrapped.append(longitude + offset)
        previous = longitude
    return unwrapped


@lru_cache(maxsize=128)
def find_solar_longitude_ingress(year: int, target_longitude: float) -> datetime:
    start = datetime(year, 1, 1, tzinfo=UTC)
    end = datetime(year + 1, 1, 1, tzinfo=UTC)
    samples: list[datetime] = []
    current = start
    while current <= end:
        samples.append(current)
        current += timedelta(hours=6)

    longitudes = _unwrap_longitudes([solar_longitude_degrees(dt) for dt in samples])
    start_longitude = longitudes[0]
    target = target_longitude
    while target < start_longitude:
        target += 360.0

    left_dt = samples[0]
    right_dt = samples[-1]
    for index in range(len(samples) - 1):
        if longitudes[index] <= target <= longitudes[index + 1]:
            left_dt = samples[index]
            right_dt = samples[index + 1]
            break

    for _ in range(32):
        midpoint = left_dt + (right_dt - left_dt) / 2
        left_long = solar_longitude_degrees(left_dt)
        mid_long = solar_longitude_degrees(midpoint)
        if mid_long < left_long:
            mid_long += 360.0
        local_target = target
        while local_target < left_long:
            local_target += 360.0
        if mid_long < local_target:
            left_dt = midpoint
        else:
            right_dt = midpoint
    return right_dt


def current_month_branch_from_longitude(longitude: float) -> tuple[int, str, str]:
    normalized = (longitude - 315.0) % 360.0
    month_order = int(normalized // 30.0) % 12
    branch, boundary, label = SOLAR_TERM_BOUNDARIES[month_order]
    return month_order, branch, label


def solar_term_window_for_datetime(dt: datetime) -> dict[str, str]:
    longitude = solar_longitude_degrees(dt)
    month_order, branch, label = current_month_branch_from_longitude(longitude)
    start_target = SOLAR_TERM_BOUNDARIES[month_order][1]
    next_target = SOLAR_TERM_BOUNDARIES[(month_order + 1) % 12][1]
    year_for_start = dt.year if not (start_target > 300 and dt.month == 1) else dt.year - 1
    start_dt = find_solar_longitude_ingress(year_for_start, start_target)
    end_dt = find_solar_longitude_ingress(dt.year, next_target)
    if end_dt <= start_dt:
        end_dt = find_solar_longitude_ingress(dt.year + 1, next_target)
    return {
        "term_label": label,
        "month_branch": branch,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "solar_longitude": round(longitude, 4),
    }
