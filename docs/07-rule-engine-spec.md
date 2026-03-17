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

An `evidence_ref` record must contain:

- `ref_id`
- `source_type` such as `rule`, `timeline`, `feature`, `state`
- `source_key`
- `summary`

Every accepted event must include at least one rule source and one non-rule source.

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
