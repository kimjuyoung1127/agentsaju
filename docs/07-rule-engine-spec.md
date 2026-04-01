# 07. Rule Engine Spec

## Goal

Rule Engine은 `FeatureVector + TimelineFactor + LifeState`를 읽고 사건 후보를 생성한다.

## Event Taxonomy

### Career

- `CAREER_MOVE`
- `CAREER_STALL`
- `AUTHORITY_PRESSURE`
- `SKILL_GAIN`

### Relationship

- `RELATIONSHIP_BOND`
- `RELATIONSHIP_CONFLICT`
- `RECONCILIATION_WINDOW`
- `SOCIAL_FATIGUE`

### Wealth

- `WEALTH_GAIN`
- `WEALTH_LEAK`
- `INVESTMENT_VOLATILITY`
- `ASSET_LOCK`

### Health

- `HEALTH_RECOVERY`
- `HEALTH_ALERT`
- `BURNOUT_RISK`
- `ENERGY_DROP`

## Scoring Inputs

- `ten_gods`
- `element_balance`
- `relations_matrix`
- useful/unfavorable signals
- current `LifeState`
- current `TimelineFactor`

## Scoring Outputs

Each event candidate must produce:

- `impact_vector`
- `confidence`
- `importance`
- `tradeoff`
- `evidence_refs`

## Importance Formula

Use the following normalized formula:

```text
importance =
  35 * normalized_abs_impact +
  25 * domain_relevance +
  20 * timeline_pressure +
  20 * novelty
```

Rounded and clamped to `0..100`.

## Confidence Formula

Use the following normalized formula:

```text
confidence =
  0.5 * rule_strength +
  0.3 * signal_alignment +
  0.2 * state_consistency
```

Rounded to two decimals and clamped to `0.0..1.0`.

## Evidence References

### Source Type Taxonomy

Evidence는 3개 대분류(category)와 세부 source_type으로 구분한다.

| Category | source_type | 설명 | 예시 |
| --- | --- | --- | --- |
| `rule_ref` | `rule`, `timeline`, `feature`, `state` | 형식화된 룰 엔진 규칙 및 계산 결과 | `rule:R-035`, `feature:element_clash` |
| `kb_ref` | `classic`, `modern`, `academic` | 고전/현대 문헌, 학술 자료, RAG 검색 결과 | `classic:적천수-용신편`, `modern:KR-실전사주-ch7` |
| `case_ref` | `backtest`, `pattern`, `archetype` | 유사 사례, 백테스트 패턴, 원형 사례 | `backtest:C-1203`, `pattern:career_move_after_clash` |

### Record Structure

An `evidence_ref` record must contain:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `ref_id` | string | Yes | unique within run |
| `category` | `rule_ref \| kb_ref \| case_ref` | Yes | evidence 대분류 |
| `source_type` | string | Yes | category 내 세부 유형 |
| `source_key` | string | Yes | 구체적 출처 식별자 |
| `summary` | string | Yes | 1~2문장 요약 |
| `confidence_weight` | float | No | 0.0~1.0, 해당 근거의 신뢰도 가중치 |

### Minimum Evidence Requirements

Every accepted event must include:

- **최소 1개 `rule_ref`** — 룰 엔진 계산 근거 필수
- **최소 1개 non-rule source** — `kb_ref` 또는 `case_ref` 중 하나 이상
- `kb_ref`와 `case_ref`가 모두 있으면 evidence density 보너스 적용

### Mixing Rule

동일 이벤트의 evidence_refs 내에서 category가 섞이지 않도록 그룹핑한다. Judge는 category별로 근거를 분리 평가한다.

## Tradeoff Contract

`tradeoff` includes:

- `immediate_gain`
- `immediate_cost`
- `downstream_risk`
- `recommended_posture`

## Rule Boundaries

- Rule Engine does not write narrative text.
- Rule Engine does not rank worldlines across runs.
- Rule Engine never consults LLM.
