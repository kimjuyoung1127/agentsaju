from __future__ import annotations

from .constants import GOAL_DOMAIN_MAP, STATE_DEFAULTS
from .models import Constraints, FeatureVector, Goal, LifeState
from .time_utils import clamp


def build_initial_state(
    feature_vector: FeatureVector,
    goal: Goal,
    constraints: Constraints,
) -> LifeState:
    state = dict(STATE_DEFAULTS)
    authority = feature_vector.ten_gods.get("direct_officer", 0.0) + feature_vector.ten_gods.get(
        "seven_killings", 0.0
    )
    wealth = feature_vector.ten_gods.get("direct_wealth", 0.0) + feature_vector.ten_gods.get(
        "indirect_wealth", 0.0
    )
    resource = feature_vector.ten_gods.get(
        "direct_resource", 0.0
    ) + feature_vector.ten_gods.get("indirect_resource", 0.0)
    output = feature_vector.ten_gods.get("eating_god", 0.0) + feature_vector.ten_gods.get(
        "hurting_officer", 0.0
    )
    peer = feature_vector.ten_gods.get("friend", 0.0) + feature_vector.ten_gods.get("rob_wealth", 0.0)
    imbalance = max(feature_vector.element_balance.values()) - min(feature_vector.element_balance.values())

    state["career"] += authority * 10 + output * 8
    state["stress"] += authority * 4 + max(imbalance - 0.15, 0) * 20
    state["wealth"] += wealth * 10 - peer * 4
    state["risk_exposure"] += wealth * 6
    state["health"] += resource * 8 - max(imbalance - 0.15, 0) * 20
    state["support"] += resource * 8
    state["momentum"] += output * 10
    state["relationship"] += peer * 8

    primary, secondary = GOAL_DOMAIN_MAP[goal.category]
    state[primary] += (state[primary] - STATE_DEFAULTS[primary]) * 0.25
    state[secondary] += (state[secondary] - STATE_DEFAULTS[secondary]) * 0.1

    if "debt" in constraints.must_avoid:
        state["risk_exposure"] += 5
    if "conflict" in constraints.must_avoid:
        state["stress"] += 5

    return LifeState(**{key: round(clamp(value), 2) for key, value in state.items()})
