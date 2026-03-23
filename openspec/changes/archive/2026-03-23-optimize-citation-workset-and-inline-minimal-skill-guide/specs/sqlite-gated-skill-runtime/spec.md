## MODIFIED Requirements

### Requirement: Gate-Driven Citation Analysis SHALL Use Workset-First Actions

The gate-driven runtime MUST expose citation preparation and citation semantics as separate actions over a persisted workset.

#### Scenario: Citation workset action
- **WHEN** the runtime reaches citation preparation
- **THEN** gate returns `prepare_citation_workset`
- **AND** that action persists mention extraction and mention-reference linkage before semantic analysis begins.

#### Scenario: Citation summary action
- **WHEN** citation semantics have been persisted
- **THEN** gate returns `persist_citation_summary`
- **AND** final rendering remains blocked until the global citation summary exists.

### Requirement: SKILL Guidance SHALL Be Read On Demand

The runtime guidance model MUST prefer stage-local appendix reads over eager preload of every detailed document.

#### Scenario: External guidance references
- **WHEN** gate returns `instruction_refs`
- **THEN** they point only to the current stage appendix and required interfaces
- **AND** they do not include removed guidance aggregates such as `references/runtime_playbook.md` or `references/rendering_contracts.md`.
