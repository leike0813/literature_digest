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

### Requirement: Gate SHALL Route Bootstrap To Runtime Template Persistence

The SQLite-gated runtime SHALL expose `persist_render_templates` as the required action immediately after bootstrap succeeds.

#### Scenario: Bootstrap receipt exists

- **WHEN** `bootstrap_runtime_db` has completed successfully
- **THEN** gate returns `next_action = persist_render_templates`
- **AND** `normalize_source` remains blocked until runtime template paths and receipts exist

### Requirement: Gate And Render SHALL Require Runtime Template Receipts

The runtime SHALL treat persisted runtime templates as a first-class prerequisite for new render workflows.

#### Scenario: Missing template receipt before render

- **WHEN** stage 6 is reached without a `persist_render_templates` receipt in a new workflow
- **THEN** gate does not allow `render_and_validate`
- **AND** render fails with a schema-compatible error payload if invoked anyway

### Requirement: LaTeX Runtime Metadata

The runtime SHALL persist LaTeX normalization metadata for later stages and auditing.

#### Scenario: LaTeX normalization succeeds

- **WHEN** `normalize_source` processes a `.tex` file or LaTeX project directory
- **THEN** `source_documents.normalized_source.metadata_json` includes `source_type`, `detection_method`, `conversion_backend`, and any resolved `main_tex_path` / `included_tex_files` / `bib_files`

### Requirement: Citekey-Aware Citation Workset

The citation workset SHALL allow mentions to carry citekey hints and references to expose citekey aliases through metadata without changing public output schema.

#### Scenario: Reference item has citekey metadata

- **WHEN** a reference item originates from `\bibitem` or `.bib`
- **THEN** its metadata retains the citekey or bibitem key for citekey-first mention mapping

### Requirement: Runtime Diagnostics SHALL Have Active Lifecycle

Runtime errors and warnings SHALL distinguish active diagnostics from historical
audit records without changing the public stdout schema.

#### Scenario: Recovered error does not pollute final payload

- **GIVEN** a stage records a runtime error
- **AND** the same stage is later completed successfully
- **WHEN** final stdout payload is built
- **THEN** the stale error is not returned in `error`
- **AND** the historical error remains available in SQLite for audit.

#### Scenario: Final warnings are aggregated

- **GIVEN** many active warnings share the same warning category
- **WHEN** final stdout payload is built
- **THEN** `warnings` contains a concise category-level string
- **AND** the stdout JSON schema remains unchanged.

### Requirement: Gate SHALL Expose Formal Repair Command

The SQLite-gated runtime SHALL provide a scripted repair command when the gate
routes execution to `repair_db_state`.

#### Scenario: Missing prerequisites route to repair command

- **WHEN** gate detects missing prerequisites for the current stage
- **THEN** `next_action` is `repair_db_state`
- **AND** `command_example.command` invokes `scripts/stage_runtime.py repair_db_state`
- **AND** SQL examples are treated as secondary diagnostic guidance.

### Requirement: Built-In Runtime Templates MAY Auto-Persist

The runtime SHALL allow built-in `zh-*` and `en-*` templates to be persisted
without an agent-authored template payload.

#### Scenario: Chinese or English target language

- **GIVEN** `runtime_inputs.language` starts with `zh` or `en`
- **WHEN** `persist_render_templates` is called without a payload file
- **THEN** the runtime copies the matching repository templates into the
  runtime templates directory
- **AND** records their paths in SQLite.

### Requirement: UTF-8 SHALL Be Explicit For Script IO

Runtime scripts SHALL explicitly use UTF-8 for JSON payload files and terminal
output where supported.

#### Scenario: Non-ASCII payload path or content

- **WHEN** a payload file contains non-ASCII text
- **THEN** the runtime reads and writes it as UTF-8
- **AND** stdout remains valid JSON text.

### Requirement: Runtime SHALL Persist Matching Metadata In SQLite

The SQLite-gated runtime SHALL store literature matching metadata in a dedicated DB table and use that table as the only render source for the public sidecar.

#### Scenario: Matching metadata persistence succeeds

- **WHEN** `persist_outline_and_scopes` receives valid matching metadata
- **THEN** the runtime writes it to SQLite
- **AND** subsequent render reads the DB value instead of recomputing it.

#### Scenario: Invalid matching metadata is rejected

- **WHEN** matching metadata is missing required fields, uses the wrong schema, has non-array fields, has non-string array items, or exceeds field limits
- **THEN** `persist_outline_and_scopes` fails
- **AND** the workflow does not advance.

### Requirement: Runtime SHALL Render And Validate Matching Metadata Artifact

The final render path SHALL materialize, register, and validate `literature_matching_metadata.json`.

#### Scenario: Render registers matching metadata artifact

