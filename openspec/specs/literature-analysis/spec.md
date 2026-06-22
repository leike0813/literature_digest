## Purpose

Define the literature-analysis skill's reference review, metadata enrichment, citation analysis, and output rendering contracts, including split-review validation, subagent delegation, and public artifact structure.
## Requirements
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

### Requirement: Split Review Conservation SHALL Use Token Coverage

The runtime SHALL validate split review text preservation using token coverage instead of exact normalized string equality.

#### Scenario: Harmless text-shape differences
- **WHEN** `split_reviews[].corrected_reference_texts` preserve the source block's core tokens
- **AND** only differ by whitespace, line breaks, Unicode normalization, fullwidth/halfwidth punctuation, quote style, dash style, or punctuation style
- **THEN** split review validation succeeds.

#### Scenario: Missing protected evidence
- **WHEN** corrected split texts drop a URL, DOI, arXiv identifier, year, author token, or title keyword from the suspect block
- **THEN** split review validation fails with `reference_entry_splitting_failed`
- **AND** the error includes token conservation diagnostics.

### Requirement: Post-Review Boundary Suspicion SHALL Be Warning-Only

After token conservation succeeds, remaining deterministic boundary suspicion SHALL NOT hard-block reference persistence by itself.

#### Scenario: Heuristic suspicion remains after reviewed split
- **WHEN** split review passes token conservation
- **AND** a subsequent reference preprocess still reports suspect blocks
- **THEN** runtime continues and returns regenerated reference review packages
- **AND** records `reference_boundary_suspicion_after_review` warnings.

### Requirement: Web Resource References SHALL Be Allowed Without Year

References that are web resources, software repositories, project pages, or URLs SHALL be allowed to proceed without a publication year.

#### Scenario: No-year URL reference
- **WHEN** a reviewed reference entry contains a URL or resource link but no publication year
- **THEN** reference persistence may proceed with `publication_year=null`
- **AND** later timeline/citation stages may warn about missing year without requiring invented metadata.

### Requirement: Skill SHALL Define Global Subagent Delegation Contract

`literature-analysis` SHALL document subagent delegation as a global execution contract for batchable review work.

#### Scenario: Batchable work and subagents are available
- **WHEN** runtime returns `batch_work_packages`
- **AND** the execution environment supports subagents
- **AND** the work is reference core review, metadata enrichment, or citation semantic review
- **THEN** the main agent defaults to delegating batches to subagents.

#### Scenario: Delegation is skipped
- **WHEN** the main agent does not delegate batchable work
- **THEN** the reason is retained in execution notes or review notes.

### Requirement: Main Agent SHALL Remain Single Writer

Subagents SHALL only produce draft JSON for their assigned batch.

#### Scenario: Subagent batch work
- **WHEN** a subagent reviews a batch
- **THEN** it returns only the documented draft array for that batch
- **AND** it does not write DB, run runtime commands, submit payloads, modify stable keys, fill internal audit fields, or generate final artifacts.

### Requirement: Runtime JIT SHALL Reinforce Delegation Contract

Runtime prepare/status payloads SHALL include delegation policy and merge contract guidance that matches the global contract.

#### Scenario: Reference or citation prepare output
- **WHEN** prepare returns batch work packages
- **THEN** the payload includes `subagent_policy`, `batch_work_packages[].subagent_prompt`, and `merge_contract.single_writer = "main_agent"`.

#### Scenario: Status guidance
- **WHEN** `status` returns field guidance for a batchable stage
- **THEN** `field_guidance.subagents` states the default-to-delegate policy and main-agent single-writer rule.

### Requirement: Skill SHALL Prohibit Temporary Scripts For Semantic Review

The skill SHALL explicitly prohibit using ad hoc scripts to replace LLM judgment for digest writing, reference core review, metadata enrichment, and citation semantic analysis.

#### Scenario: Helper script is allowed
- **WHEN** a script only serializes already-reviewed decisions, checks JSON syntax, counts stable keys, or invokes `run_analysis.py`
- **THEN** it is allowed as deterministic support.

#### Scenario: Temporary script replaces semantic work
- **WHEN** a script infers reference authors, titles, years, metadata, citation topics, citation usage, summaries, or representative image judgment
- **THEN** the skill guidance marks that as forbidden.

### Requirement: Delegatable Tasks SHALL Have Named Delegation Points

The skill SHALL name the exact task points where subagents should be used by default.

#### Scenario: Reference prepare returns core review batches
- **WHEN** `persist_references` prepare returns `batch_work_packages`
- **THEN** the main agent uses the Reference Core Review delegation prompt unless delegation is unavailable or unsuitable.

#### Scenario: Core references return metadata batches
- **WHEN** core `reference_reviews[]` submit returns `metadata_review_packages` and metadata `batch_work_packages`
- **THEN** the main agent uses the Metadata Enrichment delegation prompt unless delegation is unavailable or unsuitable.

#### Scenario: Citation prepare returns semantic batches
- **WHEN** `persist_citation_analysis` prepare returns citation `batch_work_packages`
- **THEN** the main agent uses the Citation Semantic Review delegation prompt unless delegation is unavailable or unsuitable.

### Requirement: Prepare Output SHALL Externalize Large Work Packages

Reference and citation prepare responses SHALL return paths and counts instead of inlining large work package arrays.

#### Scenario: Reference core prepare
- **WHEN** `persist_references` prepare succeeds
- **THEN** stdout includes `reference_core_review_manifest_path`, `reference_core_batch_paths`, counts, and small guidance fields
- **AND** stdout does not include `reference_review_packages` or `batch_work_packages`.

#### Scenario: Metadata prepare after core submit
- **WHEN** core `reference_reviews[]` submit succeeds
- **THEN** stdout includes `metadata_review_manifest_path`, `metadata_batch_paths`, counts, and small guidance fields
- **AND** stdout does not include `metadata_review_packages` or `batch_work_packages`.

#### Scenario: Citation prepare
- **WHEN** `persist_citation_analysis` prepare succeeds
- **THEN** stdout includes `citation_semantic_review_manifest_path`, `citation_batch_paths`, counts, and small guidance fields
- **AND** stdout does not include `citation_work_packages` or `batch_work_packages`.

### Requirement: Runtime SHALL Precut Subagent Batch Files

Runtime SHALL write subagent batch files with at most 10 work items per batch.

#### Scenario: Batch file content
- **WHEN** a batch file is written
- **THEN** it includes `batch_id`, `batch_kind`, `input_package_path`, stable keys, package subset, allowed enum subset, required return shape, forbidden fields, subagent prompt, merge notes, and `suggested_draft_output_path`.

### Requirement: Guidance SHALL Use Path-Based Delegation

The skill guidance SHALL instruct the main agent to pass batch JSON file paths to subagents and SHALL prohibit manual splitting of full worksets.

#### Scenario: Subagent delegation
- **WHEN** runtime returns batch paths
- **THEN** the main agent delegates those paths directly
- **AND** the subagent reads only its assigned batch JSON file.

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

