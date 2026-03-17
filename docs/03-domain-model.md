# 03. Domain Model

## Core Types

### BirthInput

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `calendar` | `solar \| lunar` | Yes | default consumer input is `solar` |
| `birth_datetime` | ISO datetime string | Yes | user-declared local time |
| `timezone` | IANA timezone | No | default `Asia/Seoul` |
| `location` | object | No | required only when `apply_local_mean_time=true` |
| `leap_month` | boolean | No | only meaningful for `lunar` |
| `apply_local_mean_time` | boolean | No | default `false` |
| `early_zi_time` | boolean | No | default `false` |
| `gender` | string | No | optional explanatory feature |

### ChartCore

| Field | Type | Meaning |
| --- | --- | --- |
| `pillars` | object | year/month/day/hour stem-branch |
| `hidden_stems` | object | branch-to-hidden-stems mapping |
| `day_master` | string | day stem |
| `corrections` | object | timezone, solar-time, calendar normalization |
| `policy_snapshot` | object | rules used to compute current output |

### FeatureVector

| Field | Type | Meaning |
| --- | --- | --- |
| `element_balance` | object | wood/fire/earth/metal/water normalized weights |
| `yin_yang_balance` | number | -1.0 to 1.0 |
| `ten_gods` | object | ten-gods weights |
| `relations_matrix` | array | 합/충/형/파/해 records |
| `useful_signals` | array | useful elements/signals |
| `unfavorable_signals` | array | unfavorable elements/signals |

### LifeState

| Field | Type | Range | Notes |
| --- | --- | --- | --- |
| `career` | number | 0..100 | initial default 50 |
| `relationship` | number | 0..100 | initial default 50 |
| `wealth` | number | 0..100 | initial default 50 |
| `health` | number | 0..100 | initial default 50 |
| `stress` | number | 0..100 | initial default 35 |
| `momentum` | number | 0..100 | initial default 50 |
| `support` | number | 0..100 | initial default 50 |
| `risk_exposure` | number | 0..100 | initial default 40 |

### TimelineFactor

| Field | Type | Meaning |
| --- | --- | --- |
| `mode` | `monthly \| weekly` | timeline resolution |
| `timestep` | string | `2026-03` or `2026-W12` |
| `daewoon` | object | decade luck factor |
| `sewoon` | object | year luck factor |
| `period_factor` | object | month or week-specific factor |
| `relations` | array | relations between natal chart and active timeline |

### EventCandidate

| Field | Type | Meaning |
| --- | --- | --- |
| `event_id` | string | unique within run |
| `event_type` | string | taxonomy-defined event |
| `domain` | string | `career`, `relationship`, `wealth`, `health` |
| `timestep` | string | source timeline unit |
| `impact_vector` | object | state deltas |
| `confidence` | float | 0.0..1.0 |
| `importance` | int | 0..100 |
| `tradeoff` | object | gains and losses by choice |
| `evidence_refs` | array | mandatory evidence list |

### SimulationRun

| Field | Type | Meaning |
| --- | --- | --- |
| `run_id` | string | unique baseline or branch id |
| `parent_run_id` | string or null | baseline for branches |
| `seed` | integer | deterministic replay seed |
| `timeline_mode` | `monthly \| weekly` | active resolution |
| `scenario_config` | object | goal, constraints, choices |
| `policy_snapshot` | object | simulation-level policy |
| `status` | string | pending, running, completed, failed |

### BranchOutcome

| Field | Type | Meaning |
| --- | --- | --- |
| `run_id` | string | branch run id |
| `final_state` | `LifeState` | terminal state |
| `key_events` | array | ranked event list |
| `probability_weight` | float | relative ranking weight |
| `worldline_summary` | string | short deterministic summary |

### DebateMessage

| Field | Type | Meaning |
| --- | --- | --- |
| `agent_role` | string | oracle role |
| `claim` | string | grounded claim |
| `evidence_refs` | array | mandatory citation refs |
| `objections` | array | refs to challenged claims |
| `confidence` | float | 0.0..1.0 |

### NarrativeSection

| Field | Type | Meaning |
| --- | --- | --- |
| `section_key` | string | report section id |
| `free_summary` | string | teaser |
| `paid_detail` | string | detailed explanation |
| `action_scripts` | array | grounded scripts |
| `evidence_refs` | array | cited refs |

## Invariants

- `ChartCore.policy_snapshot` is immutable after chart compilation.
- Every `EventCandidate` must have at least one `evidence_ref`.
- `SimulationRun.seed` is required for all baseline and branch runs.
- `BranchOutcome.probability_weight` is comparative and not an absolute future probability.
- Narrative output cannot contain fields absent from event, state, or evidence sources.

## Example JSON

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
    "early_zi_time": false,
    "gender": "male"
  },
  "chart_core": {
    "pillars": {
      "year": {"stem": "Gyeong", "branch": "O"},
      "month": {"stem": "Byeong", "branch": "Sul"},
      "day": {"stem": "Gap", "branch": "Ja"},
      "hour": {"stem": "Jeong", "branch": "Mi"}
    },
    "day_master": "Gap",
    "corrections": {
      "calendar_normalized": "solar",
      "timezone_used": "Asia/Seoul",
      "local_mean_time_applied": false
    },
    "policy_snapshot": {
      "calendar_engine_version": "v1",
      "timezone_default": "Asia/Seoul",
      "early_zi_time": false
    }
  }
}
```
