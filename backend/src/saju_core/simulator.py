from __future__ import annotations

from uuid import uuid4

from .chart_engine import compile_chart
from .models import EventCandidate, Goal, LifeState, SimulationRequest
from .rule_engine import evaluate_month_rules
from .state_model import build_initial_state
from .timeline import build_monthly_timeline


def _worldline_summary(events: list[EventCandidate], final_state: LifeState, goal: Goal) -> str:
    if not events:
        return f"Stable monthly baseline with limited {goal.category} volatility."
    top_event = max(events, key=lambda event: event.importance)
    goal_value = getattr(final_state, goal.category)
    return (
        f"Top signal is {top_event.event_type} around {top_event.timestep}; "
        f"ending {goal.category} state is {goal_value:.1f}."
    )


def run_baseline_simulation(
    request: SimulationRequest,
) -> dict[str, object]:
    compiled = compile_chart(request.birth_input)
    life_state = build_initial_state(compiled.feature_vector, request.goal, request.constraints)
    policy_snapshot = {
        "simulation_version": "sim-v1",
        "accepted_event_limit_monthly": 3,
        "accepted_event_limit_weekly": 5,
    }
    timeline = build_monthly_timeline(compiled.chart_core, request.horizon_year, policy_snapshot)
    run_id = str(uuid4())
    events: list[EventCandidate] = []
    seen_events: set[str] = set()
    current_state = life_state
    for factor in timeline:
        month_events = evaluate_month_rules(
            run_key=f"{request.seed}:{factor.timestep}",
            feature_vector=compiled.feature_vector,
            goal=request.goal,
            constraints=request.constraints,
            state=current_state,
            timeline_factor=factor,
            seen_events=seen_events,
        )
        for event in month_events:
            current_state = event.state_after
            seen_events.add(event.event_type)
        events.extend(month_events)

    return {
        "run": {
            "run_id": run_id,
            "parent_run_id": None,
            "seed": request.seed,
            "timeline_mode": "monthly",
            "scenario_config": {
                "goal": request.goal.model_dump(),
                "constraints": request.constraints.model_dump(),
                "horizon_year": request.horizon_year,
            },
            "policy_snapshot": policy_snapshot,
            "status": "completed",
        },
        "chart": compiled,
        "initial_state": life_state,
        "timeline": timeline,
        "final_state": current_state,
        "events": events,
        "worldline_summary": _worldline_summary(events, current_state, request.goal),
    }
