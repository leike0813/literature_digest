## ADDED Requirements

### Requirement: Reference Core Review SHALL Exclude Metadata

The reference core review payload SHALL only accept core reference fields and SHALL reject rich metadata inside `reference_reviews[]`.

#### Scenario: Metadata submitted in core review
- **WHEN** `persist_references` receives `reference_reviews[].metadata`
- **THEN** it returns `reference_payload_invalid`
- **AND** the error tells the agent to submit metadata through the metadata review round.

### Requirement: Metadata Enrichment SHALL Be A Separate Reference Round

After core references are persisted, the runtime SHALL generate metadata review packages and require a metadata review payload before moving to citation analysis.

#### Scenario: Core references persisted
- **WHEN** `persist_references` receives valid `reference_reviews[]`
- **THEN** it persists core reference items
- **AND** returns `metadata_review_packages`
- **AND** keeps `next_action` as `persist_references`.

#### Scenario: Metadata reviews persisted
- **WHEN** `persist_references` receives valid `metadata_reviews[]` covering every metadata package
- **THEN** it persists metadata enrichment
- **AND** returns `next_action = "persist_citation_analysis"`.

### Requirement: Metadata Workset SHALL Keep Static Contract At Instruction Level

The metadata enrichment workset SHALL keep `allowed_metadata_fields` and `locked_fields` in instruction-level data instead of repeating them on every item.

#### Scenario: Metadata workset is exported
- **WHEN** runtime writes `reference_metadata_enrichment_workset.json`
- **THEN** top-level `instructions` includes `allowed_metadata_fields` and `locked_fields`
- **AND** each item contains only item-specific review context.

### Requirement: Public References SHALL Exclude Parse Audit Fields

Public `references.json` SHALL expose bibliographic reference data and SHALL NOT include internal parse audit fields.

#### Scenario: References are rendered
- **WHEN** final outputs are rendered
- **THEN** each reference item excludes `selected_pattern`, `pattern_candidate`, and `entry_index`
- **AND** public bibliographic fields and enriched metadata remain available.

### Requirement: Reference Parse Audit SHALL Be Available As Tmp Sidecar

The runtime SHALL write a tmp audit sidecar for parse selections and candidates.

#### Scenario: References rendered after core review
- **WHEN** final outputs are rendered
- **THEN** `.literature_analysis_tmp/reference_parse_audit.json` contains selected parse pattern and candidate details for each reference.
