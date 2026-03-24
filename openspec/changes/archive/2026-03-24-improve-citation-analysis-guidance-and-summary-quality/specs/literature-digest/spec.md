## MODIFIED Requirements

### Requirement: Citation Analysis Summary SHALL Be Narrative And Structured

The skill MUST guide stage-5 summary generation toward narrative review structure instead of category counting.

#### Scenario: Persist global citation summary
- **WHEN** `persist_citation_summary` runs
- **THEN** the payload MUST include `summary` plus required `basis`
- **AND** `basis` MUST include `research_threads`, `argument_shape`, and `key_ref_indexes`
- **AND** the stored summary is treated as a narrative account of how the source paper organizes related work, not a count of citation categories.

#### Scenario: Render final citation report
- **WHEN** the final citation report is rendered
- **THEN** it includes the stored narrative summary
- **AND** it includes a short “Key References” section derived from `basis.key_ref_indexes`.

### Requirement: Citation Item Semantics SHALL Capture Topic And Usage

The skill MUST require more than a coarse function label for each citation workset item.

#### Scenario: Persist citation semantics
- **WHEN** `persist_citation_semantics` runs
- **THEN** each item MUST include `ref_index`, `function`, `topic`, `usage`, `summary`, `is_key_reference`, and `confidence`
- **AND** the runtime rejects items that omit `topic`, omit `usage`, or provide a non-boolean `is_key_reference`.
