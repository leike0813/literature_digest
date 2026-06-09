## ADDED Requirements

### Requirement: Stage 4 SHALL Use Deterministic Reference Preprocess v1.7.1

The main `literature-digest` skill SHALL prepare Stage 4 reference entries and parse candidates using the deterministic line-first v1.7.1 behavior, including CJK/fullwidth handling, author-initial protection, IEEE quoted-title parsing, venue-marker parsing, non-reference line filtering, trailing page-marker cleanup, bilingual entry merge, and file-level quality detection.

#### Scenario: CJK reference produces structured candidates

- **WHEN** a references scope contains CJK/fullwidth bibliography lines with type markers
- **THEN** `prepare_references_workset` emits parse candidates that preserve original raw text and include title/year candidates when deterministically recoverable.

#### Scenario: File quality signal is persisted

- **WHEN** `prepare_references_workset` completes
- **THEN** the runtime persists v1.7.1 file-level quality metrics
- **AND** the workset export includes `file_quality` and `file_quality_low`.

### Requirement: Low-Quality Reference Files MAY Be Explicitly Abandoned

When deterministic preprocessing reports file-level reference quality as low, the skill SHALL let the agent explicitly continue reference extraction or abandon it. Abandonment SHALL be allowed only through a gate-directed action and SHALL be auditable in DB state.

#### Scenario: Low-quality file routes to extraction decision

- **GIVEN** deterministic preprocessing produced `file_quality_low = true`
- **WHEN** Stage 4 gate is evaluated
- **THEN** the next action is `decide_reference_extraction`
- **AND** the gate instructions explain both the continue and abandon choices.

#### Scenario: Abandoned references render as an empty array

- **GIVEN** the agent explicitly abandoned reference extraction through the guarded action
- **WHEN** final artifacts are rendered
- **THEN** `references.json` is a bare empty array
- **AND** `citation_analysis.json.meta.reference_extraction.status = "abandoned"`.

### Requirement: Reference-Free Citation Analysis SHALL Skip Ref-Index Mapping Checks Only After Verified Abandonment

Citation analysis SHALL skip `ref_index` mapping requirements only when reference extraction was explicitly abandoned after DB-backed low-quality preprocessing.

#### Scenario: Reference-free citation analysis succeeds

- **GIVEN** reference extraction was abandoned after deterministic low-quality detection
- **WHEN** Stage 5 citation analysis runs
- **THEN** citation mentions are still extracted
- **AND** unresolved mentions are retained with a stable abandon reason
- **AND** semantic items, timeline ref indexes, and summary key refs may be empty.

#### Scenario: Normal citation analysis remains strict

- **GIVEN** reference extraction was not abandoned
- **WHEN** Stage 5 payloads omit required `ref_index` mappings
- **THEN** the runtime rejects them as before.
