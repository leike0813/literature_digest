## ADDED Requirements

### Requirement: Gate returns a fixed core instruction block

The literature-digest runtime gate MUST return a `core_instruction` string in every payload.

#### Scenario: Main-path gate payload includes core instruction

- **WHEN** `gate_runtime.py` returns a payload for any workflow stage
- **THEN** the payload includes `core_instruction`
- **AND** it contains the compact cross-stage execution rules
- **AND** it remains stable across stages

### Requirement: Final stdout JSON guidance uses concrete examples

Guidance documents that define the final stdout JSON contract MUST include concrete JSON examples.

#### Scenario: Final stdout JSON is documented with examples

- **WHEN** `SKILL.md`, bootstrap guidance, render guidance, or runtime interface docs describe final stdout JSON
- **THEN** they include a success JSON example or failure JSON example, as appropriate
- **AND** they do not rely only on field bullet lists
