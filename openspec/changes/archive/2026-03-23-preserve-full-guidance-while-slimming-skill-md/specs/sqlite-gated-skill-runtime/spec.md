## ADDED Requirements

### Requirement: Gate References SHALL Resolve To Rich Guidance

The gate payload MUST reference documents that carry the detailed guidance for the current action, not summary-only placeholders.

#### Scenario: Gate emits instruction refs
- **WHEN** the gate returns `instruction_refs`
- **THEN** those references resolve to step/contract docs containing substantive operational guidance
- **AND** the agent does not need to fall back to deleted content from an old monolithic `SKILL.md`.
