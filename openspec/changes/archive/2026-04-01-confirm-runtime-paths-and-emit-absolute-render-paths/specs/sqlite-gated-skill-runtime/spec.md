## ADDED Requirements

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
