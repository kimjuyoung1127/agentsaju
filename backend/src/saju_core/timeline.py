from __future__ import annotations

from datetime import UTC, datetime

from .constants import BRANCH_ELEMENTS, GOAL_DOMAIN_MAP, STEM_ELEMENTS
from .models import ChartCore, RelationRow, TimelineFactor
from .sexagenary import compute_month_pillar, compute_year_pillar
from .solar_terms import solar_longitude_degrees, solar_term_window_for_datetime


def _timeline_relations(chart_core: ChartCore, active_year_stem: str, active_month_stem: str) -> list[RelationRow]:
    rows: list[RelationRow] = []
    natal_day_master = chart_core.day_master
    if natal_day_master == active_year_stem:
        rows.append(
            RelationRow(
                scope="timeline",
                source_key="day_master",
                target_key="year_stem",
                relation_type="resonance",
                strength=0.7,
            )
        )
    if natal_day_master == active_month_stem:
        rows.append(
            RelationRow(
                scope="timeline",
                source_key="day_master",
                target_key="month_stem",
                relation_type="resonance",
                strength=0.9,
            )
        )
    return rows


def _domain_pressure(stem: str, branch: str) -> dict[str, float]:
    pressure = {
        "career": 0.4,
        "relationship": 0.4,
        "wealth": 0.4,
        "health": 0.4,
    }
    stem_element = STEM_ELEMENTS[stem]
    branch_element = BRANCH_ELEMENTS[branch]
    if stem_element in {"metal", "water"}:
        pressure["wealth"] += 0.25
    if stem_element in {"wood", "fire"}:
        pressure["career"] += 0.2
        pressure["relationship"] += 0.1
    if branch_element in {"earth", "metal"}:
        pressure["career"] += 0.1
    if branch_element in {"water", "wood"}:
        pressure["relationship"] += 0.15
        pressure["health"] += 0.1
    if branch_element == "fire":
        pressure["health"] -= 0.05
        pressure["career"] += 0.15
    return {key: round(max(0.0, min(1.0, value)), 4) for key, value in pressure.items()}


def build_monthly_timeline(chart_core: ChartCore, horizon_year: int, policy: dict[str, object]) -> list[TimelineFactor]:
    timeline: list[TimelineFactor] = []
    ipchun = datetime.fromisoformat(chart_core.corrections["solar_term_window"]["start"])
    year_reference = horizon_year if ipchun.year == horizon_year else horizon_year
    for month in range(1, 13):
        dt = datetime(horizon_year, month, 15, 12, tzinfo=UTC)
        longitude = solar_longitude_degrees(dt)
        month_order = int(((longitude - 315.0) % 360.0) // 30.0) % 12
        active_year = compute_year_pillar(year_reference if month >= 2 else year_reference - 1)
        active_month = compute_month_pillar(active_year.stem, month_order)
        relations = _timeline_relations(chart_core, active_year.stem, active_month.stem)
        solar_window = solar_term_window_for_datetime(dt)
        timeline.append(
            TimelineFactor(
                mode="monthly",
                timestep=f"{horizon_year}-{month:02d}",
                daewoon={"status": "not_implemented_v1"},
                sewoon={"year_pillar": active_year.model_dump()},
                period_factor={
                    "month_pillar": active_month.model_dump(),
                    "solar_term_window": solar_window,
                    "domain_pressure": _domain_pressure(active_month.stem, active_month.branch),
                },
                relations=relations,
            )
        )
    return timeline
