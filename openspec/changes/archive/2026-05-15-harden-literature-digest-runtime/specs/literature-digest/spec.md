## ADDED Requirements

### Requirement: Reference Splitting SHALL Avoid Venue False Positives

Reference splitting SHALL NOT treat venue fragments or author initials as strong
reference starts without additional reference-entry evidence.

#### Scenario: Proceedings text inside one reference

- **GIVEN** a reference contains `In Proceedings ...`
- **WHEN** the references workset is prepared
- **THEN** that venue phrase does not by itself create a new reference entry.

#### Scenario: Inline numeric entries

- **GIVEN** one references line contains multiple numeric entries such as
  `[42] ... [43] ...`
- **WHEN** the references workset is prepared
- **THEN** the line is split into separate entries when both numeric markers are
  strong entry starts.

### Requirement: Split Review SHALL Support Stable False-Positive Resolution

Split review SHALL expose the current suspect generation and allow a reviewed
block to be force-kept when the agent confirms the suspicion is false.

#### Scenario: Force keep suspect block

- **GIVEN** `prepare_references_workset` reports a suspect block
- **WHEN** `persist_reference_entry_splits` receives `resolution = force_keep`
- **THEN** the block is accepted as a single reference entry
- **AND** the runtime does not re-enter split review for the same block.

### Requirement: Citation Function Contract SHALL Be Visible

Citation function values SHALL remain a fixed enum and the valid values SHALL
be visible in SKILL and stage guidance.

#### Scenario: Unsupported function value

- **WHEN** `persist_citation_semantics` receives an unsupported function value
- **THEN** the runtime normalizes it to `uncategorized`
- **AND** emits a warning that names the allowed function values.

### Requirement: Citation Timeline SHALL Remain Closed Over Dated Items

Citation timeline validation SHALL require every dated citation item to appear
in exactly one timeline bucket.

#### Scenario: Missing dated citation item

- **WHEN** a dated citation item is missing from `early`, `mid`, and `recent`
- **THEN** `persist_citation_timeline` rejects the payload with a clear missing
  `ref_index` message.
