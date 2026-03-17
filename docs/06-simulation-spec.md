# 06. Simulation Spec

## Goal

Simulator는 월/주 timeline factor와 rule engine을 사용해 baseline worldline과 branch worldlines를 생성한다.

## Run Types

### Baseline Run

- a single deterministic run produced from chart + goal + constraints + seed
- default mode is `monthly`
- contains 12 timesteps for a yearly horizon

### Branch Run

- derived from a baseline run
- must include `parent_run_id`
- can override selected choices, risk posture, or weekly zoom target

## Timeline Rules

### Default

- yearly horizon = 12 monthly timesteps
- timestep ids use `YYYY-MM`

### Weekly Expansion

- only available for a selected month
- replaces one monthly bucket with 4 or 5 weekly buckets
- weekly bucket ids use `YYYY-WNN`

### No Daily Mode in Core

- daily mode is not part of core simulation spec
- if needed later, it is an orchestration extension, not a core requirement

## Seed and Replay

- every run requires a `seed`
- same chart, goal, constraints, policy snapshot, and seed must replay identically
- branch runs may use their own seed, but parent relationship must be recorded

## Timestep Processing

For each timestep:

1. load `TimelineFactor`
2. generate candidate events from rule engine
3. score and rank events
4. apply accepted event impacts to `LifeState`
5. persist `state_before`, `state_after`, `event_ids`, `evidence_refs`

## Accepted Event Policy

- max 3 key events per monthly timestep
- max 5 key events per weekly timestep
- lower-ranked events may remain in raw storage but are not promoted to key events

## Branch Configuration

`scenario_config` may contain:

- `goal_variant`
- `choice_label`
- `risk_tolerance`
- `relationship_posture`
- `weekly_zoom_target`

## Output

- `SimulationRun`
- ordered `EventCandidate` list
- final `LifeState`
- optional `BranchOutcome`

## Failure Modes

| Case | Result |
| --- | --- |
| missing parent for branch | 422 |
| weekly zoom requested for absent month | 422 |
| seed missing | 422 |
| unsupported timeline mode | 422 |
