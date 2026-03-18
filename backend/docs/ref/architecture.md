# Backend Architecture

## Module Map

```text
src/saju_core/constants.py     fixed taxonomy, stems/branches, rule templates
src/saju_core/models.py        shared Pydantic contracts
src/saju_core/time_utils.py    timezone and local mean time normalization
src/saju_core/sexagenary.py    pillar formulas, hidden stems, relations
src/saju_core/solar_terms.py   Skyfield solar longitude and term windows
src/saju_core/chart_engine.py  BirthInput -> ChartCore + FeatureVector
src/saju_core/state_model.py   FeatureVector -> LifeState
src/saju_core/timeline.py      12-month timeline generation
src/saju_core/rule_engine.py   16-rule candidate scoring and acceptance
src/saju_core/simulator.py     baseline monthly orchestration
src/saju_core/storage.py       SQLite dev persistence
src/saju_api/main.py           FastAPI routes and error mapping
```

## Request Flow

```text
POST /simulations
-> compile_chart()
-> build_initial_state()
-> build_monthly_timeline()
-> evaluate_month_rules() x 12
-> save chart/run/events
-> return run_id + policy_snapshot
```

## Contracts

- chart engine returns `ChartCore`, `FeatureVector`, `ValidationMeta`
- simulation stores baseline run only
- accepted events include `rule` evidence and at least one non-rule evidence
- monthly mode is the only implemented timeline resolution in this workspace phase
