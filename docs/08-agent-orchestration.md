# 08. Agent Orchestration

## Goal

Agent layer는 시뮬레이터가 만든 branch outcomes를 읽고, grounded debate를 통해 상위 세계선을 정렬한다.

## Agent Roles

| Role | Primary Responsibility |
| --- | --- |
| `DestinyAnalyst` | 원국, 대운, 세운, 월운의 총괄 해석 |
| `CareerOracle` | career and wealth upside/downside 중심 반박 |
| `RelationshipOracle` | 관계성과 갈등/회복 가능성 중심 반박 |
| `HealthOracle` | health and stress collapse 경고 |
| `RiskOracle` | 손실, 실패, 과대해석 위험 점검 |
| `FreeWillOracle` | 현재 습관, 선택 성향, 제약조건 반영 |
| `JudgeAgent` | 주장 병합, 충돌 해소, 상위 세계선 정렬 |

## Debate Input

Each debate receives:

- baseline outcome
- selected branch outcomes
- top events per outcome
- evidence refs for each event
- user goal and constraints

## Debate Rules

- each oracle must cite `evidence_refs`
- any unsupported claim is discarded
- oracles may disagree on interpretation, not on facts
- judge merges duplicate claims by evidence identity

## Debate Output

Judge returns:

- ranked top 3 to 7 worldlines
- one-line reason for each worldline
- major risk and opportunity tags
- discarded worldlines list with discard reason

## Ranking Criteria

Judge ranks by:

1. goal alignment
2. cumulative domain balance
3. downside containment
4. confidence consistency
5. evidence density

## Constraints

- maximum 7 grounded oracle roles in core
- no free-form multi-agent chat room
- no oracle can modify event scores or raw state

## Message Shape

```json
{
  "agent_role": "RiskOracle",
  "claim": "This branch contains a concentrated wealth-loss risk in Q3.",
  "evidence_refs": ["ev-rule-12", "ev-state-03"],
  "objections": ["CareerOracle:branch-b"],
  "confidence": 0.76
}
```
