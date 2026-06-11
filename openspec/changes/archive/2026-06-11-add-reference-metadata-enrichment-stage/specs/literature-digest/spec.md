## ADDED Requirements

### Requirement: Reference Metadata Enrichment Stage

`literature-digest` SHALL enrich optional reference metadata in a dedicated Stage 4 step after core reference rows and reference quality review are complete.

#### Scenario: Normal references route through enrichment before citation

- **WHEN** `persist_references` succeeds with no active quality issues
- **THEN** the next action SHALL be `prepare_reference_metadata_enrichment`
- **AND** citation workset preparation SHALL require completed metadata enrichment.

#### Scenario: Quality review routes through enrichment

- **WHEN** `review_reference_quality` resolves or accepts every active issue
- **THEN** the next action SHALL be `prepare_reference_metadata_enrichment`.

#### Scenario: Enrichment updates rendered references

- **WHEN** `persist_reference_metadata_enrichment` submits supported optional metadata for a `ref_index`
- **THEN** the runtime SHALL merge those fields into the corresponding reference metadata
- **AND** final `references.json` SHALL expose them on that reference object.

#### Scenario: Reference-free mode skips enrichment

- **GIVEN** reference extraction was explicitly abandoned based on DB-backed low file quality
- **WHEN** the workflow enters Stage 5
- **THEN** metadata enrichment SHALL NOT be required.

### Requirement: Reference Quality Review

Reference quality review SHALL focus on core reference row quality and SHALL NOT use missing optional rich metadata as a `reference_quality_issues` warning.

#### Scenario: Missing optional metadata does not create quality issue

- **WHEN** a raw reference contains DOI, venue, pages, or URL evidence
- **AND** `persist_references` omits those optional fields
- **THEN** the runtime SHALL NOT emit `rich_metadata_evidence_missing`
- **AND** the workflow SHALL continue to reference metadata enrichment.
