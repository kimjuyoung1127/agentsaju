# backend 프로젝트 상태

최종 업데이트: 2026-03-18 (KST)  
기준 문서: `docs/DEVELOPMENT.md`, `docs/ref/architecture.md`

## 현재 Phase

- **Phase 1A**: 완료
  - chart engine
  - feature extraction
  - state initialization
- **Phase 1B**: 완료
  - monthly timeline
  - rule engine
  - baseline simulator
- **Phase 1C**: 완료
  - FastAPI endpoints
  - SQLite dev persistence
  - pytest fixtures and smoke coverage
- **후속 Phase**: 미시작
  - weekly zoom
  - branch runs
  - debate/narrative
  - async worker/websocket

## 라이브 구현 상태

| 기능 | 상태 | 비고 |
|------|------|------|
| `POST /charts/compile` | ✅ | deterministic chart + feature + validation_meta |
| `POST /simulations` | ✅ | sync baseline monthly simulation, stored as completed |
| `GET /simulations/{id}` | ✅ | run metadata + final state + summary |
| `GET /simulations/{id}/events` | ✅ | ordered accepted events |
| lunar input | ✅ | local fixture regression included |
| local mean time | ✅ | longitude 기반 deterministic correction |
| early-zi policy | ✅ | `23:00~23:59` next-day day pillar support |

## 자동화 검증

| 항목 | 상태 | 비고 |
|------|------|------|
| `python -m pytest -q` | ✅ | `11 passed` |
| chart determinism | ✅ | identical input/output verified |
| simulation determinism | ✅ | same seed -> same event sequence |
| monthly event cap | ✅ | max 3 accepted events per timestep |
| API smoke | ✅ | compile/create/get/events endpoints covered |

## 현재 주의 사항

- SQLite schema는 dev persistence 목적이라 PostgreSQL production schema의 축약 버전이다.
- Skyfield ephemeris(`de421.bsp`)는 첫 실행 시 로컬 cache를 만든다.
- `timezonefinder`는 현재 환경 호환성을 위해 `6.2.0`으로 고정했다.
- KASI regression은 로컬 fixture 기반이며 런타임 외부 API 호출은 없다.

## 다음 작업 후보

1. PostgreSQL persistence adapter 추가
2. weekly zoom endpoint와 timeline 분기 추가
3. branch simulation과 lineage 저장 추가
4. websocket progress envelope를 `asyncapi.yaml`과 정렬
