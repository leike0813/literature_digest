# literature-analysis Delta Specification

## Requirements

### Requirement: References SHALL Use Current Agent-Facing Review Payload

`persist_references` submit SHALL accept `reference_reviews[]` keyed by `reference_key` and SHALL reject old runtime-oriented submit fields.

#### Scenario: Reference review is submitted
- **WHEN** the payload contains `reference_reviews[]`
- **THEN** runtime maps `reference_key` and `selected_parse_pattern` to prepared candidates
- **AND** persists compatible reference items.

### Requirement: Citation SHALL Use Work Keys And Runtime-Derived Timeline

`persist_citation_analysis` submit SHALL accept `citation_semantic_reviews[]` keyed by `citation_work_key` and `timeline_summaries`, not internal `ref_index` or `timeline.*.ref_indexes`.

#### Scenario: Citation review is submitted
- **WHEN** semantic reviews and timeline summaries are valid
- **THEN** runtime persists citation semantics
- **AND** derives timeline bucket membership from citation item years.

### Requirement: Prepare Responses SHALL Include Subagent Work Packages

Reference and citation prepare outputs SHALL include batch packages, field guidance, merge contracts, and subagent prompt templates.

#### Scenario: Workset is prepared
- **WHEN** prepare succeeds
- **THEN** the response includes enough JIT information for agents and subagents to fill only the current payload shape.
