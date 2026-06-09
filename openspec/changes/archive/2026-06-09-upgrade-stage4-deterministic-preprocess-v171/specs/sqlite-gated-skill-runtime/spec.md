## ADDED Requirements

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
