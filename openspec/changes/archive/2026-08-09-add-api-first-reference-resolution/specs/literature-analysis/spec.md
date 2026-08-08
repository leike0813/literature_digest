## ADDED Requirements

### Requirement: Literature Analysis SHALL Accept A Stable Source Identifier

The skill SHALL accept an optional `identifier` parameter for DOI and arXiv identifiers and SHALL persist a nullable, source-grounded `source_identity` in the analysis plan.

#### Scenario: Explicit identifier is valid
- **WHEN** `init_runtime` receives a supported DOI or arXiv identifier
- **THEN** runtime stores its canonical form as the preferred reference API lookup identity

#### Scenario: Explicit identifier is invalid
- **WHEN** `init_runtime` receives a non-empty unsupported identifier
- **THEN** runtime records a warning
- **AND** reference preparation uses the persisted analysis-plan source identity when one is available

#### Scenario: Analysis plan identifies the source
- **WHEN** `persist_analysis_plan` submits a non-null `source_identity`
- **THEN** the identifier is supported by quoted normalized-source evidence outside `references_scope`
- **AND** runtime persists it for later reference resolution

### Requirement: Reference Preparation SHALL Resolve Public API Records Before Semantic Review

After deterministic local entries and parse candidates are prepared, runtime SHALL query Crossref for DOI sources and Semantic Scholar for DOI or arXiv sources, normalize their reference records, and conservatively match complete records before split-review packages are externalized.

#### Scenario: API records match local entries
- **WHEN** complete provider records have a unique high-confidence identifier or title match to prepared entries
- **THEN** runtime persists those entries as API-resolved reference items
- **AND** retains the local entry index, order, raw text, and selected local parse candidate

#### Scenario: Provider response contains extra or reordered records
- **WHEN** provider records differ in count or order from prepared entries
- **THEN** runtime neither creates nor removes local reference entries
- **AND** unmatched provider records remain audit-only

#### Scenario: Reference boundaries require review
- **WHEN** local preparation requires split review
- **THEN** runtime first matches API candidates to the deterministically prepared entries
- **AND** suppresses a suspect block only when every mapped entry is API-accepted
- **AND** retains the complete block, source text, and proposed fragments when any mapped entry remains unresolved

#### Scenario: Semantic Scholar arXiv title candidate is not an exact identifier match
- **WHEN** a title candidate comes from Semantic Scholar and contains a normalized arXiv identifier
- **THEN** its title score MUST be at least 0.95 before it participates in mutual-best uniqueness checks
- **AND** other non-exact title candidates retain the 0.90 threshold and 0.05 margin

#### Scenario: Split review changes accepted entry boundaries
- **WHEN** a partially API-accepted suspect block is submitted with corrected boundaries
- **THEN** runtime clears prior entry resolutions, retains the cached provider response, and rematches the regenerated entries

### Requirement: Public API Resolution SHALL Degrade To Local Review

Provider unavailability, rate limiting, malformed responses, empty results, incomplete records, and ambiguous matches SHALL be warning-only conditions for reference extraction.

#### Scenario: One provider fails
- **WHEN** Crossref or Semantic Scholar fails
- **THEN** runtime records the provider outcome
- **AND** continues with the remaining applicable provider

#### Scenario: API resolution is unavailable
- **WHEN** there is no effective identifier or no provider resolves an entry
- **THEN** the unresolved entry follows the existing local reference core review path
- **AND** the final result does not report an API failure as its `error`

### Requirement: Reference Review SHALL Cover Only API-Unresolved Entries

Runtime SHALL externalize core and metadata evidence work only for entries not accepted through API resolution and SHALL merge reviewed entries with protected API-resolved items.

#### Scenario: API resolution is partial
- **WHEN** only a subset of prepared entries is accepted from providers
- **THEN** `reference_core_required_coverage_keys` contains exactly the unresolved local keys
- **AND** a valid core submit atomically merges reviewed items with API-resolved items in local order

#### Scenario: API resolution is complete
- **WHEN** every prepared entry is accepted from providers
- **THEN** runtime records reference persistence without requiring a core review payload
- **AND** skips metadata evidence review
- **AND** returns `next_action = "persist_citation_analysis"`

### Requirement: API Resolution Provenance SHALL Remain Internal

Runtime SHALL retain provider fetch and match provenance for audit without adding fields or files to the public output contract.

#### Scenario: Public references are rendered
- **WHEN** API-resolved and locally reviewed references are rendered
- **THEN** `references.json` preserves the existing public bibliographic shape and local order
- **AND** provider names, match scores, raw responses, and resolution decisions are absent from public items

## MODIFIED Requirements

### Requirement: Metadata Enrichment SHALL Be A Separate Reference Round

After unresolved core references are persisted, the runtime SHALL generate metadata evidence packages only for locally reviewed reference items and require a metadata evidence payload before moving to citation analysis. API-resolved items SHALL bypass this round.

#### Scenario: Core references persisted
- **WHEN** `persist_references` receives valid `reference_reviews[]` covering every unresolved key
- **THEN** it merges core items with API-resolved items
- **AND** returns `metadata_evidence_batch_paths` for locally reviewed items
- **AND** keeps `next_action` as `persist_references`

#### Scenario: Metadata reviews persisted
- **WHEN** `persist_references` receives valid `metadata_evidence_reviews[]` covering every metadata evidence package
- **THEN** it persists metadata enrichment
- **AND** returns `next_action = "persist_citation_analysis"`

#### Scenario: No locally reviewed items require metadata evidence
- **WHEN** all prepared entries were accepted through API resolution
- **THEN** runtime records metadata evidence preparation and persistence as skipped
- **AND** advances directly to citation analysis

### Requirement: Reference Metadata SHALL Be Reviewed From Local Evidence Only

The agent-facing reference metadata submit round SHALL be Reference Metadata Evidence Review, SHALL apply only to locally reviewed entries, and SHALL forbid external lookup.

#### Scenario: Metadata evidence batch
- **WHEN** unresolved core `reference_reviews[]` are persisted
- **THEN** stdout includes `metadata_evidence_review_manifest_path` and `metadata_evidence_batch_paths`
- **AND** batch JSON includes `external_lookup_allowed=false`, allowed evidence sources, and forbidden external lookup actions

#### Scenario: Metadata evidence submit
- **WHEN** the agent submits reference metadata
- **THEN** the payload uses `metadata_evidence_reviews[]`
- **AND** each status is `fields_extracted`, `existing_fields_confirmed`, or `no_local_evidence`

#### Scenario: Old payload rejected
- **WHEN** a payload contains `metadata_reviews[]`
- **THEN** runtime rejects it with a current-state repair hint

#### Scenario: External metadata blocked
- **WHEN** submitted DOI, URL, archiveID, ISBN, ISSN, pages, volume, or issue metadata lacks local batch evidence
- **THEN** runtime rejects it with `metadata_without_local_evidence`
