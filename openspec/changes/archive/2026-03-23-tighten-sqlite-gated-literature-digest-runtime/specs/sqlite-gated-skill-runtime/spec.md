## ADDED Requirements

### Requirement: Gate Runtime SHALL Point To The Right Instructions

The gate payload MUST include explicit document references for the current `next_action`.

#### Scenario: Gate returns a legal action
- **WHEN** the gate returns a `next_action`
- **THEN** it also returns `instruction_refs`
- **AND** those references point to the relevant `references/step_*.md` file and any shared contract document needed for that action.

### Requirement: Gate Runtime SHALL Provide Minimal SQL Examples

The gate payload MUST include SQL examples scoped to the current `next_action`.

#### Scenario: SQL examples emitted
- **WHEN** the gate returns a `next_action`
- **THEN** it also returns `sql_examples`
- **AND** each SQL example contains `purpose`, `sql`, and `notes`
- **AND** the examples are limited to the minimum reads/writes relevant to that action.
