## ADDED Requirements

### Requirement: Citation Analysis SHALL Persist Tolerant Best-Effort Results

The literature-analysis runtime MUST persist citation analysis as a tolerant best-effort stage when normalized source, citation scope, and known citation keys are available. The runtime MUST NOT invent semantic citation content for missing reviews.

#### Scenario: Empty citation payload persists
- **WHEN** `persist_citation_analysis` receives no `citation_semantic_reviews`, no `timeline_summaries`, and no global `summary`
- **THEN** the runtime persists empty citation items
- **AND** persists citation timeline buckets with empty summaries
- **AND** persists an empty global citation summary
- **AND** final rendering can produce all public artifacts.

#### Scenario: Partial citation review coverage persists
- **WHEN** `persist_citation_analysis` receives reviews for only some known `citation_work_key` values
- **THEN** the runtime persists only the submitted known citation items
- **AND** it MUST NOT create placeholder items for missing keys
- **AND** final rendering can produce all public artifacts.

#### Scenario: Empty semantic fields are accepted
- **WHEN** a submitted citation review omits or leaves empty `topic`, `usage`, `role_in_context`, `keywords`, or `summary`
- **THEN** the runtime persists the field as an empty string or empty array
- **AND** it MUST NOT generate replacement semantic text.

#### Scenario: Duplicate citation keys are merged
- **WHEN** multiple submitted reviews use the same known `citation_work_key`
- **THEN** the runtime merges them into one persisted citation item
- **AND** string fields use the first non-empty value
- **AND** `keywords` are merged and deduplicated in first-seen order
- **AND** the duplicate does not block persistence.

#### Scenario: Unsafe citation payload remains rejected
- **WHEN** a submitted citation review uses an unknown `citation_work_key` or includes forbidden internal fields
- **THEN** the runtime rejects the payload
- **AND** it does not persist partial citation state from that payload.

#### Scenario: Citation workset can be empty
- **WHEN** citation scope exists but deterministic citation extraction produces no stable mapped workset
- **THEN** citation preparation succeeds with an empty workset
- **AND** later citation persistence and rendering can produce a schema-compatible citation artifact.

#### Scenario: Empty public citation summary is valid
- **WHEN** final rendering builds `citation_analysis.json` with an empty `summary` string
- **THEN** public output validation accepts the citation artifact
- **AND** the final stdout payload can report success.
