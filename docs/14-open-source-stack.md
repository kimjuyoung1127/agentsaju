# 14. 오픈소스 스택 가이드

Last updated: `2026-03-17`

이 프로젝트는 공개 오픈소스만으로도 핵심 뼈대를 세울 수 있다.
아래는 카테고리별 후보와 우선순위, 그리고 최종 추천 조합이다.

---

## 1. 사주 / 만세력 / Bazi 계산 엔진

| 프로젝트 | 언어 | 핵심 특징 | 우선순위 |
| --- | --- | --- | --- |
| **yhj1024/manseryeok** | TypeScript | 한국 만세력, 양력/음력, 절기 월주, 60갑자, 분 단위 시주 | 1순위 |
| **alvamind/bazi-calculator-by-alvamind** | Node/TS | 현대적 Bazi 계산/분석, 타입 안정성 | 2순위 |
| **tommitoan/bazica** | Go | 고성능 BaZi 계산, 마이크로서비스화에 적합 | 3순위 (고성능 필요 시) |
| **cantian-ai/bazi-mcp** | - | MCP 서버, "AI 해석보다 정확한 계산" 포지션 | 참고 |
| **yize/solarlunar** | JS | 태양력/음력 변환, 천간지지, 24절기 | 보조 라이브러리 |
| **livedcode/ChineseCalendarLib** | .NET | 음양력 변환, 간지, 절기, BaZi | 참고 |

### 설계 원칙

- 만세력/캘린더 계산 → 오픈소스 활용
- 해석 규칙과 상태 모델 → **자체 소유** (핵심 차별화)

---

## 2. 멀티에이전트 오케스트레이션

| 프로젝트 | 언어 | 핵심 특징 | 우선순위 |
| --- | --- | --- | --- |
| **langchain-ai/langgraph** | Python/JS | 상태 기반 에이전트, 분기/재시도/장기 실행 | 1순위 |
| **crewAIInc/crewAI** | Python | 역할 기반 멀티에이전트 협업 | 2순위 |
| **microsoft/autogen** | Python | 멀티에이전트 협업, 참고 기준점 | 참고 |

### 이 프로젝트에 맞는 이유

자유 대화형 에이전트보다 **구조화된 단계형 판단**이 중요하기 때문에
LangGraph의 상태 머신 방식이 가장 적합하다.
JS 버전(langgraphjs)도 있어 Next.js 스택과 호환된다.

---

## 3. 에이전트 사회 / 시뮬레이션 / 군집 행동

| 프로젝트 | 언어 | 핵심 특징 | 우선순위 |
| --- | --- | --- | --- |
| **projectmesa/mesa** | Python | 에이전트 기반 모델링 대표, 복잡계/다중 에이전트 | 1순위 |
| **tsinghua-fib-lab/AgentSociety** | Python | 대규모 사회 시뮬레이션, MiroFish 감성 | 2순위 |
| **AffordableGenerativeAgents** | Python | 저비용 generative agents | 참고 |
| **qiliuchn/gatsim** | Python | 다중 에이전트 시뮬레이션 설계 참고 | 참고 |
| **LLM-Agent-Based-Modeling-and-Simulation** | - | 서베이형 저장소 | 조사용 |

### 적용 방향

"1000명 토론"보다 **"다수 하위 에이전트가 세계를 형성하고 대표 주장으로 압축"**하는 구조.
실제 구현은 Mesa나 AgentSociety를 참고한다.

---

## 4. 토론 / 군집 / 네트워크 시각화

| 프로젝트 | 핵심 특징 | 우선순위 |
| --- | --- | --- |
| **vasturiano/react-force-graph** | React 2D/3D/VR force graph, 군집/대표 노드 시각화 | 1순위 |
| **vasturiano/3d-force-graph** | 3D force graph 렌더러 | 기반 렌더러 |
| **vasturiano/d3-force-3d** | 3D 물리 엔진 | 기반 물리 |
| **vasturiano/three-forcegraph** | Three.js force graph | 기반 |
| **r3f-forcegraph** | React Three Fiber 결합 | 대안 |
| **jacomyal/sigma.js** | WebGL 대규모 그래프, 수천 노드급 | 2순위 |
| **cytoscape/cytoscape.js** | 그래프 이론 + 시각화, 논증 관계 | 3순위 |
| **vis-network** | 동적 네트워크, 클러스터링 | 대안 |

