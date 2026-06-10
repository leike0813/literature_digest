## ADDED Requirements

### Requirement: Gate Directives For Placeholder Reference Titles

The SQLite-gated runtime SHALL expose placeholder title hard blocks through the existing Stage 4 quality directive contract.

#### Scenario: Gate reports placeholder title repair instructions

- **GIVEN** active `reference_quality_issues` with `reason_code = "placeholder_title"`
- **WHEN** `gate_runtime.py` is run
- **THEN** the payload SHALL include `quality_directives.kind = "stage4_reference_quality"`
- **AND** the issue SHALL include `entry_index`, `ref_index`, `current_value`, `raw_excerpt`, and `recommendation`
- **AND** the recommendation SHALL tell the agent to recover the cited title from raw/candidates or omit the unrecoverable row.
