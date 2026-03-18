from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from .models import CompileChartResponse, EventCandidate, LifeState, SimulationGetResponse


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS chart_record (
    chart_id TEXT PRIMARY KEY,
    birth_input_ref TEXT,
    chart_core TEXT NOT NULL,
    feature_vector TEXT NOT NULL,
    validation_meta TEXT NOT NULL,
    policy_snapshot TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS simulation_run (
    run_id TEXT PRIMARY KEY,
    chart_id TEXT NOT NULL,
    parent_run_id TEXT,
    seed INTEGER NOT NULL,
    timeline_mode TEXT NOT NULL,
    scenario_config TEXT NOT NULL,
    policy_snapshot TEXT NOT NULL,
    status TEXT NOT NULL,
    final_state TEXT NOT NULL,
    worldline_summary TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS event_log (
    event_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    parent_run_id TEXT,
    timestep TEXT NOT NULL,
    event_type TEXT NOT NULL,
    domain TEXT NOT NULL,
    importance INTEGER NOT NULL,
    confidence REAL NOT NULL,
    evidence_refs TEXT NOT NULL,
    state_before TEXT NOT NULL,
    state_after TEXT NOT NULL,
    tradeoff TEXT NOT NULL,
    impact_vector TEXT NOT NULL,
    seed INTEGER NOT NULL,
    policy_snapshot TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class SQLiteStorage:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.executescript(SCHEMA_SQL)

    def save_chart(self, compiled: CompileChartResponse) -> str:
        chart_id = str(uuid4())
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO chart_record (
                    chart_id, birth_input_ref, chart_core, feature_vector,
                    validation_meta, policy_snapshot
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    chart_id,
                    None,
                    json.dumps(compiled.chart_core.model_dump()),
                    json.dumps(compiled.feature_vector.model_dump()),
                    json.dumps(compiled.validation_meta.model_dump()),
                    json.dumps(compiled.chart_core.policy_snapshot),
                ),
            )
        return chart_id

    def save_simulation(
        self,
        chart_id: str,
        run_payload: dict[str, object],
        final_state: LifeState,
        worldline_summary: str,
        events: list[EventCandidate],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO simulation_run (
                    run_id, chart_id, parent_run_id, seed, timeline_mode,
                    scenario_config, policy_snapshot, status, final_state, worldline_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_payload["run_id"],
                    chart_id,
                    run_payload["parent_run_id"],
                    run_payload["seed"],
                    run_payload["timeline_mode"],
                    json.dumps(run_payload["scenario_config"]),
                    json.dumps(run_payload["policy_snapshot"]),
                    run_payload["status"],
                    json.dumps(final_state.model_dump()),
                    worldline_summary,
                ),
            )
            for event in events:
                connection.execute(
                    """
                    INSERT INTO event_log (
                        event_id, run_id, parent_run_id, timestep, event_type, domain,
                        importance, confidence, evidence_refs, state_before, state_after,
                        tradeoff, impact_vector, seed, policy_snapshot
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_id,
                        run_payload["run_id"],
                        run_payload["parent_run_id"],
                        event.timestep,
                        event.event_type,
                        event.domain,
                        event.importance,
                        event.confidence,
                        json.dumps([ref.model_dump() for ref in event.evidence_refs]),
                        json.dumps(event.state_before.model_dump()),
                        json.dumps(event.state_after.model_dump()),
                        json.dumps(event.tradeoff),
                        json.dumps(event.impact_vector),
                        run_payload["seed"],
                        json.dumps(run_payload["policy_snapshot"]),
                    ),
                )

    def get_simulation(self, run_id: str) -> SimulationGetResponse | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT run_id, parent_run_id, seed, timeline_mode, status,
                       policy_snapshot, final_state, worldline_summary
                FROM simulation_run WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return SimulationGetResponse(
            run_id=row["run_id"],
            parent_run_id=row["parent_run_id"],
            seed=row["seed"],
            timeline_mode=row["timeline_mode"],
            status=row["status"],
            policy_snapshot=json.loads(row["policy_snapshot"]),
            final_state=LifeState(**json.loads(row["final_state"])),
            worldline_summary=row["worldline_summary"],
        )

    def get_events(self, run_id: str) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_id, event_type, domain, timestep, importance, confidence,
                       evidence_refs, tradeoff, impact_vector
                FROM event_log
                WHERE run_id = ?
                ORDER BY timestep ASC, importance DESC, confidence DESC
                """,
                (run_id,),
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "domain": row["domain"],
                "timestep": row["timestep"],
                "impact_vector": json.loads(row["impact_vector"]),
                "confidence": row["confidence"],
                "importance": row["importance"],
                "tradeoff": json.loads(row["tradeoff"]),
                "evidence_refs": json.loads(row["evidence_refs"]),
            }
            for row in rows
        ]
