# Delta: sqlite-gated-skill-runtime

## ADDED Requirements

### Requirement: Main-Path Actions SHALL Emit Receipts

The SQLite-gated runtime SHALL persist receipts for successful scripted main-path actions.

#### Scenario: Successful stage action writes receipt
- **WHEN** a main-path action succeeds
- **THEN** the runtime writes or updates an `action_receipts` row for that action

#### Scenario: Upstream rerun invalidates downstream receipts
- **WHEN** an earlier main-path action reruns successfully
- **THEN** the runtime deletes receipts for downstream actions whose outputs are no longer trustworthy

### Requirement: Citation Timeline And Summary SHALL Ground On Persisted Citation Items

Stage-5 aggregate outputs SHALL reference only citation items that completed item-level semantic persistence.

#### Scenario: Timeline references missing citation item
- **WHEN** `persist_citation_timeline` receives a `ref_index` that is absent from `citation_items`
- **THEN** the runtime rejects the payload

#### Scenario: Summary basis references missing citation item
- **WHEN** `persist_citation_summary` receives `basis.key_ref_indexes` containing a `ref_index` absent from `citation_items`
- **THEN** the runtime rejects the payload
