# literature-analysis Specification

## Purpose

`literature-analysis` provides a full paper analysis skill that keeps the public outputs of `literature-digest` while replacing the agent-facing workflow with fewer, decision-oriented stages.

## Requirements

### Requirement: Skill SHALL Be Added In Parallel

The repository SHALL add `literature-analysis` as a new skill package without changing existing `literature-digest` or `literature-digest-lite` behavior.

#### Scenario: Existing skills remain unchanged
- **WHEN** the new skill is added
- **THEN** existing skill directories remain usable under their current names
- **AND** no existing public output contract is removed from them.

### Requirement: Public Output SHALL Remain Full-Compatible

Successful `literature-analysis` stdout SHALL preserve the full `literature-digest` output keys and fixed public artifact filenames.

#### Scenario: Successful output
- **WHEN** `literature-analysis` completes successfully
- **THEN** stdout includes `digest_path`, `references_path`, `citation_analysis_path`, `literature_matching_metadata_path`, `citation_analysis_report_path`, `provenance`, `warnings`, and `error`
- **AND** public artifacts use `digest.md`, `references.json`, `citation_analysis.json`, `citation_analysis.md`, and `literature_matching_metadata.json`.

### Requirement: Runtime SHALL Reuse Mature Deterministic Logic

The first implementation phase SHALL reuse existing deterministic `literature-digest` logic for source normalization, reference preprocessing, citation preprocessing, and final rendering.

#### Scenario: Runtime initialization
- **WHEN** `init_runtime` runs
- **THEN** it initializes SQLite runtime state, persists render templates, normalizes the source, and returns the next agent-facing action.

### Requirement: Stages SHALL Align With Agent Decisions

The new workflow SHALL expose stages at semantic decision points and avoid agent-facing runtime-only stages after initialization.

#### Scenario: Digest and references are separate
- **WHEN** the workflow reaches content generation
- **THEN** `persist_digest` persists digest content independently
- **AND** `persist_references` persists reference extraction independently
- **AND** references preparation does not require a digest payload.

### Requirement: Payloads SHALL Be Agent-Friendly

Agent-facing payloads SHALL be flat where practical, use semantic field names, and avoid requiring the agent to manually restate cross-stage dependencies.

#### Scenario: Dependency context is provided just in time
- **WHEN** a later stage depends on persisted state
- **THEN** the runtime reads SQLite and returns nearby context or workset paths
- **AND** invalid submitted fields produce concrete validation errors.

### Requirement: Subagent Work SHALL Be Explicitly Supported

Reference and citation worksets SHALL include guidance that allows the main agent to delegate batch review to subagents while retaining single-writer SQLite discipline.

#### Scenario: Reference workset prepared
- **WHEN** reference preprocessing completes
- **THEN** the runtime returns workset paths and a suggested subagent prompt
- **AND** the main agent remains responsible for merging results and submitting one persist payload.

### Requirement: Final Rendering SHALL Cascade After Citation Persistence

After citation semantic payloads are persisted, the runtime SHALL render and validate public artifacts without requiring an additional agent semantic decision.

#### Scenario: Citation analysis persisted
- **WHEN** `persist_citation_analysis` receives a valid citation payload
- **THEN** citation semantics, timeline, and summary are persisted
- **AND** final artifacts are rendered and validated automatically.
