from __future__ import annotations

from saju_core.chart_engine import compile_chart
from saju_core.errors import SajuValidationError
from saju_core.models import BirthInput
from saju_core.sexagenary import convert_lunar_to_solar
from saju_core.solar_terms import find_solar_longitude_ingress


def test_chart_cases_are_deterministic(chart_cases: list[dict[str, object]]) -> None:
    for case in chart_cases:
        birth_input = BirthInput.model_validate(case["birth_input"])
        first = compile_chart(birth_input)
        second = compile_chart(birth_input)
        assert first.model_dump() == second.model_dump()

        expected = case["expected"]
        assert first.validation_meta.normalized_birth_datetime == expected["normalized_birth_datetime"]
        assert first.chart_core.day_master == expected["day_master"]
        assert first.chart_core.pillars["year"].model_dump() == expected["year_pillar"]
        assert first.chart_core.pillars["month"].model_dump() == expected["month_pillar"]
        assert first.chart_core.pillars["day"].model_dump() == expected["day_pillar"]


def test_lunar_fixture_matches_local_regression(kasi_regression: dict[str, object]) -> None:
    example = kasi_regression["solar_to_lunar_examples"][0]
    year, month, day = convert_lunar_to_solar(
        example["lunar_year"],
        example["lunar_month"],
        example["lunar_day"],
        example["leap_month"],
    )
    assert f"{year:04d}-{month:02d}-{day:02d}" == example["solar_date"]


def test_solar_term_fixtures_produce_ordered_instants(kasi_regression: dict[str, object]) -> None:
    ipchun = find_solar_longitude_ingress(
        kasi_regression["solar_term_examples"][0]["year"],
        kasi_regression["solar_term_examples"][0]["target_longitude"],
    )
    cheongmyeong = find_solar_longitude_ingress(
        kasi_regression["solar_term_examples"][1]["year"],
        kasi_regression["solar_term_examples"][1]["target_longitude"],
    )
    assert ipchun.isoformat().startswith("2026-02")
    assert cheongmyeong > ipchun


def test_early_zi_changes_day_pillar() -> None:
    base = BirthInput(
        calendar="solar",
        birth_datetime="2000-01-01T23:30:00+09:00",
        timezone="Asia/Seoul",
        early_zi_time=False,
    )
    shifted = base.model_copy(update={"early_zi_time": True})
    base_result = compile_chart(base)
    shifted_result = compile_chart(shifted)
    assert base_result.chart_core.pillars["day"] != shifted_result.chart_core.pillars["day"]


def test_local_mean_time_can_roll_previous_day() -> None:
    birth_input = BirthInput(
        calendar="solar",
        birth_datetime="1990-10-10T00:10:00+09:00",
        timezone="Asia/Seoul",
        apply_local_mean_time=True,
        location={"longitude": 120.0, "latitude": 37.5},
    )
    result = compile_chart(birth_input)
    assert result.validation_meta.normalized_birth_datetime.startswith("1990-10-09T23:10")


def test_missing_longitude_rejected() -> None:
    birth_input = BirthInput(
        calendar="solar",
        birth_datetime="1990-10-10T14:30:00+09:00",
        timezone="Asia/Seoul",
        apply_local_mean_time=True,
    )
    try:
        compile_chart(birth_input)
    except SajuValidationError as exc:
        assert "longitude is required" in exc.message
    else:
        raise AssertionError("expected validation error")
