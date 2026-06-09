## ADDED Requirements

### Requirement: Gate Directives Preserve Original Reference Title Language

The SQLite-gated runtime SHALL present Stage 4 quality directives in a way that preserves original reference title language and script.

#### Scenario: Hard-block command guidance avoids translation

- **GIVEN** active Stage 4 `reference_quality_issues`
- **WHEN** `gate_runtime.py` returns `quality_directives` and `command_example`
- **THEN** the execution note and command notes SHALL instruct the agent to recover the original cited title from raw/candidates
- **AND** SHALL explicitly forbid translating, Anglicizing, or romanizing titles to satisfy the quality gate.

