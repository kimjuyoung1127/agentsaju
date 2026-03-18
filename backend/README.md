# saju-monthly-core

Python backend for the deterministic saju chart engine and monthly baseline simulator.

## Documentation

This workspace follows the same document-governance shape used in `unityctl`.

- `docs/ref/` : long-lived reference docs
- `docs/status/` : current implementation and verification status
- `docs/daily/` : dated work logs
- `docs/weekly/` : weekly rollups
- `docs/DEVELOPMENT.md` : one-page current development summary

Start here:

- `docs/DEVELOPMENT.md`
- `docs/status/PROJECT-STATUS.md`
- `docs/ref/getting-started.md`
- `docs/ref/architecture.md`

## Quick Start

```bash
cd backend
python -m pip install -e .[dev]
python -m pytest -q
uvicorn saju_api.main:app --app-dir src --reload
```

## API

- `POST /charts/compile`
- `POST /simulations`
- `GET /simulations/{id}`
- `GET /simulations/{id}/events`

## Current Scope

- Deterministic `BirthInput -> ChartCore -> FeatureVector`
- `LifeState` initialization
- 12-step monthly timeline generation
- 16-rule baseline event generation
- SQLite dev persistence
- FastAPI sync endpoints for local development

Excluded in this workspace phase:

- weekly zoom
- branch runs
- debate/narrative layers
- websocket delivery
- Celery/Redis worker orchestration
