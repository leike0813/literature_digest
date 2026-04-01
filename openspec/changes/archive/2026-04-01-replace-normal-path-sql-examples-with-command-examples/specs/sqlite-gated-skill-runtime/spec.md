## ADDED Requirements

### Requirement: Gate separates normal execution commands from repair SQL

The sqlite-gated runtime MUST distinguish normal-path script invocation guidance from repair SQL guidance in its gate payloads.

#### Scenario: Gate emits the correct hint type for the current action

- **WHEN** a gate payload is emitted
- **THEN** non-repair actions surface `command_example`
- **AND** repair actions surface `sql_examples`
- **AND** the two hint types are not redundantly returned together for the same action
