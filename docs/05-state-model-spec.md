# 05. State Model Spec

## Goal

State Model은 차트와 현재 사용자 목표를 읽고, 인생 자원과 압력 상태를 수치화한다.

## State Axes

### Primary Domains

| Field | Meaning | Range |
| --- | --- | --- |
| `career` | 직업 안정성, 성장성, 사회적 위치 | 0..100 |
| `relationship` | 연애, 결혼, 대인관계 안정성 | 0..100 |
| `wealth` | 수입, 지출 안정성, 자원 확보력 | 0..100 |
| `health` | 체력, 회복력, 붕괴 위험 반대값 | 0..100 |

### Secondary Modifiers

| Field | Meaning | Range |
| --- | --- | --- |
| `stress` | 전반 압박과 소진도 | 0..100 |
| `momentum` | 최근 추진력과 상승 흐름 | 0..100 |
| `support` | 외부 도움과 완충 자원 | 0..100 |
| `risk_exposure` | 변동성과 손실 노출도 | 0..100 |

## Initialization Rules

- primary domains start at `50`
- `stress` starts at `35`
- `momentum` starts at `50`
- `support` starts at `50`
- `risk_exposure` starts at `40`

These defaults are then adjusted by `FeatureVector` and user goal/constraints.

## Mapping Rules

### Feature-driven adjustments

- strong officer/authority signals raise `career`, may also raise `stress`
- strong wealth signals raise `wealth`, may raise `risk_exposure`
- strong resource/support signals raise `health` and `support`
- strong output/expression signals raise `career` and `momentum`
- strong peer/competition signals raise `relationship`, may lower `wealth`
- strong imbalance lowers `health` and raises `stress`

### Goal-driven adjustments

- `goal.category=career` raises `career` sensitivity multiplier
- `goal.category=relationship` raises `relationship` sensitivity multiplier
- `goal.category=wealth` raises `wealth` sensitivity multiplier
- `goal.category=health` raises `health` sensitivity multiplier

### Constraint-driven adjustments

- `must_avoid=debt` increases wealth-loss penalty
- `must_avoid=conflict` increases relationship-conflict penalty
- current job instability raises base `risk_exposure`

## Transition Rules

- state is updated only through timeline factors and accepted event impacts
- clamped range for every state is `0..100`
- any `health < 20` adds persistent stress penalty in following timesteps
- any `support > 80` reduces stress spikes by 20 percent
- any `risk_exposure > 75` amplifies negative wealth and relationship events by 15 percent

## Example

```json
{
  "life_state": {
    "career": 58,
    "relationship": 46,
    "wealth": 54,
    "health": 49,
    "stress": 41,
    "momentum": 55,
    "support": 52,
    "risk_exposure": 47
  }
}
```