- **WHEN** `render_and_validate --mode render` completes
- **THEN** `artifact_registry` contains `literature_matching_metadata_path`
- **AND** `build_public_output_payload()` returns that absolute path.

#### Scenario: Check mode validates matching metadata file

- **WHEN** `render_and_validate --mode check` receives a non-empty `literature_matching_metadata_path`
- **THEN** it validates the referenced JSON object against the v1 shape.

### Requirement: DB-Backed Reference Quality Directives

The SQLite-gated runtime SHALL store active Stage 4 reference quality issues in DB and expose them through gate payloads.

#### Scenario: Gate reports hard block directives

- **GIVEN** active `reference_quality_issues` with `severity = "hard_block"`
- **WHEN** `gate_runtime.py` is run
- **THEN** the payload SHALL include `quality_directives.kind = "stage4_reference_quality"`
- **AND** `quality_directives.severity = "hard_block"`
- **AND** every issue SHALL include `issue_id`, `entry_index`, `ref_index`, `reason_code`, `field`, `current_value`, `raw_excerpt`, and `recommendation`.

#### Scenario: Gate reports soft warning review directives

- **GIVEN** active `reference_quality_issues` with only `severity = "warning"`
- **WHEN** `gate_runtime.py` is run
- **THEN** the payload SHALL route to or describe `review_reference_quality`
- **AND** `quality_directives` SHALL explain that every warning must be corrected or explicitly accepted.

### Requirement: Gate Directives Preserve Original Reference Title Language

The SQLite-gated runtime SHALL present Stage 4 quality directives in a way that preserves original reference title language and script.

#### Scenario: Hard-block command guidance avoids translation

- **GIVEN** active Stage 4 `reference_quality_issues`
- **WHEN** `gate_runtime.py` returns `quality_directives` and `command_example`
- **THEN** the execution note and command notes SHALL instruct the agent to recover the original cited title from raw/candidates
- **AND** SHALL explicitly forbid translating, Anglicizing, or romanizing titles to satisfy the quality gate.

### Requirement: Runtime SHALL Persist Deterministic Reference Preprocess Quality

The SQLite-gated runtime SHALL store the deterministic reference preprocess quality snapshot in DB and SHALL use that DB row as the only authority for allowing reference extraction abandonment.

#### Scenario: Quality snapshot is DB-backed

- **WHEN** `prepare_references_workset` completes
- **THEN** `reference_preprocess_quality` contains the schema/version, metric values, triggered signal names, and `file_quality_low`.

#### Scenario: Payload cannot spoof low-quality status

- **WHEN** `decide_reference_extraction` receives `decision = "abandon"`
- **AND** DB state does not contain a deterministic `file_quality_low = true` snapshot
- **THEN** the runtime rejects the action regardless of the payload contents.

### Requirement: Gate SHALL Expose Guarded Reference Extraction Decision

The gate SHALL route low-quality reference preprocess results through `decide_reference_extraction` and SHALL explain that abandonment is optional but only allowed because of the deterministic DB-backed signal.

#### Scenario: Gate emits decision command example

- **GIVEN** workflow state is `stage_4_references / decide_reference_extraction`
- **WHEN** `gate_runtime.py` runs
- **THEN** the payload contains a command example with both `continue` and `abandon` payload examples
- **AND** the execution note states that the gate/runtime will verify the DB-backed low-quality signal.

### Requirement: Runtime SHALL Support Reference-Free Citation Preconditions

When reference extraction has been verified as abandoned, gate and render prerequisites SHALL require Stage 5 action receipts but SHALL NOT require non-empty reference/citation mapping tables.

#### Scenario: Stage 6 allows reference-free render

- **GIVEN** reference extraction is verified abandoned
- **AND** Stage 5 actions completed with receipts
- **WHEN** gate evaluates Stage 6
- **THEN** missing non-empty `reference_items`, `citation_workset_items`, or `citation_items` do not route to repair.

#### Scenario: Normal render remains strict

- **GIVEN** reference extraction is not abandoned
- **WHEN** Stage 6 lacks non-empty reference or citation mapping rows
- **THEN** gate and render prerequisites reject the state as before.

### Requirement: Gate Directives For Placeholder Reference Titles

The SQLite-gated runtime SHALL expose placeholder title hard blocks through the existing Stage 4 quality directive contract.

#### Scenario: Gate reports placeholder title repair instructions

- **GIVEN** active `reference_quality_issues` with `reason_code = "placeholder_title"`
- **WHEN** `gate_runtime.py` is run
- **THEN** the payload SHALL include `quality_directives.kind = "stage4_reference_quality"`
- **AND** the issue SHALL include `entry_index`, `ref_index`, `current_value`, `raw_excerpt`, and `recommendation`
- **AND** the recommendation SHALL tell the agent to recover the cited title from raw/candidates or omit the unrecoverable row.

