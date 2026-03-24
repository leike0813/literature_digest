## MODIFIED Requirements

### Requirement: References Extraction SHALL Use A Prepared Preparse Workset

The references stage MUST prepare deterministic split candidates before the agent writes final `reference_items`.

#### Scenario: Prepare references workset
- **WHEN** `prepare_references_workset` runs
- **THEN** it reads `normalized_source` plus `references_scope`
- **AND** it persists `reference_entries`, `reference_batches`, and `reference_parse_candidates`
- **AND** it exports both a full workset and a lightweight review view.

#### Scenario: Persist refined references
- **WHEN** `persist_references` runs
- **THEN** it accepts only `items[]` keyed by `entry_index` and `selected_pattern`
- **AND** it validates that the selected pattern exists in `reference_parse_candidates`
- **AND** it rejects suspicious title boundaries instead of publishing malformed titles.

### Requirement: References Parsing SHALL Preserve Candidate Ambiguity

The runtime MUST keep all viable deterministic split candidates for ambiguous references.

#### Scenario: Multiple patterns match
- **WHEN** a raw reference entry matches more than one supported split pattern
- **THEN** all matching candidates are stored
- **AND** the agent chooses one `selected_pattern` during refinement instead of reparsing from scratch.
