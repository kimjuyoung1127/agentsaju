from __future__ import annotations

from copy import deepcopy
from typing import Callable
from uuid import uuid5, NAMESPACE_URL

from .constants import EVENT_DOMAIN, GOAL_DOMAIN_MAP, RULE_IMPACTS, RULE_POSTURES
from .models import Constraints, EvidenceRef, EventCandidate, FeatureVector, Goal, LifeState, TimelineFactor
from .time_utils import clamp


def _aggregate_scores(feature_vector: FeatureVector) -> dict[str, float]:
    ten_gods = feature_vector.ten_gods
    return {
        "authority": ten_gods.get("direct_officer", 0.0) + ten_gods.get("seven_killings", 0.0),
        "wealth": ten_gods.get("direct_wealth", 0.0) + ten_gods.get("indirect_wealth", 0.0),
        "resource": ten_gods.get("direct_resource", 0.0) + ten_gods.get("indirect_resource", 0.0),
        "output": ten_gods.get("eating_god", 0.0) + ten_gods.get("hurting_officer", 0.0),
        "peer": ten_gods.get("friend", 0.0) + ten_gods.get("rob_wealth", 0.0),
        "imbalance": max(feature_vector.element_balance.values()) - min(feature_vector.element_balance.values()),
    }


def _domain_relevance(goal: Goal, domain: str) -> float:
    primary, secondary = GOAL_DOMAIN_MAP[goal.category]
    if domain == primary:
        return 1.0
    if domain == secondary:
        return 0.7
    return 0.4


def _state_consistency(event_type: str, state: LifeState) -> float:
    consistency = 0.4
    if event_type in {"RELATIONSHIP_CONFLICT", "BURNOUT_RISK"} and state.stress > 75:
        consistency += 0.4
    if event_type in {"HEALTH_RECOVERY", "RELATIONSHIP_BOND"} and state.support > 80:
        consistency += 0.4
    if event_type in {"WEALTH_LEAK", "INVESTMENT_VOLATILITY"} and state.risk_exposure > 75:
        consistency += 0.4
    if event_type.startswith("HEALTH_") and state.health < 20:
        consistency += 0.2
    return min(1.0, consistency)


def _signal_alignment(event_type: str, scores: dict[str, float], timeline_pressure: dict[str, float]) -> float:
    if event_type in {"CAREER_MOVE", "SKILL_GAIN"}:
        return min(1.0, scores["output"] * 0.7 + timeline_pressure["career"] * 0.6)
    if event_type == "CAREER_STALL":
        return min(1.0, (1 - scores["authority"]) * 0.6 + (1 - timeline_pressure["career"]) * 0.7)
    if event_type == "AUTHORITY_PRESSURE":
        return min(1.0, scores["authority"] * 0.8 + timeline_pressure["career"] * 0.5)
    if event_type in {"RELATIONSHIP_BOND", "RECONCILIATION_WINDOW"}:
        return min(1.0, scores["peer"] * 0.7 + timeline_pressure["relationship"] * 0.6)
    if event_type in {"RELATIONSHIP_CONFLICT", "SOCIAL_FATIGUE"}:
        return min(1.0, scores["peer"] * 0.5 + scores["imbalance"] * 0.8)
    if event_type in {"WEALTH_GAIN", "ASSET_LOCK"}:
        return min(1.0, scores["wealth"] * 0.7 + timeline_pressure["wealth"] * 0.6)
    if event_type in {"WEALTH_LEAK", "INVESTMENT_VOLATILITY"}:
        return min(1.0, scores["wealth"] * 0.4 + scores["imbalance"] * 0.6 + state_like_pressure(timeline_pressure) * 0.4)
    return min(1.0, scores["resource"] * 0.7 + timeline_pressure["health"] * 0.6)


def state_like_pressure(timeline_pressure: dict[str, float]) -> float:
    return max(timeline_pressure["wealth"], timeline_pressure["health"])