### 이 프로젝트에 맞는 이유

"점들의 군집, 대표자 노드, 위에서 아래로 내려다보는 토론 시각화"와
react-force-graph가 가장 잘 맞는다.

---

## 5. 입자 / 군집 / boids / 움직임 연출

| 프로젝트 | 핵심 특징 | 우선순위 |
| --- | --- | --- |
| **Mugen87/yuka** | JS 게임 AI, steering behaviors, navigation, perception | 1순위 |
| **markuslerner/Particular** | GPU 가속, flocking/swarm/seek/arrive | 2순위 |
| **sampstrong/r3f-particle-system** | R3F FBO 시뮬레이션 | R3F 노선 |
| **tim-soft/react-particles-webgl** | WebGL 파티클 | 대안 |
| **mmdalipour/particle-morph** | morph 효과 | 대안 |
| **r3f-flow-field-particles** | flow-field 입자 연출 | 대안 |
| **three.quarks** | Three.js 고성능 VFX | 대안 |

### 추천 조합

react-force-graph + Yuka 또는 Particular =
"점 군집이 생기고 토론하는 듯한 화면"을 만들기 좋다.

---

## 6. 벡터DB / RAG / 근거 검색

| 프로젝트 | 유형 | 핵심 특징 | 우선순위 |
| --- | --- | --- | --- |
| **qdrant/qdrant** | 벡터DB | 고성능, payload filtering, 규칙/사례 필터링 | 1순위 |
| **weaviate/weaviate** | 벡터DB | cloud-native, 벡터+키워드+RAG+reranking | 2순위 |
| **chroma-core/chroma** | 벡터DB | 프로토타입 속도, memory/RAG 빠른 연결 | 프로토타입용 |
| **neo4j/neo4j** | 그래프DB | rule_ref/kb_ref/case_ref evidence graph | 1순위 (그래프) |
| **memgraph/memgraph** | 그래프DB | 경량 그래프DB | 대안 |

### 추천 조합

**Qdrant + Neo4j**
벡터 검색 + evidence graph 연결이 이 프로젝트의 근거 체계와 잘 맞는다.

---

## 7. 룰 엔진 / 결정론적 판정

| 프로젝트 | 언어 | 핵심 특징 | 우선순위 |
| --- | --- | --- | --- |
| **jruizgit/rules** (durable_rules) | Python/Node/Ruby | 이벤트/상태 기반 규칙 평가 | 참고 |
| **ali-master/rule-engine** | TypeScript | JSON 기반 선언형 규칙 | 참고 |

### 설계 원칙

- 핵심 계산 → 자체 코드
- 상위 해석 규칙만 → 룰 엔진 (선택적)

---

## 8. 비동기 실행 / 워크플로우

| 프로젝트 | 언어 | 핵심 특징 | 우선순위 |
| --- | --- | --- | --- |
| **temporalio/temporal** | 다중 | durable execution, 장시간 워크플로우, 재시도/복구 | 1순위 |
| **celery/celery** | Python | 분산 태스크 큐 + flower 모니터링 | 2순위 (Python) |
| **taskiq-python/taskiq** | Python | async FastAPI 친화, 가볍고 타입 힌트 지원 | 대안 (Python) |
| **taskforcesh/bullmq** | Node | Redis 기반 큐/배치 처리 | 1순위 (Node) |

---

## 9. LLM 게이트웨이 / 라우팅 / 비용 제어

| 프로젝트 | 핵심 특징 | 우선순위 |
| --- | --- | --- |
| **BerriAI/litellm** | 100+ LLM API 통합, 비용 추적, 로드밸런싱 | 1순위 |
| **Portkey-AI/gateway** | AI 게이트웨이 | 대안 |
| **theopenco/llmgateway** | LLM 게이트웨이 | 대안 |

