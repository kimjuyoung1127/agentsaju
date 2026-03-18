# backend 개발 진행 상황

> 최종 업데이트: 2026-03-18

## 문서 구조

현재 `backend/docs/`는 아래 구조를 기준으로 운영합니다.

- `docs/ref/` : 장기 참조 문서, 아키텍처, 시작 가이드
- `docs/status/` : 현재 구현 상태와 검증 결과
- `docs/daily/` : 일별 작업 기록
- `docs/weekly/` : 주간 요약
- `docs/DEVELOPMENT.md` : 현재 코드베이스 기준 단일 개발 현황 요약

새 문서를 추가하거나 이동할 때는 루트가 아니라 위 분류에 맞춰 배치합니다.

---

## 프로젝트 개요

| 항목 | 값 |
|------|-----|
| 레포 위치 | `C:\Users\ezen601\Desktop\Jason\agentsaju\backend` |
| 런타임 | Python 3.12 |
| API 프레임워크 | FastAPI |
| 검증 | pytest |
| 저장 | SQLite dev DB |
| 천문 계산 | Skyfield |
| 음양력 변환 | korean-lunar-calendar |
| 좌표 기반 timezone | timezonefinder 6.2.0 |

주요 참조 문서:

- `docs/ref/getting-started.md`
- `docs/ref/architecture.md`
- `docs/status/PROJECT-STATUS.md`

---

## 아키텍처

```text
backend/
├── src/saju_core   chart, state, timeline, rules, simulator, storage
├── src/saju_api    FastAPI endpoints and error mapping
├── tests/          pytest + fixtures
└── docs/           ref/status/daily/weekly 구조
```

핵심 흐름:

```text
BirthInput
-> compile_chart()
-> build_initial_state()
-> build_monthly_timeline()
-> evaluate_month_rules()
-> run_baseline_simulation()
-> SQLite persistence + FastAPI responses
```

---

## 현재 상태

| 영역 | 상태 | 요약 |
|------|------|------|
| Chart Engine | ✅ | solar/lunar normalization, local mean time, early-zi, 4 pillars |
| Feature Extraction | ✅ | element balance, ten gods, relations matrix, signal buckets |
| State Model | ✅ | fixed defaults + weight table + constraints |
| Monthly Timeline | ✅ | 12-month timeline with solar-term windows and domain pressure |
| Rule Engine | ✅ | 16 events, scoring, evidence refs, top-3 monthly acceptance |
| Simulator | ✅ | baseline only, deterministic monthly run |
| API | ✅ | compile, create simulation, fetch run, fetch events |
| Persistence | ✅ | SQLite dev schema for chart/run/event storage |
| Tests | ✅ | 11 pytest cases passing |
| Weekly/Branch/Debate | ⛔ 제외 | 다음 phase 범위 |

---

## 검증 현황

기준: 2026-03-18 재실행

```bash
python -m pytest -q
```

- 결과: `11 passed`

포함된 검증:

- chart determinism
- lunar conversion regression fixture
- solar term ordering
- early-zi day pillar change
- local mean time rollover
- validation error handling
- simulation determinism
- monthly event contract
- FastAPI endpoint smoke coverage

---

## 기술 결정 로그

| 날짜 | 결정 | 이유 |
|------|------|------|
| 2026-03-18 | `backend/docs/`를 `unityctl` 스타일로 분리 운영 | 장기 참조와 현재 상태 문서를 분리해 drift를 줄이기 위해 |
| 2026-03-18 | Python 순정 코어 유지 | 차트/시뮬레이션 계산을 한 런타임에서 재현 가능하게 유지하기 위해 |
| 2026-03-18 | `timezonefinder==6.2.0` 고정 | 현재 Windows 환경에서 최신 버전 빌드 실패를 피하면서 기능 요구를 유지하기 위해 |
| 2026-03-18 | SQLite dev persistence 채택 | 문서 계약을 유지하면서 빠르게 로컬 검증하기 위해 |
