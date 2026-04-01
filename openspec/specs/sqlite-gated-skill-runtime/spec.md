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

### Requirement: Main-Path Actions SHALL Emit Receipts

The SQLite-gated runtime SHALL persist receipts for successful scripted main-path actions.

#### Scenario: Successful stage action writes receipt
- **WHEN** a main-path action succeeds
- **THEN** the runtime writes or updates an `action_receipts` row for that action

#### Scenario: Upstream rerun invalidates downstream receipts
- **WHEN** an earlier main-path action reruns successfully
- **THEN** the runtime deletes receipts for downstream actions whose outputs are no longer trustworthy

### Requirement: Citation Timeline And Summary SHALL Ground On Persisted Citation Items

Stage-5 aggregate outputs SHALL reference only citation items that completed item-level semantic persistence.

#### Scenario: Timeline references missing citation item
- **WHEN** `persist_citation_timeline` receives a `ref_index` that is absent from `citation_items`
- **THEN** the runtime rejects the payload

#### Scenario: Summary basis references missing citation item
- **WHEN** `persist_citation_summary` receives `basis.key_ref_indexes` containing a `ref_index` absent from `citation_items`
- **THEN** the runtime rejects the payload

### Requirement: Gate separates normal execution commands from repair SQL

The sqlite-gated runtime MUST distinguish normal-path script invocation guidance from repair SQL guidance in its gate payloads.

#### Scenario: Gate emits the correct hint type for the current action

- **WHEN** a gate payload is emitted
- **THEN** non-repair actions surface `command_example`
- **AND** repair actions surface `sql_examples`
- **AND** the two hint types are not redundantly returned together for the same action

### Requirement: Gate SHALL Start New Runs With Runtime Path Confirmation

The SQLite-gated runtime MUST direct new runs to confirm runtime paths before bootstrap.

#### Scenario: DB missing
- **WHEN** `gate_runtime.py` runs and the runtime DB does not exist
- **THEN** it returns `next_action = confirm_runtime_paths`
- **AND** `execution_note` tells the agent to capture shell cwd before calling any skill script.

### Requirement: Render Result Mirror SHALL Use Persisted Result Path

The final render result mirror file MUST use the DB-backed result JSON path.

#### Scenario: Render writes mirror JSON
- **WHEN** `render_and_validate --mode render` completes or fails with a schema-compatible payload
- **THEN** it writes the same JSON object to `runtime_inputs.result_json_path`
- **AND** that mirror path is resolved from SQLite for new runs.

