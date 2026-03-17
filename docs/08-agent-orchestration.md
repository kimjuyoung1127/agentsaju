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

## Adaptive Scaling

에이전트 수는 케이스 난이도에 따라 동적으로 조절한다. 항상 7명 전원이 참여하는 것이 아니라, 복잡도에 비례하여 확장한다.

### Complexity Tiers

| Tier | 조건 | 활성 에이전트 | 예상 토큰 비용 |
| --- | --- | --- | --- |
| `simple` | 충돌 0~1건, 학파 합의, 단일 도메인 우세 | 3명 (DestinyAnalyst + 도메인 1명 + Judge) | 낮음 |
| `moderate` | 충돌 2~3건, 도메인 간 트레이드오프 존재 | 5명 (DestinyAnalyst + 도메인 2명 + RiskOracle + Judge) | 중간 |
| `complex` | 충돌 4건+, 학파 divergence, 용신 판정 충돌, 근거 부족 | 7명 전원 | 높음 |

### Complexity Score 산정

```text
complexity_score =
  2 * relation_clash_count +
  3 * school_divergence_count +
  1 * multi_domain_tradeoff_count +
  2 * insufficient_evidence_count
```

| Score Range | Tier |
| --- | --- |
| 0~3 | `simple` |
| 4~8 | `moderate` |
| 9+ | `complex` |

### Scaling Rules

- Tier 결정은 시뮬레이션 완료 후, 토론 시작 전에 수행
- DestinyAnalyst와 JudgeAgent는 모든 Tier에서 필수 참여
- 비활성 에이전트의 역할은 Judge가 흡수 (해당 관점 요약만 추가)
- Tier는 `debate_record`에 `complexity_tier`로 기록

### Future Extension

- 특정 도메인의 worker를 팀 내 2~3명으로 확장하는 것은 Phase 2+ 이후 검토
- 초기 구현은 위 3-tier 고정 스케일링으로 시작

## Constraints

- maximum 7 grounded oracle roles in core
- no free-form multi-agent chat room
- no oracle can modify event scores or raw state

## Team Structure

### Phase 1: Flat Structure (초기 구현)

초기에는 7명 플랫 구조를 유지한다. 모든 Oracle이 동일 레벨에서 Judge에게 직접 보고한다.

```
DestinyAnalyst ─┐
CareerOracle   ─┤
RelationOracle ─┤
HealthOracle   ─┼──→ JudgeAgent ──→ Final Ranking
RiskOracle     ─┤
FreeWillOracle ─┘
```

### Phase 2+: Hierarchical Team Structure (확장)

케이스 복잡도가 높아지면 도메인별 팀으로 분화한다. 각 팀은 Leader가 요약하여 Judge에게 보고한다.

```
┌─ Career Team ──────────────────┐
│  CareerOracle (Leader)         │
│  + Explorer (탐색자)            │──→ Team Summary
│  + Critic (반론자)              │
│  + EvidenceCollector (증거수집) │
└────────────────────────────────┘
                                    ┐
┌─ Relationship Team ────────────┐  │
│  RelationshipOracle (Leader)   │  │
│  + Explorer                    │──┼──→ JudgeAgent ──→ Final Ranking
│  + Critic                      │  │
└────────────────────────────────┘  │
                                    │
┌─ Health/Risk Team ─────────────┐  │
│  HealthOracle (Leader)         │  │
│  + RiskOracle (Co-Leader)      │──┤
│  + Calibrator (과장제거)        │  │
└────────────────────────────────┘  │
                                    │
  DestinyAnalyst ───────────────────┤
  FreeWillOracle ───────────────────┘
```

### Team Communication Rules

- **팀 내부**: 자유 통신 (단, 최대 2라운드)
- **팀 간**: Leader → Judge 경로만 허용. 팀 간 직접 통신 금지
- **Judge**: 팀 요약만 수신. 개별 worker 메시지는 Leader가 필터링

### Worker Roles (팀 내부)

| Role | 역할 |
| --- | --- |
| Explorer | 해석 후보 탐색, 가능성 열거 |
| Critic | 반론/예외 제기, 과대해석 견제 |
| EvidenceCollector | kb_ref/case_ref 근거 회수 및 정리 |
| Calibrator | confidence 과장 제거, 중립적 재평가 |

### Scaling by Tier

| Tier | 팀 구성 |
| --- | --- |
| `simple` | 팀 없음, 플랫 3명 |
| `moderate` | 팀 없음, 플랫 5명 |
| `complex` | 도메인별 팀 구성, 각 팀 3~4명, 총 15~20명 |

### Implementation Note

- Phase 1 구현은 플랫 구조로 시작
- 팀 구조는 프로토콜 검증 후 Phase 2+ 에서 도입
- 팀 구조 도입 시에도 총 에이전트 수는 20명 이하로 제한

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
