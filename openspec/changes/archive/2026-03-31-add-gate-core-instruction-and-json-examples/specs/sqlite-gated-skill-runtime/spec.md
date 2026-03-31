## ADDED Requirements

### Requirement: Gate payload distinguishes persistent and step-local guidance

The sqlite-gated runtime MUST separate always-on core guidance from step-local guidance.

#### Scenario: Gate returns both instruction layers

- **WHEN** the runtime gate returns a workflow payload
- **THEN** it includes a stable `core_instruction`
- **AND** it includes a step-specific `execution_note`
- **AND** the two fields serve distinct roles rather than duplicating each other
