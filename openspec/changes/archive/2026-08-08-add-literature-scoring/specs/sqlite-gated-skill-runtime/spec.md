## ADDED Requirements

### Requirement: Runtime SHALL Persist Scoring As DB-Backed State

The runtime SHALL persist one normalized computed literature score in SQLite and SHALL use that row as the only semantic source for score rendering.

#### Scenario: Valid scoring payload is persisted
- **WHEN** literature scoring validation and calculation succeed
- **THEN** the normalized result is stored with its rubric identity
- **AND** `persist_literature_score` records a successful action receipt.

#### Scenario: Score artifact is re-rendered
- **WHEN** finalization reruns after valid score state exists
- **THEN** the artifact is rebuilt from SQLite rather than from an agent-authored public JSON file.

### Requirement: Runtime SHALL Persist A Per-Run Rubric Snapshot

Initialization SHALL copy the canonical scoring rubric and score template into the run's temporary runtime area and persist their paths with the other runtime inputs.

#### Scenario: Runtime initializes
- **WHEN** `init_runtime` persists built-in templates
- **THEN** it also persists an immutable scoring-rubric snapshot and score-template path for that run.

### Requirement: Gate SHALL Route Mode-Aware Scoring Actions

The workflow state and status payload SHALL route scoring after digest in normal mode and immediately after normalization in score-only mode.

#### Scenario: Normal mode reaches scoring
- **WHEN** digest persistence has a successful receipt and scoring does not
- **THEN** status returns the scoring action, instruction reference, payload shape, and field guidance.

#### Scenario: Score-only mode reaches scoring
- **WHEN** normalization succeeds with `score_only=true`
- **THEN** status routes directly to scoring without requiring outline, scopes, or digest rows.

### Requirement: Render Preconditions SHALL Depend On Run Mode

The runtime SHALL enforce separate full and score-only render prerequisites while keeping one stable stdout shape.

#### Scenario: Full render prerequisites
- **WHEN** a full run is finalized
- **THEN** score state and a scoring receipt are required in addition to the existing full-analysis prerequisites.

#### Scenario: Score-only render prerequisites
- **WHEN** a score-only run is finalized
- **THEN** normalized source, persisted runtime assets, score state, and scoring receipt are required
- **AND** digest, reference, citation, outline, and scope data are not required.

### Requirement: Scoring Recovery SHALL Preserve Independent Downstream Work

Receipt invalidation and repair SHALL follow actual data dependencies rather than treating scoring as a dependency of reference or citation semantics.

#### Scenario: Source normalization reruns
- **WHEN** normalized source is replaced
- **THEN** the scoring receipt and all downstream receipts are invalidated.

#### Scenario: Scoring reruns after downstream work
- **WHEN** scoring is persisted again without changing normalized source
- **THEN** final render is invalidated
- **AND** valid reference and citation receipts remain intact.

#### Scenario: Missing score is repaired in an otherwise advanced run
- **WHEN** downstream receipts exist but score state or its receipt is missing
- **THEN** repair routes to scoring first
- **AND** subsequently routes to the first missing downstream action or final render.

