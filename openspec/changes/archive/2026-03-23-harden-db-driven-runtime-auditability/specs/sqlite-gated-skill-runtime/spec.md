## MODIFIED Requirements

### Requirement: Main-Path Runtime Inputs SHALL Be DB-Authoritative

The gate-driven runtime MUST treat earlier persisted state as authoritative input for later main-path actions.

#### Scenario: Normalize source stage
- **WHEN** `normalize_source` runs after bootstrap
- **THEN** it reads `runtime_inputs.source_path` and `runtime_inputs.language`
- **AND** it does not reopen those values through late CLI overrides.

#### Scenario: Citation mention preparation stage
- **WHEN** `prepare_citation_mentions` runs
- **THEN** it reads `source_documents.normalized_source` and `section_scopes.citation_scope`
- **AND** it rejects late scope override payloads or CLI inputs.

### Requirement: Auxiliary Tools SHALL Be Separate From Gate Next Actions

Utility-only commands MAY exist, but they MUST not be represented as gate-driven main-path actions.

#### Scenario: Citation workset export
- **WHEN** `export_citation_workset` is used
- **THEN** it reads runtime DB state without mutating it
- **AND** it is documented as an auxiliary helper rather than a required `next_action`.
