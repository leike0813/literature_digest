## ADDED Requirements

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
