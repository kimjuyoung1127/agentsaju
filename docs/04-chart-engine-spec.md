# 04. Chart Engine Spec

## Goal

Chart Engine은 사용자가 입력한 출생 정보를 결정론적 차트와 파생 피처 계산의 기준값으로 변환한다.

## Inputs

- `BirthInput`
- optional validation metadata for KASI regression

## Locked Policy Defaults

| Policy | Default | Rule |
| --- | --- | --- |
| `timezone` | `Asia/Seoul` | omitted input uses this default |
| `calendar` | `solar` | omitted input is rejected at API level; UI default is solar |
| `apply_local_mean_time` | `false` | when `true`, longitude is mandatory |
| `early_zi_time` | `false` | 23:00~00:59 is not rolled to next day by default |
| `location` | optional | required only for solar-time correction |
| `leap_month` | `false` | only used for lunar input |

## Output Contract

Chart Engine returns:

1. `ChartCore`
2. `FeatureVector`
3. `validation_meta`

`validation_meta` contains:

- `engine_version`
- `policy_snapshot`
- `normalized_birth_datetime`
- `kasi_comparison_status`

## Validation Strategy

### KASI usage

- KASI is the regression oracle for year/month/day ganji and leap-month verification.
- KASI comparison is recorded, not exposed as public business logic.
- Missing KASI access or mismatched edge case is a validation status, not a silent fallback.

### Golden Set

The golden set must include:

- leap month start/end boundaries
- solar term boundary timestamps
- early-zi boundary timestamps
- local mean time day rollover cases

The golden set is stored as test fixtures, not hardcoded in engine logic.

## Engine Decisions

- Chart calculation is deterministic and pure with respect to input + policy snapshot.
- Chart Engine must not inspect goal, constraints, or simulation seed.
- If required input for selected policy is missing, the engine returns a validation error.

## Failure Modes

| Case | Response |
| --- | --- |
| invalid datetime | 422 |
| lunar input without month/day | 422 |
| `apply_local_mean_time=true` without longitude | 422 |
| unsupported timezone string | 422 |
| KASI mismatch during regression test | test failure, not runtime fallback |

## Example Validation Payload

```json
{
  "validation_meta": {
    "engine_version": "chart-v1",
    "policy_snapshot": {
      "timezone_default": "Asia/Seoul",
      "apply_local_mean_time": false,
      "early_zi_time": false
    },
    "normalized_birth_datetime": "1990-10-10T14:30:00+09:00",
    "kasi_comparison_status": "matched"
  }
}
```
