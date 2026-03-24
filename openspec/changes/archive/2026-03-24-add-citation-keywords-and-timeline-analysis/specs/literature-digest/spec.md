## MODIFIED Requirements

### Requirement: Citation Analysis SHALL Include Keywords And Timeline

The skill MUST capture richer structured semantics for each cited work and a separate timeline analysis before rendering final citation artifacts.

#### Scenario: Persist citation item semantics
- **WHEN** `persist_citation_semantics` runs
- **THEN** each item MUST include `ref_index`, `function`, `topic`, `usage`, `summary`, `keywords`, `is_key_reference`, and `confidence`
- **AND** `keywords` MUST be a non-empty array of non-empty short phrases.

#### Scenario: Persist timeline analysis
- **WHEN** `persist_citation_timeline` runs
- **THEN** the payload MUST contain `timeline.early`, `timeline.mid`, and `timeline.recent`
- **AND** each bucket MUST contain `summary` and `ref_indexes`
- **AND** every citation item with a stable year MUST appear in exactly one bucket.

### Requirement: Citation Report SHALL Render Richer Human-Readable Entries

The final citation report MUST expose citation metadata in a form that is easier for humans to scan.

#### Scenario: Render citation analysis markdown
- **WHEN** the final citation report is rendered
- **THEN** grouped citation items include `citation_label`, `author_year_label`, `title`, `keywords`, and `summary`
- **AND** the report replaces the old ordered-citation section with a timeline analysis section
- **AND** the timeline analysis contains `early`, `mid`, and `recent` summaries plus representative references.
