# 11. Storage and Lineage

## Storage Roles

### PostgreSQL

- source of truth for charts, runs, events, reports, backtests
- JSONB fields for evidence, state snapshots, policy snapshots

### Redis Streams

- simulation progress events
- report generation progress
- debate execution progress

### Celery

- simulation workers
- report workers
- backtest workers

## Minimum Persistent Entities

- `chart_record`
- `simulation_run`
- `branch_run`
- `event_log`
- `debate_record`
- `report_record`
- `backtest_record`

## event_log Minimum Fields

| Field | Meaning |
| --- | --- |
| `event_id` | unique event id |
| `run_id` | owning run |
| `parent_run_id` | lineage link |
| `timestep` | timeline unit |
| `event_type` | taxonomy event |
| `domain` | primary domain |
| `importance` | 0..100 |
| `confidence` | 0.0..1.0 |
| `evidence_refs` | mandatory evidence array |
| `state_before` | snapshot |
| `state_after` | snapshot |
| `tradeoff` | structured gains/losses |
| `seed` | replay seed |
| `policy_snapshot` | simulation policy |

## Lineage Rules

- baseline run owns the root lineage
- each branch stores `parent_run_id`
- replay requires `run_id + seed + policy_snapshot`
- debate output stores source branch ids
- narrative sections store the worldline ids they summarize

## Retention Rules

- source chart and run records are retained
- ephemeral stream messages may expire
- evidence refs must remain stable for report reproducibility

## Privacy Notes

- raw birth input retention should be minimized
- compiled chart and policy snapshot are the durable simulation inputs
- personally identifying location detail should be stored only when needed
