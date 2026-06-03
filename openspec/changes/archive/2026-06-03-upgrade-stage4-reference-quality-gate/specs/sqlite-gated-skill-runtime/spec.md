## ADDED Requirements

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

