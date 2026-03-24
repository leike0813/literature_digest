## MODIFIED Requirements

### Requirement: Stage 4 SHALL Be A Prepare-Then-Persist Flow

The gate-driven runtime MUST expose references preparse and references persistence as separate stage-4 actions.

#### Scenario: Stage 4 action order
- **WHEN** digest persistence completes
- **THEN** gate returns `prepare_references_workset`
- **AND** only after that succeeds may gate return `persist_references`.

#### Scenario: Stage 4 prerequisites
- **WHEN** gate evaluates `persist_references`
- **THEN** it requires `reference_entries` and `reference_parse_candidates`
- **AND** it blocks with repair guidance when those prepared rows are missing.

### Requirement: Stage Runtime Interface SHALL Reject Legacy Reference Payloads

The stage runtime MUST reject the legacy one-step references payload once the workset-first stage-4 flow is active.

#### Scenario: Legacy references payload
- **WHEN** `persist_references` receives `entries` or `batches`
- **THEN** it fails the action
- **AND** it instructs the caller to use prepared candidates plus refined `items[]` instead.