### 이 프로젝트에 맞는 이유

Worker는 저가 모델, Judge는 고가 모델을 쓰는 구조에서
게이트웨이는 거의 필수다.

---

## 10. 관측 / 평가 / 디버깅

| 프로젝트 | 핵심 특징 | 우선순위 |
| --- | --- | --- |
| **langfuse/langfuse** | self-host 가능, 모니터링/평가/프롬프트 관리 | 1순위 |
| **Arize-ai/phoenix** | AI observability, LangGraph tracing 지원 | 2순위 |
| **promptfoo/promptfoo** | 프롬프트/모델 비교, 자동 평가 | 3순위 (백테스트용) |
| **Helicone/helicone** | gateway + observability | 대안 |
| **TensorZero/tensorzero** | gateway/observability/evaluation 통합 | 대안 |

### 추천 조합

**Langfuse + Phoenix + Promptfoo**
멀티에이전트 trace + 실험 평가 + 프롬프트 비교를 모두 커버한다.

---

## 11. UI / 생성형 인터페이스

| 프로젝트 | 핵심 특징 | 비고 |
| --- | --- | --- |
| **CopilotKit/OpenGenerativeUI** | AI가 동적으로 만드는 rich interactive UI | 참고 |

---

## 12. 조사용 / 큐레이션 저장소

| 저장소 | 용도 |
| --- | --- |
| awesome-ai-agents-2026 | 에이전트 프레임워크 큐레이션 |
| awesome-temporal | Temporal 생태계 |
| awesome-weaviate | Weaviate 생태계 |
| awesome-mcp-servers | MCP 서버 (bazi-mcp 포함) |

---

## 최종 추천 조합

### A. TS/Next.js 중심 스택 (프로덕션 우선)

| 레이어 | 선택 |
| --- | --- |
| 사주 계산 | manseryeok + bazi-calculator-by-alvamind |
| 오케스트레이션 | LangGraphJS |
| 시각화 | react-force-graph + Yuka |
| 벡터DB | Qdrant |
| 그래프DB | Neo4j |
| 큐 | BullMQ |
| 관측 | Langfuse |
| 라우팅 | LiteLLM |

### B. Python/연구형 스택 (실험/백테스트 우선)

| 레이어 | 선택 |
| --- | --- |
| 사주 계산 | bazica 또는 Python 포팅 |
| 오케스트레이션 | LangGraph 또는 CrewAI |
| 시뮬레이션 | Mesa |
| 벡터DB | Qdrant |
| 큐 | Temporal 또는 Celery |
| 평가 | Phoenix + Promptfoo |
| 관측 | Langfuse |

---

## 우선 검토 리스트 (Top 12)

가장 먼저 실제로 설치/검증할 것:

1. **manseryeok** — 사주 계산
2. **bazi-calculator-by-alvamind** — Bazi 계산
3. **LangGraph** — 멀티에이전트 오케스트레이션
4. **CrewAI** — 역할 기반 에이전트
5. **Mesa** — 에이전트 시뮬레이션
6. **react-force-graph** — 군집/네트워크 시각화
7. **Yuka** — 입자/군집 움직임 연출
8. **Qdrant** — 벡터DB
9. **Neo4j** — 그래프DB (evidence graph)
10. **Temporal** — 워크플로우 실행
11. **LiteLLM** — LLM 게이트웨이
12. **Langfuse** — 관측/평가

이 12개로 결정론적 사주 엔진 + 멀티에이전트 해석 + 군집 시각화 + 근거 검색 + 평가 체계의 뼈대를 만들 수 있다.

---

## 선택 기준 4가지

1. 최근까지 유지보수되는가
2. 라이선스가 서비스에 맞는가
3. 현재 스택과 호환되는가
4. 핵심 차별화를 **대체**하는가, **보조**하는가

> 사주 규칙의 핵심 판정 로직은 외부 라이브러리에 전부 맡기지 않는다.
> 만세력/캘린더 계산은 오픈소스 활용, 해석 규칙과 상태 모델은 자체 소유.
