## ADDED Requirements

### Requirement: Main-path payload validation is explicit and field-level
The runtime SHALL reject malformed stage payloads before they mutate the database.

#### Scenario: Outline payload uses the wrong shape
- **WHEN** `persist_outline_and_scopes` receives `outline_nodes` items without `node_id`, `heading_level`, `title`, `line_start`, `line_end`, or `parent_node_id`
- **THEN** the command MUST fail with a stage error
- **AND** the database MUST remain at the pre-write state for that action

### Requirement: Citation workset preparation reports filtered noise
The runtime SHALL track deterministic false-positive filtering during workset preparation.

#### Scenario: False-positive mentions are removed
- **WHEN** `prepare_citation_workset` filters markdown-noise candidates
- **THEN** the command output MUST report the filtered count
- **AND** the runtime MUST persist a warning category for that filtering event

### Requirement: Repair guidance is available as an explicit appendix
The runtime SHALL expose a dedicated recovery guide for repair-oriented gate flows.

#### Scenario: Gate enters repair mode
- **WHEN** the gate returns a repair-oriented `next_action`
- **THEN** its guidance references MUST include the failure recovery appendix
