## ADDED Requirements

### Requirement: Stage 4 SHALL Support Author-Year Entry Split Review

When deterministic reference splitting still groups multiple author-year bibliography items into a single raw entry, the runtime MUST route stage 4 through a split-review action before final reference refinement.

#### Scenario: Grouped author-year entries trigger split review

- **GIVEN** the references scope contains author-year bibliography entries that remain grouped after deterministic preprocessing
- **WHEN** `prepare_references_workset` completes
- **THEN** the runtime reports grouped-entry suspicion
- **AND** gate advances to `persist_reference_entry_splits`
- **AND** the runtime does not proceed directly to `persist_references`

### Requirement: Split Review SHALL Preserve Raw Text Exactly

The split-review action MUST only adjust raw entry boundaries and MUST preserve the original references scope text exactly.

#### Scenario: Reviewed entry boundaries are accepted

- **GIVEN** `persist_reference_entry_splits` receives ordered `entries[*].raw`
- **WHEN** the concatenated reviewed raws match the original references scope text after whitespace normalization
- **THEN** the runtime rebuilds `reference_entries`, `reference_parse_candidates`, and `reference_batches`
- **AND** gate advances to `persist_references`

#### Scenario: Reviewed entry boundaries rewrite or drop text

- **GIVEN** `persist_reference_entry_splits` receives entries whose concatenated text does not match the original references scope text
- **WHEN** validation runs
- **THEN** the runtime fails with `reference_entry_splitting_failed`
