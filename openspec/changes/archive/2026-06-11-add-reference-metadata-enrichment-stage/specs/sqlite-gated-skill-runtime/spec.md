## ADDED Requirements

### Requirement: DB-Backed Reference Metadata Enrichment

The SQLite-gated runtime SHALL use a DB-backed workset and receipt to prove reference metadata enrichment was prepared and persisted before normal citation analysis.

#### Scenario: Gate requires enrichment receipt in normal mode

- **GIVEN** reference extraction is not abandoned
- **WHEN** gate evaluates Stage 5 or final render prerequisites
- **THEN** it SHALL require `action_receipts.persist_reference_metadata_enrichment`.

#### Scenario: Persist validates against DB workset

- **WHEN** `persist_reference_metadata_enrichment` is called
- **THEN** it SHALL require every submitted `ref_index` to exist in `reference_metadata_enrichment_workset`
- **AND** it SHALL reject missing, duplicate, or unknown `ref_index` values.

#### Scenario: Single-writer subagent policy

- **WHEN** gate returns reference metadata enrichment instructions
- **THEN** it SHALL allow subagent drafting only as an analysis aid
- **AND** it SHALL instruct that only the main agent submits the merged persist payload.
