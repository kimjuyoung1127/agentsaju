# 10. API Contract

## API Principles

- REST first
- async operations return resource ids and status
- all run-related payloads include `seed` and `policy_snapshot`

## Endpoints

### `POST /charts/compile`

Compiles a chart and feature vector from `BirthInput`.

Request:

```json
{
  "birth_input": {
    "calendar": "solar",
    "birth_datetime": "1990-10-10T14:30:00+09:00",
    "timezone": "Asia/Seoul",
    "location": {
      "city": "Seoul",
      "longitude": 126.978,
      "latitude": 37.5665
    },
    "apply_local_mean_time": false,
    "early_zi_time": false
  }
}
```

Response:

```json
{
  "chart_core": {},
  "feature_vector": {},
  "validation_meta": {}
}
```

### `POST /simulations`

Creates a baseline simulation.

Required fields:

- `birth_input`
- `goal`
- `constraints`
- `seed`
- `horizon_year`

Response contains:

- `run_id`
- `status`
- `timeline_mode`
- `policy_snapshot`

### `POST /simulations/{id}/branches`

Creates one or more branch runs from a baseline run.

Required fields:

- `choices`
- `seed`

Response contains branch ids and async status.

### `GET /simulations/{id}`

Returns run metadata, status, final state, top worldline summary.

### `GET /simulations/{id}/events`

Returns ordered accepted events with evidence refs.

### `POST /debates/{simulation_id}`

Runs grounded multi-agent debate across selected branch outcomes.

Request:

- `branch_ids`
- optional `top_n`

Response:

- ranked worldlines
- debate messages
- judge summary

### `GET /reports/{simulation_id}`

Returns free summary and, when authorized, paid detail.

### `POST /backtests`

Creates backtest candidates for a past year and accepts user labels.

## Error Contract

Error payload shape:

```json
{
  "error": {
    "code": "validation_error",
    "message": "longitude is required when apply_local_mean_time is true",
    "details": {}
  }
}
```

## Async Status

Allowed statuses:

- `pending`
- `running`
- `completed`
- `failed`

## ID and Lineage Rules

- `run_id` is unique per run
- `parent_run_id` is null for baseline runs
- `seed` is required and exposed in internal responses
- `policy_snapshot` is returned for debug and replay use
