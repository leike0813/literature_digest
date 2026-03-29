# sqlite-gated-skill-runtime Specification

## Purpose
TBD - created by archiving change preserve-full-guidance-while-slimming-skill-md. Update Purpose after archive.
## Requirements
### Requirement: Gate References SHALL Resolve To Rich Guidance

The gate payload MUST reference documents that carry the detailed guidance for the current action, not summary-only placeholders.

#### Scenario: Gate emits instruction refs
- **WHEN** the gate returns `instruction_refs`
- **THEN** those references resolve to step/contract docs containing substantive operational guidance
- **AND** the agent does not need to fall back to deleted content from an old monolithic `SKILL.md`

#### Scenario: Gate emits current execution note
- **WHEN** the gate returns a current `next_action`
- **THEN** it also returns an `execution_note` that captures the action's most important immediate instruction

### Requirement: Render Mode SHALL Allow Only Output-Directory Override

The DB-authoritative final render mode SHALL allow an explicit output-directory override but SHALL continue rejecting late input-source overrides.

#### Scenario: Final render uses explicit output directory
- **WHEN** `render_and_validate --mode render` receives `--out-dir`
- **THEN** the runtime writes the fixed artifact filenames into that directory
- **AND** it still reads render content only from the database

#### Scenario: Final render rejects late source overrides
- **WHEN** `render_and_validate --mode render` receives `--source-path`, `--preprocess-artifact`, or `--in`
- **THEN** the runtime fails with a schema-compatible error payload

### Requirement: Gate SHALL Route Suspicious Stage-4 Worksets To Split Review

The SQLite-gated runtime MUST expose `persist_reference_entry_splits` as a stage-4 action when grouped-entry suspicion remains after reference workset preparation.

#### Scenario: Stage 4 grouped-entry suspicion

- **GIVEN** `prepare_references_workset` has prepared reference entries and candidates
- **AND** grouped-entry suspicion remains
- **WHEN** gate evaluates the workflow state
- **THEN** `next_action` is `persist_reference_entry_splits`
- **AND** `execution_note` explains that this step only fixes raw entry boundaries

