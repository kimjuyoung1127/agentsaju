# 12. Test Plan

## Goal

문서 기반 구현이 시작되기 전에 테스트 기준을 잠근다.

## Chart Engine Tests

- same input + same policy => same chart
- leap month edge cases
- solar term boundary cases
- early-zi boundary cases
- local mean time rollover cases
- KASI regression fixture comparison

## State Model Tests

- default initialization values
- feature-driven state adjustments
- goal-driven sensitivity adjustments
- clamping behavior
- stress/support/risk exposure interaction behavior

## Rule Engine Tests

- event taxonomy validity
- every accepted event has `evidence_refs`
- importance and confidence stay within range
- same inputs produce same scored events

## Simulation Tests

- same run inputs + same seed => same event sequence
- monthly baseline produces 12 timesteps
- weekly expansion only affects target month
- branch runs keep correct `parent_run_id`

## Agent Layer Tests

- every oracle claim includes `evidence_refs`
- unsupported claim is rejected
- judge ranking remains stable for identical inputs
- duplicate branch claims merge correctly

## Narrative Layer Tests

- no unsupported facts added
- no unsupported certainty claims
- every paragraph maps to evidence
- report order follows judge ranking

## API Tests

- chart compile success and failure cases
- simulation create success and validation failures
- branch creation lineage checks
- debate execution success case
- report fetch free vs paid shape

## Acceptance Criteria

문서 인수 기준은 다음과 같다.

1. 구현자가 추가 의사결정을 하지 않아도 된다.
2. 테스트 작성자가 외부 설명 없이 fixture와 expected shape를 정의할 수 있다.
3. LLM grounding 규칙을 자동화 테스트로 옮길 수 있다.
