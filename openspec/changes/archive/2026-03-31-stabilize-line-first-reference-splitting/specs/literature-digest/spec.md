## ADDED Requirements

### Requirement: Stage 4 references preprocessing is line-first

The literature-digest references stage MUST treat each non-empty line in `references_scope` as the initial deterministic splitting unit.

#### Scenario: Deterministic splitting starts from lines

- **WHEN** `prepare_references_workset` processes a references scope
- **THEN** it first creates line-based source blocks
- **AND** it only performs inline splitting within a single line when another strong reference start is detected
- **AND** it does not silently merge possible multiline continuations

### Requirement: Split review operates on suspect blocks

The references split review MUST be limited to suspect blocks rather than a whole replacement `entries[]` payload.

#### Scenario: Reviewing suspicious reference boundaries

- **WHEN** `prepare_references_workset` marks `requires_split_review=true`
- **THEN** it exposes `suspect_blocks`
- **AND** `persist_reference_entry_splits` accepts only reviewed `blocks[]`
- **AND** each reviewed block declares `split`, `keep`, or `merge`

