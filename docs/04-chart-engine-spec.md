# 04. Chart Engine Spec

## Goal

Chart Engine은 사용자가 입력한 출생 정보를 결정론적 차트와 파생 피처 계산의 기준값으로 변환한다.

## Inputs

- `BirthInput`
- optional validation metadata for KASI regression

## School Profile

사주 해석은 학파별로 기준이 다르다. 엔진은 `school_profile`을 통해 해석 체계를 명시적으로 선택한다.

### Profile Definitions

| Profile | 설명 | 주요 차이 |
| --- | --- | --- |
| `orthodox` | 고전 원전 중심 (적천수, 자평진전) | 용신 판단 보수적, 신살 최소 반영 |
| `modern_korean` | 한국 실전 명리학 | 용신 실용적 판단, 신살 선택적 반영, 격국 유연 해석 |
| `conservative` | 격국용신 엄격 적용 | 격국 우선, 조후 보조, 신살 미반영 |
| `practical` | 통변 중심 실용파 | 상담 경험 기반, 격국보다 오행 흐름과 십신 역학 중시 |

### Default

- 기본값: `modern_korean`
- 사용자가 profile을 선택하지 않으면 기본값 적용

### Engine Behavior

- 각 profile은 고유한 룰셋 가중치를 가진다
- `policy_snapshot`에 `school_profile`이 기록된다
- 동일 차트라도 profile이 다르면 `FeatureVector`의 `useful_signals`, `unfavorable_signals`가 달라질 수 있다

### Output Separation

시뮬레이션 결과에서 학파 차이가 발생할 경우:

- **공통 합의 부분**: 모든 profile에서 일치하는 해석 → `consensus` 태그
- **학파 차이 부분**: profile별로 갈리는 해석 → `divergence` 태그 + profile별 근거 명시

이를 통해 엔진이 독단적으로 보이는 것을 방지한다.

## Locked Policy Defaults

| Policy | Default | Rule |
| --- | --- | --- |
| `school_profile` | `modern_korean` | 해석 체계 선택 |
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
