## ADDED Requirements

### Requirement: Runtime guidance does not require historical traceability docs

The sqlite-gated literature-digest runtime MUST not present migration or legacy snapshot documents as runtime guidance inputs.

#### Scenario: Runtime guidance references only active docs

- **WHEN** agent-facing docs explain what to read during execution
- **THEN** they point to the active runtime docs and appendices
- **AND** they do not instruct the agent to read migration maps or legacy snapshots during execution
