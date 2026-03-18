from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from saju_core.chart_engine import compile_chart
from saju_core.errors import SajuValidationError
from saju_core.models import (
    BirthInput,
    CompileChartResponse,
    ErrorPayload,
    SimulationCreateResponse,
    SimulationGetResponse,
    SimulationRequest,
)
from saju_core.simulator import run_baseline_simulation
from saju_core.storage import SQLiteStorage


def _create_storage() -> SQLiteStorage:
    db_path = Path(__file__).resolve().parents[2] / "data" / "saju-dev.db"
    return SQLiteStorage(db_path)


app = FastAPI(title="Saju Monthly Core", version="0.1.0")
storage = _create_storage()


@app.exception_handler(SajuValidationError)
async def validation_exception_handler(_, exc: SajuValidationError) -> JSONResponse:
    payload = ErrorPayload(error={"code": exc.code, "message": exc.message, "details": {}})
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.post("/charts/compile", response_model=CompileChartResponse)
def post_compile_chart(payload: dict[str, BirthInput]) -> CompileChartResponse:
    birth_input = BirthInput.model_validate(payload["birth_input"])
    compiled = compile_chart(birth_input)
    storage.save_chart(compiled)
    return compiled


@app.post("/simulations", response_model=SimulationCreateResponse)
def post_simulation(request: SimulationRequest) -> SimulationCreateResponse:
    result = run_baseline_simulation(request)
    chart_id = storage.save_chart(result["chart"])
    storage.save_simulation(
        chart_id=chart_id,
        run_payload=result["run"],
        final_state=result["final_state"],
        worldline_summary=result["worldline_summary"],
        events=result["events"],
    )
    return SimulationCreateResponse(
        run_id=result["run"]["run_id"],
        status=result["run"]["status"],
        timeline_mode=result["run"]["timeline_mode"],
        policy_snapshot=result["run"]["policy_snapshot"],
    )


@app.get("/simulations/{run_id}", response_model=SimulationGetResponse)
def get_simulation(run_id: str) -> SimulationGetResponse:
    result = storage.get_simulation(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    return result


@app.get("/simulations/{run_id}/events")
def get_simulation_events(run_id: str) -> list[dict[str, object]]:
    simulation = storage.get_simulation(run_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail="simulation not found")
    return storage.get_events(run_id)
