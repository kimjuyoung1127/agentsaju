from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .constants import DEFAULT_TIMEZONE


class Location(BaseModel):
    city: str | None = None
    longitude: float
    latitude: float | None = None


class BirthInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calendar: Literal["solar", "lunar"] = "solar"
    birth_datetime: datetime
    timezone: str = DEFAULT_TIMEZONE
    location: Location | None = None
    leap_month: bool = False
    apply_local_mean_time: bool = False
    early_zi_time: bool = False
    gender: str | None = None

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        if not value or "/" not in value:
            raise ValueError("unsupported timezone string")
        return value


class Goal(BaseModel):
    category: Literal["career", "relationship", "wealth", "health"]
    question: str


class Constraints(BaseModel):
    must_avoid: list[str] = Field(default_factory=list)


class Pillar(BaseModel):
    stem: str
    branch: str


class RelationRow(BaseModel):
    scope: Literal["stem", "branch", "timeline"]
    source_key: str
    target_key: str
    relation_type: str
    strength: float


class ChartCore(BaseModel):
    pillars: dict[str, Pillar]
    hidden_stems: dict[str, list[str]]
    day_master: str
    corrections: dict[str, Any]
    policy_snapshot: dict[str, Any]


class FeatureVector(BaseModel):
    element_balance: dict[str, float]
    yin_yang_balance: float
    ten_gods: dict[str, float]
    relations_matrix: list[RelationRow]
    useful_signals: list[str]
    unfavorable_signals: list[str]


class ValidationMeta(BaseModel):
    engine_version: str
    policy_snapshot: dict[str, Any]
    normalized_birth_datetime: str
    kasi_comparison_status: str


class LifeState(BaseModel):
    career: float
    relationship: float
    wealth: float
    health: float
    stress: float
    momentum: float
    support: float
    risk_exposure: float


class TimelineFactor(BaseModel):
    mode: Literal["monthly", "weekly"] = "monthly"
    timestep: str
    daewoon: dict[str, Any]
    sewoon: dict[str, Any]
    period_factor: dict[str, Any]
    relations: list[RelationRow]


class EvidenceRef(BaseModel):
    ref_id: str
    source_type: str
    source_key: str
    summary: str


class EventCandidate(BaseModel):
    event_id: str
    event_type: str
    domain: Literal["career", "relationship", "wealth", "health"]
    timestep: str
    impact_vector: dict[str, float]
    confidence: float
    importance: int
    tradeoff: dict[str, Any]
    evidence_refs: list[EvidenceRef]
    state_before: LifeState
    state_after: LifeState


class CompileChartResponse(BaseModel):
    chart_core: ChartCore
    feature_vector: FeatureVector
    validation_meta: ValidationMeta


class SimulationRequest(BaseModel):
    birth_input: BirthInput
    goal: Goal
    constraints: Constraints
    seed: int
    horizon_year: int


class SimulationCreateResponse(BaseModel):
    run_id: str
    status: Literal["pending", "running", "completed", "failed"]
    timeline_mode: Literal["monthly", "weekly"]
    policy_snapshot: dict[str, Any]


class SimulationGetResponse(BaseModel):
    run_id: str
    status: Literal["pending", "running", "completed", "failed"]
    timeline_mode: Literal["monthly", "weekly"]
    policy_snapshot: dict[str, Any]
    parent_run_id: str | None = None
    seed: int
    final_state: LifeState
    worldline_summary: str


class ErrorPayload(BaseModel):
    error: dict[str, Any]
