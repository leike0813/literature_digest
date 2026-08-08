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

### Requirement: Guidance SHALL Not Describe Metadata Discovery

Skill guidance SHALL describe the round as local evidence review and SHALL explicitly prohibit web search and external bibliographic databases.

#### Scenario: Subagent prompt
- **WHEN** the metadata evidence subagent prompt is generated or documented
- **THEN** it states `This is not a metadata discovery task`
- **AND** it forbids web search, Crossref, arXiv, Google Scholar, Zotero, Semantic Scholar, DOI resolver, and external databases.

### Requirement: Citation analysis persists best-effort artifacts

The `literature-analysis` runtime SHALL complete the citation analysis stage and render final artifacts after citation workset preparation has run, even when the prepared workset contains no stable mapped citation items. Empty citation semantics, timeline summaries, and global summary SHALL be valid persisted results.

#### Scenario: Empty prepared workset completes final render
- **WHEN** citation workset preparation succeeds with zero citation packages and the agent submits an empty citation payload
- **THEN** the runtime SHALL persist empty citation semantics, timeline, and summary records and SHALL render final artifacts with an empty citation item list

#### Scenario: Missing preparation still fails
- **WHEN** the agent submits citation semantics before citation workset preparation has completed
- **THEN** the runtime SHALL fail and require citation workset preparation

#### Scenario: Unknown submitted references still fail
- **WHEN** a citation semantics payload contains a ref index or citation work key outside the prepared workset
- **THEN** the runtime SHALL reject the payload rather than inventing a mapping

#### Scenario: Empty prepared workset export succeeds
- **WHEN** citation workset preparation completed with empty mentions and items
- **THEN** exporting the citation workset SHALL return empty arrays instead of reporting the workset as missing

### Requirement: Citation workset preparation maps source citation mentions to references

The `literature-analysis` runtime SHALL prepare citation worksets by mapping source citation mentions to persisted references using deterministic local evidence. It SHALL support LaTeX citekeys, source-local bracket-alpha labels, numeric reference numbers, and author-year hints without requiring additional agent-submitted citation semantic fields.

#### Scenario: Alpha labels map to reference entries
- **WHEN** the source body contains `[RNSS18, DCLT18, YDY+19]` and the reference list contains matching bracket-alpha entries
- **THEN** citation workset preparation SHALL create mapped workset items for the matching references with `citation-label` mentions

#### Scenario: Original alpha label is preserved for rendering
- **WHEN** a citation item is mapped through a bracket-alpha label such as `[DCLT18]`
- **THEN** the rendered citation label SHALL use `[DCLT18]` rather than a generated author-year fallback

#### Scenario: Unknown alpha labels are not guessed
- **WHEN** the source body contains a bracket-alpha label that has no matching persisted reference alias
- **THEN** citation workset preparation SHALL NOT create a workset item for that label
#### Scenario: Duplicate alpha labels are ambiguous

- **WHEN** more than one persisted reference exposes the same normalized bracket-alpha label
- **THEN** mentions using that label SHALL remain unmapped and the runtime SHALL record a warning

### Requirement: Digest Depth SHALL Adapt To Source Length And Information Density

The `literature-analysis` agent SHALL choose digest depth from the normalized source's substantive length and information density. Numeric item ranges SHALL be treated as soft writing guidance rather than validation limits, and the runtime SHALL preserve the existing structured payload and coverage validation behavior.

#### Scenario: Ordinary paper uses the normal depth

- **WHEN** the normalized source is an ordinary journal or conference paper with a conventional number of substantive sections and findings
- **THEN** the agent produces a digest near the documented reference ranges
- **AND** it does not expand the digest merely to consume an available range

#### Scenario: Long information-dense source expands

- **WHEN** the normalized source contains substantially more grounded methods, experiments, results, limitations, chapters, or independent subtopics
- **THEN** the agent expands the relevant digest slot items and section summaries to preserve those distinctions
- **AND** it may exceed the documented soft reference ranges without causing a validation error or warning solely because of item count

#### Scenario: Long but sparse source does not inflate mechanically

- **WHEN** a source is long because of layout, appendices, repeated material, or other low-density content
- **THEN** the agent bases digest depth on substantive evidence rather than page, character, or line thresholds
- **AND** it avoids padding, synonymous bullets, repeated claims, and unsupported detail

### Requirement: Literature Analysis SHALL Include A Scoring Stage

The normal `literature-analysis` workflow SHALL route from digest persistence to literature scoring before reference extraction and SHALL include the score artifact in final output.

#### Scenario: Digest completes in normal mode

- **WHEN** `persist_digest` succeeds with `score_only=false`
- **THEN** the next agent-facing action is `persist_literature_score`.

#### Scenario: Scoring completes in normal mode

- **WHEN** `persist_literature_score` accepts a valid payload
- **THEN** the next agent-facing action is `persist_references`
- **AND** the eventual full stdout contains a non-empty absolute `literature_score_path`.

### Requirement: Literature Analysis SHALL Support Score-Only Runs

The Skill SHALL accept a boolean `score_only` parameter with default `false` and SHALL persist the selected mode at initialization.

#### Scenario: Score-only run initializes

- **WHEN** `init_runtime` receives `score_only=true`
- **THEN** source normalization still completes
- **AND** the next agent-facing action is `persist_literature_score`
- **AND** analysis planning and digest generation are skipped.

#### Scenario: Score-only run succeeds

- **WHEN** scoring succeeds in a score-only run
- **THEN** `literature_score_path` is a non-empty absolute path
- **AND** `digest_path`, `references_path`, `citation_analysis_path`, and `literature_matching_metadata_path` are empty strings
- **AND** `citation_analysis_report_path` is absent.

#### Scenario: Disallowed score-only action is invoked

- **WHEN** a score-only run invokes analysis plan, digest, references, or citation analysis
- **THEN** the runtime returns `mode_action_not_allowed`
- **AND** keeps `next_action = "persist_literature_score"` until scoring succeeds.

### Requirement: Skill Guidance SHALL Preserve Existing Instructions

The scoring change SHALL add only the main-path instructions required to execute scoring and SHALL route detailed scoring semantics, examples, and techniques to a dedicated reference document.

#### Scenario: Agent reads SKILL.md

- **WHEN** the updated Skill is loaded
- **THEN** it contains the scoring input/output contract, command, stage order, hard constraints, and failure routing needed to execute the current workflow
- **AND** existing instructions unrelated to the new workflow remain unchanged.

#### Scenario: Agent enters scoring

- **WHEN** scoring is the current action
- **THEN** the Skill directs the agent to the dedicated scoring reference and runtime-generated scoring context for detailed guidance.

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

