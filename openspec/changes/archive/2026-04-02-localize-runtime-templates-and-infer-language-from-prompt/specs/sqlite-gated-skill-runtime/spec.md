## ADDED Requirements

### Requirement: Gate SHALL Route Bootstrap To Runtime Template Persistence

The SQLite-gated runtime SHALL expose `persist_render_templates` as the required action immediately after bootstrap succeeds.

#### Scenario: Bootstrap receipt exists

- **WHEN** `bootstrap_runtime_db` has completed successfully
- **THEN** gate returns `next_action = persist_render_templates`
- **AND** `normalize_source` remains blocked until runtime template paths and receipts exist

### Requirement: Gate And Render SHALL Require Runtime Template Receipts

The runtime SHALL treat persisted runtime templates as a first-class prerequisite for new render workflows.

#### Scenario: Missing template receipt before render

- **WHEN** stage 6 is reached without a `persist_render_templates` receipt in a new workflow
- **THEN** gate does not allow `render_and_validate`
- **AND** render fails with a schema-compatible error payload if invoked anyway
