# 13. Implementation Roadmap

## Goal

문서 잠금 이후 구현 순서를 고정한다.

## Build Order

### Phase 1: Deterministic Core

1. Chart Engine
2. Feature extraction
3. State Model
4. Policy snapshot and validation metadata

### Phase 2: Simulation Core

1. Timeline factor generation
2. Rule Engine
3. Baseline simulation
4. Branch simulation
5. Event log persistence

### Phase 3: Explanation Core

1. Evidence layer (3종 분류: rule_ref / kb_ref / case_ref)
2. Knowledge Retrieval (RAG) — Gemini Embedding 2 기반 문헌/사례 검색
3. Debate orchestration (adaptive scaling: simple/moderate/complex tier)
4. Judge ranking
5. Narrative generation

### Phase 4: Service Layer

1. API endpoints
2. Async jobs
3. Storage integration
4. Report retrieval

### Phase 5: Advanced Agent (Future)

1. 계층형 팀 구조 (도메인별 팀 + Leader/Worker 분화)
2. 학파별 프로파일 다중 실행 및 consensus/divergence 비교
3. Knowledge Base 확장 (고전 원전, 사례 DB 대규모 인덱싱)

## Review Gates (Updated)

- Gate 1: chart engine matches golden fixtures
- Gate 2: simulation replay is deterministic
- Gate 2.5: school_profile 변경 시 FeatureVector 차이 검증
- Gate 3: debate messages are evidence-grounded (3종 category 포함)
- Gate 3.5: RAG 검색 결과가 evidence_refs에 정확히 연결됨
- Gate 4: narrative output passes grounding checks
- Gate 5: 팀 구조 도입 시 플랫 구조 대비 품질 향상 검증

## Out of Scope for First Implementation Pass

- payment provider integration
- end-user web UI
- mobile app packaging
- real-time websocket dashboard
- B2B analytics
