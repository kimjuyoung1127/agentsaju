from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import floor

from korean_lunar_calendar import KoreanLunarCalendar

from .constants import (
    BRANCHES,
    BRANCH_ELEMENTS,
    BRANCH_RELATIONS,
    CONTROLS,
    ELEMENTS,
    GENERATES,
    HIDDEN_STEMS,
    HIDDEN_STEM_WEIGHTS,
    STEMS,
    STEM_ELEMENTS,
    STEM_RELATIONS,
    STEM_YIN_YANG,
)
from .models import Pillar, RelationRow


@dataclass(frozen=True)
class PillarComputation:
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar


def pillar_from_index(index: int) -> Pillar:
    return Pillar(stem=STEMS[index % 10], branch=BRANCHES[index % 12])


def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    a = (14 - month) // 12
    y2 = year + 4800 - a
    m2 = month + 12 * a - 3
    return day + ((153 * m2 + 2) // 5) + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def compute_day_pillar(dt: datetime) -> Pillar:
    index = (gregorian_to_jdn(dt.year, dt.month, dt.day) + 5) % 60
    return pillar_from_index(index)


def compute_hour_pillar(day_stem: str, hour: int) -> Pillar:
    branch_index = ((hour + 1) // 2) % 12
    start_stem_index = ((STEMS.index(day_stem) % 5) * 2) % 10
    stem_index = (start_stem_index + branch_index) % 10
    return Pillar(stem=STEMS[stem_index], branch=BRANCHES[branch_index])


def compute_year_pillar(reference_year: int) -> Pillar:
    return pillar_from_index((reference_year - 1984) % 60)


def compute_month_pillar(year_stem: str, month_order: int) -> Pillar:
    start_stem_index = ((STEMS.index(year_stem) % 5) * 2 + 2) % 10
    stem_index = (start_stem_index + month_order) % 10
    branch_index = (2 + month_order) % 12
    return Pillar(stem=STEMS[stem_index], branch=BRANCHES[branch_index])


def convert_lunar_to_solar(year: int, month: int, day: int, leap_month: bool) -> tuple[int, int, int]:
    calendar = KoreanLunarCalendar()
    calendar.setLunarDate(year, month, day, leap_month)
    solar = calendar.SolarIsoFormat().split("-")
    return int(solar[0]), int(solar[1]), int(solar[2])


def hidden_stems_for_branch(branch: str) -> list[str]:
    return list(HIDDEN_STEMS[branch])


def compute_relations_matrix(pillars: dict[str, Pillar]) -> list[RelationRow]:
    rows: list[RelationRow] = []
    items = list(pillars.items())
    for index, (left_key, left_value) in enumerate(items):
        for right_key, right_value in items[index + 1 :]:
            branch_relation = BRANCH_RELATIONS.get(
                frozenset({left_value.branch, right_value.branch})
            )
            if branch_relation:
                rows.append(
                    RelationRow(
                        scope="branch",
                        source_key=left_key,
                        target_key=right_key,
                        relation_type=branch_relation[0],
                        strength=branch_relation[1],
                    )
                )
            stem_relation = STEM_RELATIONS.get(frozenset({left_value.stem, right_value.stem}))
            if stem_relation:
                rows.append(
                    RelationRow(
                        scope="stem",
                        source_key=left_key,
                        target_key=right_key,
                        relation_type=stem_relation[0],
                        strength=stem_relation[1],
                    )
                )
    return rows


def _same_polarity(left: str, right: str) -> bool:
    return STEM_YIN_YANG[left] == STEM_YIN_YANG[right]


def ten_god_for(day_stem: str, other_stem: str) -> str:
    day_element = STEM_ELEMENTS[day_stem]
    other_element = STEM_ELEMENTS[other_stem]
    same_polarity = _same_polarity(day_stem, other_stem)

    if day_element == other_element:
        return "friend" if same_polarity else "rob_wealth"
    if GENERATES[day_element] == other_element:
        return "eating_god" if same_polarity else "hurting_officer"
    if CONTROLS[day_element] == other_element:
        return "indirect_wealth" if same_polarity else "direct_wealth"
    if CONTROLS[other_element] == day_element:
        return "seven_killings" if same_polarity else "direct_officer"
    return "indirect_resource" if same_polarity else "direct_resource"


def compute_element_balance(pillars: dict[str, Pillar]) -> dict[str, float]:
    totals = {element: 0.0 for element in ELEMENTS}
    for pillar in pillars.values():
        totals[STEM_ELEMENTS[pillar.stem]] += 1.0
        totals[BRANCH_ELEMENTS[pillar.branch]] += 1.0
        hidden = hidden_stems_for_branch(pillar.branch)
        for idx, stem in enumerate(hidden):
            weight = HIDDEN_STEM_WEIGHTS[idx] if idx < len(HIDDEN_STEM_WEIGHTS) else 0.05
            totals[STEM_ELEMENTS[stem]] += weight
    total_weight = sum(totals.values()) or 1.0
    return {key: round(value / total_weight, 4) for key, value in totals.items()}


def compute_yin_yang_balance(pillars: dict[str, Pillar]) -> float:
    balance = 0.0
    for pillar in pillars.values():
        balance += 1 if STEM_YIN_YANG[pillar.stem] == "yang" else -1
        balance += 1 if pillar.branch in {"Ja", "In", "Jin", "O", "Sin", "Sul"} else -1
    return round(balance / 8.0, 4)


def compute_ten_god_weights(day_stem: str, pillars: dict[str, Pillar]) -> dict[str, float]:
    totals = {
        "friend": 0.0,
        "rob_wealth": 0.0,
        "eating_god": 0.0,
        "hurting_officer": 0.0,
        "indirect_wealth": 0.0,
        "direct_wealth": 0.0,
        "seven_killings": 0.0,
        "direct_officer": 0.0,
        "indirect_resource": 0.0,
        "direct_resource": 0.0,
    }
    for name, pillar in pillars.items():
        if name != "day":
            totals[ten_god_for(day_stem, pillar.stem)] += 1.0
        hidden = hidden_stems_for_branch(pillar.branch)
        for idx, stem in enumerate(hidden):
            weight = HIDDEN_STEM_WEIGHTS[idx] if idx < len(HIDDEN_STEM_WEIGHTS) else 0.05
            totals[ten_god_for(day_stem, stem)] += weight
    total = sum(totals.values()) or 1.0
    return {key: round(value / total, 4) for key, value in totals.items()}


def dominant_elements(element_balance: dict[str, float]) -> tuple[list[str], list[str]]:
    ranked = sorted(element_balance.items(), key=lambda item: item[1], reverse=True)
    unfavorable = [ranked[0][0], ranked[1][0]]
    useful = [ranked[-1][0], ranked[-2][0]]
    return useful, unfavorable


def month_order_from_longitude(longitude: float) -> int:
    normalized = (longitude - 315.0) % 360.0
    return int(floor(normalized / 30.0)) % 12
