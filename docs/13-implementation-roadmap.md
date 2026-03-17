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

1. Evidence layer
2. Debate orchestration
3. Judge ranking
4. Narrative generation

### Phase 4: Service Layer

1. API endpoints
2. Async jobs
3. Storage integration
4. Report retrieval

## Review Gates

- Gate 1: chart engine matches golden fixtures
- Gate 2: simulation replay is deterministic
- Gate 3: debate messages are evidence-grounded
- Gate 4: narrative output passes grounding checks

## Out of Scope for First Implementation Pass

- payment provider integration
- end-user web UI
- mobile app packaging
- real-time websocket dashboard
- B2B analytics
