# Getting Started

## Install

```bash
cd backend
python -m pip install -e .[dev]
```

## Run Tests

```bash
python -m pytest -q
```

## Run API

```bash
uvicorn saju_api.main:app --app-dir src --reload
```

## Example Requests

### Compile Chart

```bash
curl -X POST http://127.0.0.1:8000/charts/compile ^
  -H "Content-Type: application/json" ^
  -d "{\"birth_input\":{\"calendar\":\"solar\",\"birth_datetime\":\"1990-10-10T14:30:00+09:00\",\"timezone\":\"Asia/Seoul\"}}"
```

### Run Monthly Simulation

```bash
curl -X POST http://127.0.0.1:8000/simulations ^
  -H "Content-Type: application/json" ^
  -d "{\"birth_input\":{\"calendar\":\"solar\",\"birth_datetime\":\"1990-10-10T14:30:00+09:00\",\"timezone\":\"Asia/Seoul\"},\"goal\":{\"category\":\"career\",\"question\":\"Should I move this year?\"},\"constraints\":{\"must_avoid\":[\"debt\",\"conflict\"]},\"seed\":1024,\"horizon_year\":2026}"
```
