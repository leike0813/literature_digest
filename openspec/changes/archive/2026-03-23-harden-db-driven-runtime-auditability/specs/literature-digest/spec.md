## MODIFIED Requirements

### Requirement: Later Main-Path Stages SHALL Read Persisted Decisions From DB

Once a prior stage has written a decision into the runtime database, later main-path actions MUST read that decision from DB rather than accept a new override through CLI or JSON.

#### Scenario: Citation scope already persisted
- **WHEN** `persist_outline_and_scopes` has already written `section_scopes.citation_scope`
- **THEN** `prepare_citation_mentions` reads that DB scope
- **AND** it does not accept a new scope file, scope range, or payload scope override.

#### Scenario: Final render stage
- **WHEN** `render_and_validate --mode render` runs
- **THEN** it reads artifact inputs and output root from DB
- **AND** it does not accept explicit source-path or out-dir inputs for the main publish path.

### Requirement: References And Citation Outputs SHALL Expose Audit Signals

The skill MUST surface non-blocking audit and reliability signals derived from runtime decisions and structured data quality checks.

#### Scenario: Reference numbering anomaly detected
- **WHEN** references numbering is non-monotonic or non-continuous
- **THEN** the runtime writes warnings and item-level numbering metadata
- **AND** the final citation analysis may lower mapping reliability when numeric mentions depend on those references.