def _apply_impact(
    state: LifeState,
    event_type: str,
    constraints: Constraints,
) -> LifeState:
    updated = state.model_dump()
    impacts = deepcopy(RULE_IMPACTS[event_type])
    if event_type in {"WEALTH_LEAK", "INVESTMENT_VOLATILITY"} and "debt" in constraints.must_avoid:
        impacts["wealth"] = impacts.get("wealth", 0) * 1.2
    if event_type in {"RELATIONSHIP_CONFLICT", "SOCIAL_FATIGUE"} and "conflict" in constraints.must_avoid:
        impacts["relationship"] = impacts.get("relationship", 0) * 1.2

    if updated["support"] > 80 and impacts.get("stress", 0) > 0:
        impacts["stress"] *= 0.8
    if updated["risk_exposure"] > 75:
        if impacts.get("wealth", 0) < 0:
            impacts["wealth"] *= 1.15
        if impacts.get("relationship", 0) < 0:
            impacts["relationship"] *= 1.15

    for key, value in impacts.items():
        updated[key] = clamp(updated[key] + value)

    if updated["health"] < 20:
        updated["stress"] = clamp(updated["stress"] + 5)
    return LifeState(**{key: round(value, 2) for key, value in updated.items()})


def _build_tradeoff(event_type: str) -> dict[str, object]:
    domain = EVENT_DOMAIN[event_type]
    gains = [f"{domain} momentum"] if event_type not in {"WEALTH_LEAK", "CAREER_STALL", "HEALTH_ALERT"} else []
    costs = ["higher stress"] if RULE_IMPACTS[event_type].get("stress", 0) > 0 else []
    risks = []
    if domain == "wealth":
        risks.append("relationship strain")
    if domain == "career":
        risks.append("fatigue if prolonged")
    if domain == "health":
        risks.append("reduced resilience")
    return {
        "immediate_gain": gains,
        "immediate_cost": costs,
        "downstream_risk": risks,
        "recommended_posture": RULE_POSTURES[event_type],
    }


def _normalized_abs_impact(event_type: str) -> float:
    total = sum(abs(value) for value in RULE_IMPACTS[event_type].values())
    return min(1.0, total / 30.0)


def _novelty(event_type: str, seen_events: set[str]) -> float:
    return 1.0 if event_type not in seen_events else 0.35


def _candidate(
    run_key: str,
    event_type: str,
    timestep: str,
    goal: Goal,
    constraints: Constraints,
    state_before: LifeState,
    state_after: LifeState,
    rule_strength: float,
    signal_alignment: float,
    timeline_pressure: dict[str, float],
    seen_events: set[str],
) -> EventCandidate:
    domain = EVENT_DOMAIN[event_type]
    timeline_pressure_value = timeline_pressure[domain]
    state_consistency = _state_consistency(event_type, state_before)
    confidence = round(
        min(1.0, max(0.0, 0.5 * rule_strength + 0.3 * signal_alignment + 0.2 * state_consistency)),
        2,
    )
    importance = round(
        min(
            100,
            max(
                0,
                35 * _normalized_abs_impact(event_type)
                + 25 * _domain_relevance(goal, domain)
                + 20 * timeline_pressure_value
                + 20 * _novelty(event_type, seen_events),
            ),
        )
    )
    evidence_refs = [
        EvidenceRef(
            ref_id=f"ev-rule-{event_type.lower()}",
            source_type="rule",
            source_key=event_type,
            summary=f"{event_type} rule triggered",
        ),
        EvidenceRef(
            ref_id=f"ev-time-{timestep}",
            source_type="timeline",
            source_key=timestep,
            summary=f"timeline pressure {timeline_pressure_value:.2f} influenced {domain}",
        ),
    ]
    if event_type in {"AUTHORITY_PRESSURE", "BURNOUT_RISK", "RELATIONSHIP_CONFLICT"}:
        evidence_refs.append(
            EvidenceRef(
                ref_id=f"ev-state-{timestep}-{event_type.lower()}",
                source_type="state",
                source_key="life_state",
                summary=f"state stress={state_before.stress:.1f}, support={state_before.support:.1f}",
            )
        )
    return EventCandidate(
        event_id=str(uuid5(NAMESPACE_URL, f"{run_key}:{timestep}:{event_type}")),
        event_type=event_type,
        domain=domain,
        timestep=timestep,
        impact_vector={key: float(value) for key, value in RULE_IMPACTS[event_type].items()},
        confidence=confidence,
        importance=importance,
        tradeoff=_build_tradeoff(event_type),
        evidence_refs=evidence_refs,
        state_before=state_before,
        state_after=state_after,
    )


