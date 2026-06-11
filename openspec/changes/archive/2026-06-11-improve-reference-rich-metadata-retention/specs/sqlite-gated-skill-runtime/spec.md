## ADDED Requirements

### Requirement: Gate Guides Rich Reference Metadata Completion

The SQLite-gated runtime SHALL expose missing rich reference metadata evidence through existing Stage 4 quality directives.

#### Scenario: Gate reports rich metadata warning

- **GIVEN** active `reference_quality_issues` with `reason_code = "rich_metadata_evidence_missing"`
- **WHEN** `gate_runtime.py` is run
- **THEN** the payload SHALL route the agent to `review_reference_quality`
- **AND** the issue SHALL include evidence and a recommendation to add supported fields or explicitly accept the warning when unreliable.
