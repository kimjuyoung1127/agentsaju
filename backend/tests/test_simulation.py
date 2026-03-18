from __future__ import annotations

from collections import Counter

from saju_core.models import BirthInput, Constraints, Goal, SimulationRequest
from saju_core.simulator import run_baseline_simulation


def _request() -> SimulationRequest:
    return SimulationRequest(
        birth_input=BirthInput(
            calendar="solar",
            birth_datetime="1990-10-10T14:30:00+09:00",
            timezone="Asia/Seoul",
        ),
        goal=Goal(category="career", question="Should I move this year?"),
        constraints=Constraints(must_avoid=["debt", "conflict"]),
        seed=1024,
        horizon_year=2026,
    )


def test_simulation_is_deterministic() -> None:
    first = run_baseline_simulation(_request())
    second = run_baseline_simulation(_request())

    first_events = [
        (event.timestep, event.event_type, event.importance, event.confidence)
        for event in first["events"]
    ]
    second_events = [
        (event.timestep, event.event_type, event.importance, event.confidence)
        for event in second["events"]
    ]
    assert first_events == second_events
    assert first["final_state"].model_dump() == second["final_state"].model_dump()


def test_simulation_contracts() -> None:
    result = run_baseline_simulation(_request())
    assert len(result["timeline"]) == 12

    counts = Counter(event.timestep for event in result["events"])
    assert all(count <= 3 for count in counts.values())
    for event in result["events"]:
        assert 0 <= event.importance <= 100
        assert 0.0 <= event.confidence <= 1.0
        assert any(ref.source_type == "rule" for ref in event.evidence_refs)
        assert any(ref.source_type in {"timeline", "feature", "state"} for ref in event.evidence_refs)
