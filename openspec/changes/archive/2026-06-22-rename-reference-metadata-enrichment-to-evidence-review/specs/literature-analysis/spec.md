## ADDED Requirements

### Requirement: Reference Metadata SHALL Be Reviewed From Local Evidence Only

The reference metadata submit round SHALL be agent-facing as Reference Metadata Evidence Review and SHALL forbid external lookup.

#### Scenario: Metadata evidence batch
- **WHEN** core `reference_reviews[]` submit succeeds
- **THEN** stdout includes `metadata_evidence_review_manifest_path` and `metadata_evidence_batch_paths`
- **AND** batch JSON includes `external_lookup_allowed=false`, allowed evidence sources, and forbidden external lookup actions.

#### Scenario: Metadata evidence submit
- **WHEN** the agent submits reference metadata
- **THEN** the payload uses `metadata_evidence_reviews[]`
- **AND** each status is `fields_extracted`, `existing_fields_confirmed`, or `no_local_evidence`.

#### Scenario: Old payload rejected
- **WHEN** a payload contains `metadata_reviews[]`
- **THEN** runtime rejects it with a current-state repair hint.

#### Scenario: External metadata blocked
- **WHEN** DOI, URL, archiveID, ISBN, ISSN, pages, volume, or issue metadata lacks local batch evidence
- **THEN** runtime rejects it with `metadata_without_local_evidence`.

### Requirement: Guidance SHALL Not Describe Metadata Discovery

Skill guidance SHALL describe the round as local evidence review and SHALL explicitly prohibit web search and external bibliographic databases.

#### Scenario: Subagent prompt
- **WHEN** the metadata evidence subagent prompt is generated or documented
- **THEN** it states `This is not a metadata discovery task`
- **AND** it forbids web search, Crossref, arXiv, Google Scholar, Zotero, Semantic Scholar, DOI resolver, and external databases.
