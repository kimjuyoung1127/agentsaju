# 09. Narrative Layer Spec

## Goal

Narrative Layer는 grounded facts만 읽어 사람이 이해하기 쉬운 설명과 행동 스크립트를 생성한다.

## Allowed Inputs

- `ChartCore` summary fields
- `FeatureVector` summary fields
- ranked `BranchOutcome`
- accepted `EventCandidate`
- `evidence_refs`
- user goal and constraints

## Forbidden Inputs

- raw hidden prompt instructions from other subsystems
- ad-hoc user memory not present in persisted inputs
- inferred future facts not present in events or outcomes

## Forbidden Outputs

- new event types
- altered scores
- altered probabilities
- uncited medical, legal, or investment certainty claims

## Output Types

### Free Summary

- 1 to 3 short paragraphs
- highlight top branch and top risk period
- cite at least 2 evidence refs

### Paid Detail

- branch-by-branch explanation
- domain-specific reasoning
- cause and tradeoff summary
- cite all major evidence groups

### Action Scripts

- max 3 scripts per section
- each script must map to one scenario and one posture
- tone guidance is allowed, new facts are not

## Grounding Rules

- every paragraph must trace to at least one event or evidence group
- if evidence is insufficient, the system must emit “insufficient evidence” phrasing
- narrative ranking must follow judge ranking, not override it

## Validation

Before release, each narrative section is checked for:

- unsupported named facts
- unsupported dates
- unsupported certainty language
- missing evidence references