def evaluate_month_rules(
    run_key: str,
    feature_vector: FeatureVector,
    goal: Goal,
    constraints: Constraints,
    state: LifeState,
    timeline_factor: TimelineFactor,
    seen_events: set[str],
) -> list[EventCandidate]:
    scores = _aggregate_scores(feature_vector)
    timeline_pressure = timeline_factor.period_factor["domain_pressure"]
    generated: list[EventCandidate] = []
    rules: list[tuple[str, Callable[[], float]]] = [
        ("CAREER_MOVE", lambda: min(1.0, scores["output"] * 0.8 + timeline_pressure["career"] * 0.7)),
        (
            "CAREER_STALL",
            lambda: min(1.0, (1 - scores["authority"]) * 0.7 + (1 - timeline_pressure["career"]) * 0.7),
        ),
        (
            "AUTHORITY_PRESSURE",
            lambda: min(1.0, scores["authority"] * 0.8 + (state.stress / 100.0) * 0.6),
        ),
        ("SKILL_GAIN", lambda: min(1.0, scores["output"] * 0.6 + scores["resource"] * 0.4 + 0.2)),
        ("RELATIONSHIP_BOND", lambda: min(1.0, scores["peer"] * 0.7 + timeline_pressure["relationship"] * 0.7)),
        (
            "RELATIONSHIP_CONFLICT",
            lambda: min(1.0, scores["imbalance"] * 0.8 + (state.stress / 100.0) * 0.7),
        ),
        (
            "RECONCILIATION_WINDOW",
            lambda: min(1.0, scores["peer"] * 0.5 + (1 - state.stress / 100.0) * 0.5 + 0.15),
        ),
        ("SOCIAL_FATIGUE", lambda: min(1.0, scores["peer"] * 0.6 + (1 - state.support / 100.0) * 0.6)),
        ("WEALTH_GAIN", lambda: min(1.0, scores["wealth"] * 0.8 + timeline_pressure["wealth"] * 0.7)),
        (
            "WEALTH_LEAK",
            lambda: min(
                1.0,
                scores["imbalance"] * 0.5
                + (1 - state.support / 100.0) * 0.4
                + (1 - timeline_pressure["wealth"]) * 0.5,
            ),
        ),
        (
            "INVESTMENT_VOLATILITY",
            lambda: min(1.0, scores["wealth"] * 0.5 + (state.risk_exposure / 100.0) * 0.7),
        ),
        (
            "ASSET_LOCK",
            lambda: min(1.0, scores["wealth"] * 0.5 + (state.momentum / 100.0) * 0.2 + 0.2),
        ),
        (
            "HEALTH_RECOVERY",
            lambda: min(1.0, scores["resource"] * 0.8 + (state.support / 100.0) * 0.5),
        ),
        (
            "HEALTH_ALERT",
            lambda: min(1.0, scores["imbalance"] * 0.7 + (state.stress / 100.0) * 0.5),
        ),
        (
            "BURNOUT_RISK",
            lambda: min(
                1.0,
                (state.stress / 100.0) * 0.8 + scores["authority"] * 0.4 + scores["output"] * 0.3,
            ),
        ),
        (
            "ENERGY_DROP",
            lambda: min(1.0, scores["imbalance"] * 0.5 + (state.momentum / 100.0) * 0.2 + 0.25),
        ),
    ]

    for event_type, strength_fn in rules:
        rule_strength = round(strength_fn(), 4)
        if rule_strength < 0.45:
            continue
        state_after = _apply_impact(state, event_type, constraints)
        signal_alignment = _signal_alignment(event_type, scores, timeline_pressure)
        candidate = _candidate(
            run_key=run_key,
            event_type=event_type,
            timestep=timeline_factor.timestep,
            goal=goal,
            constraints=constraints,
            state_before=state,
            state_after=state_after,
            rule_strength=rule_strength,
            signal_alignment=signal_alignment,
            timeline_pressure=timeline_pressure,
            seen_events=seen_events,
        )
        if candidate.confidence >= 0.55:
            generated.append(candidate)

    generated.sort(key=lambda item: (-item.importance, -item.confidence, item.event_type))
    deduped: list[EventCandidate] = []
    seen_types: set[str] = set()
    for candidate in generated:
        dedupe_key = f"{candidate.event_type}:{candidate.timestep}"
        if dedupe_key in seen_types:
            continue
        seen_types.add(dedupe_key)
        deduped.append(candidate)
        if len(deduped) == 3:
            break
    return deduped
