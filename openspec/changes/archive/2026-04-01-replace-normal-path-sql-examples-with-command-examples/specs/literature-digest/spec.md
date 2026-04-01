## ADDED Requirements

### Requirement: Normal-path gate payloads use command examples instead of SQL examples

The literature-digest gate MUST return a `command_example` for non-repair actions and MUST NOT expose executable SQL examples on the normal main path.

#### Scenario: Main-path gate payload returns script command guidance

- **WHEN** `gate_runtime.py` returns a payload whose `next_action` is not a repair action
- **THEN** the payload includes a non-null `command_example`
- **AND** `command_example.command` shows the next `scripts/stage_runtime.py <next_action>` call
- **AND** `command_example.payload_example` is present only when that action expects a payload file
- **AND** `sql_examples` is an empty array

### Requirement: Repair gate payloads keep SQL examples

Repair guidance MUST continue to surface SQL examples through the existing gate field.

#### Scenario: Repair payload keeps SQL repair hints

- **WHEN** `gate_runtime.py` returns a payload whose `next_action` starts with `repair_`
- **THEN** the payload includes repair-oriented `sql_examples`
- **AND** `command_example` is `null`
