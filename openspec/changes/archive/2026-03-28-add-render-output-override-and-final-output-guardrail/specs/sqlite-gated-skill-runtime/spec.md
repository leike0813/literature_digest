## MODIFIED Requirements

### Requirement: Gate References SHALL Resolve To Rich Guidance

The gate payload MUST reference documents that carry the detailed guidance for the current action, not summary-only placeholders.

#### Scenario: Gate emits instruction refs
- **WHEN** the gate returns `instruction_refs`
- **THEN** those references resolve to step/contract docs containing substantive operational guidance
- **AND** the agent does not need to fall back to deleted content from an old monolithic `SKILL.md`

#### Scenario: Gate emits current execution note
- **WHEN** the gate returns a current `next_action`
- **THEN** it also returns an `execution_note` that captures the action's most important immediate instruction

## ADDED Requirements

### Requirement: Render Mode SHALL Allow Only Output-Directory Override

The DB-authoritative final render mode SHALL allow an explicit output-directory override but SHALL continue rejecting late input-source overrides.

#### Scenario: Final render uses explicit output directory
- **WHEN** `render_and_validate --mode render` receives `--out-dir`
- **THEN** the runtime writes the fixed artifact filenames into that directory
- **AND** it still reads render content only from the database

#### Scenario: Final render rejects late source overrides
- **WHEN** `render_and_validate --mode render` receives `--source-path`, `--preprocess-artifact`, or `--in`
- **THEN** the runtime fails with a schema-compatible error payload
