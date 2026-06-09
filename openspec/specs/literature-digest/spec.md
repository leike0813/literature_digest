# literature-digest Specification

## Purpose
TBD - created by archiving change enhance-reference-rich-fields. Update Purpose after archive.
## Requirements
### Requirement: Keep Mandatory Reference Contract Unchanged

The skill MUST keep the existing required reference item fields unchanged.

Each reference item MUST still include:
- `author: string[]`
- `title: string`
- `year: number|null`
- `raw: string`
- `confidence: number`

#### Scenario: Preserve required-only compatibility
- **WHEN** the skill outputs references
- **THEN** every item still contains the original required fields above
- **AND** no previously required field is removed or downgraded.

### Requirement: Prioritize High-Value Optional Metadata Extraction

The skill SHALL aggressively extract high-value optional fields when supported by clear evidence in `raw` text.

Priority order for optional fields:
1. Venue/container information:
   - `publicationTitle`
   - conference/journal/school/container name (mapped to the most appropriate output field)
2. Bibliographic location:
   - `volume`
   - `issue`
   - `pages`
3. Identifiers and links:
   - `DOI`
   - `url`
   - `arxiv`
4. Publisher/institution details:
   - `publisher`
   - school/institution-like publisher info when present

#### Scenario: Evidence-present optional extraction
- **GIVEN** a reference `raw` string includes conference/journal name, volume/issue/pages, DOI or URL
- **WHEN** the skill parses the item
- **THEN** it SHOULD output those optional fields instead of returning only the minimum required fields.

### Requirement: No Minimal-Only Laziness When Evidence Exists

The skill MUST NOT intentionally stop at minimal required fields if high-value optional fields are directly extractable from `raw`.

#### Scenario: Avoid minimum-only output
- **GIVEN** `raw` contains explicit `In: <venue>`, `vol.`, `no.`, `pp.`, `doi`, or URL patterns
- **WHEN** parsing completes
- **THEN** corresponding optional fields SHOULD be populated
- **AND** output SHOULD NOT be limited to only required fields unless extraction is genuinely uncertain.

### Requirement: Optional Fields Stay Optional and Non-Hallucinatory

Optional fields remain non-mandatory. If evidence is absent or ambiguous, the skill MUST prefer omission over hallucination.

#### Scenario: Missing optional evidence
- **GIVEN** a reference entry lacks trustworthy venue/volume/issue/pages/identifier signals
- **WHEN** parsing the item
- **THEN** optional fields MAY be omitted
- **AND** `confidence` SHOULD reflect uncertainty without fabricating metadata.

### Requirement: Add Citation Analysis Artifact (Introduction Only)

The skill MUST produce an additional output artifact `citation_analysis.json` and return its path via `citation_analysis_path`.

#### Scenario: Stdout keys include citation analysis path
- **WHEN** the skill completes successfully
- **THEN** stdout JSON MUST include:
  - `digest_path`
  - `references_path`
  - `citation_analysis_path`
  - `provenance.generated_at`
  - `provenance.input_hash`
  - `warnings`
  - `error`

### Requirement: Artifact File Protocol

Artifacts MUST be written using fixed filenames:
- `digest.md`
- `references.json`
- `citation_analysis.json`

The default output directory remains the directory of `source_path`, but the final render step MAY override the output directory explicitly without changing filenames.

#### Scenario: Default render output directory
- **WHEN** the final render step runs without an explicit output-directory override
- **THEN** `digest.md`, `references.json`, and `citation_analysis.json` are written beside `source_path`

#### Scenario: Render output directory override
- **WHEN** the final render step runs with an explicit output-directory override
- **THEN** the runtime writes the fixed artifact filenames into that directory
- **AND** the final stdout payload reports those actual artifact paths

### Requirement: Source Input SHALL Be Normalized Before Analysis

The skill MUST accept a single `source_path` input and MUST determine the input type from file content rather than extension. Before any digest/reference/citation logic runs, the skill MUST normalize the input into `<cwd>/.literature_digest_tmp/source.md`.

#### Scenario: PDF signature input
- **WHEN** the input file bytes start with `%PDF-`
- **THEN** the skill treats the input as PDF even if the extension suggests otherwise
- **AND** it normalizes the content into `<cwd>/.literature_digest_tmp/source.md` before downstream analysis.

#### Scenario: UTF-8 text input
- **WHEN** the input file is valid UTF-8 text and does not start with `%PDF-`
- **THEN** the skill treats the input as markdown/plain-text source
- **AND** it copies the content into `<cwd>/.literature_digest_tmp/source.md` before downstream analysis.

### Requirement: Citation Analysis Scope = Introduction (Chapter 1)

Citation analysis MUST only consider in-text citations appearing within Chapter 1 Introduction (including its subsections).

#### Scenario: Introduction-only analysis
- **GIVEN** a paper markdown with `# 1 Introduction` and later sections
- **WHEN** generating `citation_analysis.json`
- **THEN** citations outside the Introduction scope MUST NOT appear in `items` or `unmapped_mentions`
- **AND** `meta.scope` MUST reflect the Introduction line range (1-based).

### Requirement: Support Numeric and Author-Year Citations

The skill MUST support both:
- numeric citations (e.g. `[5, 36]`, `[40–42]`)
- author-year citations (e.g. `(Smith, 2020)`, `Smith et al. (2020)`)

#### Scenario: Numeric citations mapping
- **GIVEN** Introduction contains `[5, 36]` or `[40–42]`
- **WHEN** generating `citation_analysis.json`
- **THEN** numeric citations SHOULD be mapped to `references.json` via `ref_index`
- **AND** ranges MUST be expanded consistently.

#### Scenario: Author-year citations high quality
- **GIVEN** Introduction contains author-year citations (including multi-cites separated by `;`)
- **WHEN** generating `citation_analysis.json`
- **THEN** the skill MUST parse author-year structures correctly
- **AND** MUST attempt reliable mapping using `year` + first-author surname against `references.json`
- **AND** MUST NOT hard-guess when ambiguous; ambiguous/unmatched citations MUST be recorded in `unmapped_mentions`.

### Requirement: `citation_analysis.json` Minimum Schema

`citation_analysis.json` MUST be a UTF-8 JSON object containing:
- `meta` with `language`, `scope`
- `items` (array)
- `unmapped_mentions` (array)
- `report_md` (string)

#### Scenario: Skill execution completed
- **WHEN** generating `citation_analysis.json`
- **THEN** `citation_analysis.json` MUST be a UTF-8 JSON object containing contents listed above

### Requirement: Citation Analysis SHALL Follow Explicit Multi-Stage Workflow
For citation analysis generation, the system MUST follow an explicit staged workflow defined in `literature-digest/SKILL.md`: preprocess extraction, mention mapping/accounting, semantic aggregation, and final gate checks.

#### Scenario: Workflow order is enforced
- **WHEN** generating `citation_analysis.json`
- **THEN** semantic aggregation is executed only after preprocess extraction is available
- **AND** final output is produced only after mention-accounting checks run.

### Requirement: Citation Scope Decision SHALL Be Agent-Owned and Single-Object
`citation_scope` MUST be decided by LLM/agent (not by deterministic preprocess scripts), and represented as a single scope-definition object that can cover one or multiple review chapters.

#### Scenario: Multi-section review coverage
- **WHEN** review discourse spans both `Introduction` and `Related Work(s)`
- **THEN** the chosen `citation_scope` covers both sections rather than only one
- **AND** downstream preprocess runs strictly inside this provided scope.

#### Scenario: Parent-section child coverage
- **WHEN** `citation_scope` selects a parent review section that has child subsections
- **THEN** the scope includes all child-subsection content until the next heading of same-or-higher level
- **AND** under-coverage is treated as invalid scope and triggers fallback handling.

### Requirement: Mention Accounting Gate
The system MUST account for every extracted mention by placing it either in mapped `items[].mentions` or in `unmapped_mentions`, and MUST NOT silently drop mentions.

#### Scenario: Full mention accounting
- **WHEN** preprocess extracts N citation mentions in `citation_scope`
- **THEN** the final citation-analysis structure contains exactly N consumed mention records across mapped and unmapped groups
- **AND** no extracted mention is omitted from both groups.

### Requirement: Semantic Tasks MUST Be Grounded on Preprocess Evidence
After preprocess, semantic tasks MUST use preprocess outputs and local snippets as primary evidence. Mapping decisions MUST prefer deterministic cues first and MUST fall back to `unmapped_mentions` when confidence is insufficient.

#### Scenario: Ambiguous author-year mapping
- **WHEN** an author-year mention has multiple plausible reference candidates
- **THEN** the system records the mention in `unmapped_mentions` with a reason code
- **AND** the system does not force a low-confidence hard mapping.

### Requirement: Fallback Behavior for Boundary Cases
`literature-digest/SKILL.md` MUST define deterministic fallback behavior for boundary cases including missing/invalid `citation_scope`, missing references, parse failures, and gate-check failures.

#### Scenario: References unavailable
- **WHEN** references cannot be loaded for mapping
- **THEN** citation mentions are still extracted from provided `citation_scope`
- **AND** mentions that cannot be mapped are emitted through `unmapped_mentions` rather than dropped.

#### Scenario: Gate check failure
- **WHEN** mention-accounting gate fails
- **THEN** the system returns a schema-compatible output with a populated `error`
- **AND** avoids returning a false-success citation-analysis result.

### Requirement: Guidance Refactors SHALL Preserve Detailed Content

When detailed guidance is moved out of `SKILL.md`, the skill repository MUST preserve that content in external docs instead of replacing it with summaries.

#### Scenario: Long-form guidance migrated
- **WHEN** `SKILL.md` is slimmed down
- **THEN** the removed detailed instructions, examples, and templates remain present elsewhere in the skill package
- **AND** the refactor does not discard their operational content.

### Requirement: SKILL Contract SHALL Be Concise But Indexed

`SKILL.md` MAY remain concise, but it MUST include an explicit index to the rich external guidance docs.

#### Scenario: Agent reads SKILL.md
- **WHEN** an agent starts from `SKILL.md`
- **THEN** it can locate the detailed stage/topic guidance through explicit links
- **AND** those links point to docs that contain the preserved full detail.

### Requirement: Gate Payload SHALL Include Execution Notes

The gate payload SHALL include a short `execution_note` for the current action.

#### Scenario: Main-path action is ready
- **WHEN** the gate returns a ready main-path `next_action`
- **THEN** the payload includes a non-empty `execution_note`
- **AND** that note summarizes the most important execution constraint for the current action

### Requirement: Final Render Guidance SHALL Be Scoped To Stage 6 Gate Output

The instruction to directly adopt the render script stdout JSON as the final assistant output SHALL be delivered through the stage-6 gate note rather than a broader global rule.

#### Scenario: Gate advances to final render
- **WHEN** the gate returns `next_action = render_and_validate`
- **THEN** `execution_note` tells the agent to run render mode next
- **AND** `execution_note` tells the agent to directly use the render script stdout JSON as the final assistant output

### Requirement: Stage 4 SHALL Support Author-Year Entry Split Review

When deterministic reference splitting still groups multiple author-year bibliography items into a single raw entry, the runtime MUST route stage 4 through a split-review action before final reference refinement.

#### Scenario: Grouped author-year entries trigger split review

- **GIVEN** the references scope contains author-year bibliography entries that remain grouped after deterministic preprocessing
- **WHEN** `prepare_references_workset` completes
- **THEN** the runtime reports grouped-entry suspicion
- **AND** gate advances to `persist_reference_entry_splits`
- **AND** the runtime does not proceed directly to `persist_references`

### Requirement: Split Review SHALL Preserve Raw Text Exactly

The split-review action MUST only adjust raw entry boundaries and MUST preserve the original references scope text exactly.

#### Scenario: Reviewed entry boundaries are accepted

- **GIVEN** `persist_reference_entry_splits` receives ordered `entries[*].raw`
- **WHEN** the concatenated reviewed raws match the original references scope text after whitespace normalization
- **THEN** the runtime rebuilds `reference_entries`, `reference_parse_candidates`, and `reference_batches`
- **AND** gate advances to `persist_references`

#### Scenario: Reviewed entry boundaries rewrite or drop text

- **GIVEN** `persist_reference_entry_splits` receives entries whose concatenated text does not match the original references scope text
- **WHEN** validation runs
- **THEN** the runtime fails with `reference_entry_splitting_failed`

### Requirement: Stage 5 Citation Analysis SHALL Be Script-Grounded

The skill SHALL treat stage 5 citation analysis as complete only when the scripted action chain has been executed in order.

#### Scenario: Gate blocks stage-5 progression without required receipts
- **WHEN** a stage-5 or stage-6 transition is attempted without the required prior stage-5 action receipts
- **THEN** gate blocks progression
- **AND** the missing prerequisite summary names the missing `action_receipts.*` entries

#### Scenario: Render blocks final publication without required receipts
- **WHEN** `render_and_validate --mode render` is called and any required stage-5 receipt is missing
- **THEN** render returns a schema-compatible error JSON
- **AND** it does not publish final public artifacts

### Requirement: Citation Stage SHALL Fail On Empty Review-Like Worksets

The skill SHALL not treat review-like or citation-shaped scopes with zero stable citation workset output as a normal completion state.

#### Scenario: Review-like scope yields zero stable mentions
- **WHEN** `prepare_citation_workset` processes a review-like or citation-shaped scope
- **AND** it produces zero stable mentions or zero citation workset items
- **THEN** the action fails with a citation-stage grounding error

### Requirement: Author-Year Mapping SHALL Support Multi-Token First Authors

The skill SHALL normalize first-author surname aliases so author-year mentions can match references whose first author contains multiple tokens.

#### Scenario: Multi-token first author maps successfully
- **WHEN** a mention uses a surname hint such as `zamir`
- **AND** the matching reference first author is structured as `Waqas Zamir, S.`
- **THEN** author-year matching resolves the mention to that reference item for the same year

### Requirement: Normal-path gate payloads use command examples instead of SQL examples

The literature-digest gate MUST return a `command_example` for non-repair actions and MUST NOT expose executable SQL examples on the normal main path.

#### Scenario: Main-path gate payload returns script command guidance

- **WHEN** `gate_runtime.py` returns a payload whose `next_action` is not a repair action
- **THEN** the payload includes a non-null `command_example`
- **AND** `command_example.command` shows the next `scripts/stage_runtime.py <next_action>` call
- **AND** `command_example.payload_example` is present only when that action expects a payload file
- **AND** `sql_examples` is an empty array

### Requirement: Repair gate payloads keep SQL examples

Repair guidance MUST continue to surface SQL examples through the existing gate field.

#### Scenario: Repair payload keeps SQL repair hints

- **WHEN** `gate_runtime.py` returns a payload whose `next_action` starts with `repair_`
- **THEN** the payload includes repair-oriented `sql_examples`
- **AND** `command_example` is `null`

### Requirement: Runtime Paths SHALL Be Confirmed Before Bootstrap

New runs MUST confirm runtime directories before bootstrap persists source inputs.

#### Scenario: Startup confirms shell cwd first
- **WHEN** a new run starts
- **THEN** the first runtime action is `confirm_runtime_paths`
- **AND** it persists `working_dir`, `tmp_dir`, `db_path`, `result_json_path`, and `output_dir`
- **AND** `bootstrap_runtime_db` runs only after that confirmation step.

### Requirement: Final Public Output Paths SHALL Be Absolute

The final stdout payload SHALL emit absolute artifact paths.

#### Scenario: Render succeeds
- **WHEN** `render_and_validate --mode render` completes successfully
- **THEN** `digest_path`, `references_path`, `citation_analysis_path`, and `citation_analysis_report_path` (when present) are absolute paths.

### Requirement: Runtime Markdown Templates SHALL Be Persisted Before Normalization

The skill SHALL persist run-specific digest and citation Markdown templates into the runtime tmp directory before source normalization proceeds.

#### Scenario: Bootstrap advances to runtime template persistence

- **WHEN** `bootstrap_runtime_db` succeeds
- **THEN** the next main-path action is `persist_render_templates`
- **AND** normalization does not proceed until runtime template paths are persisted

### Requirement: Render SHALL Use DB-Backed Runtime Templates

The final render step SHALL load digest and citation Markdown templates only from the runtime template paths persisted in SQLite for new runs.

#### Scenario: Runtime templates are present

- **WHEN** `render_and_validate --mode render` runs for a new workflow that completed `persist_render_templates`
- **THEN** digest Markdown is rendered from `runtime_inputs.digest_template_path`
- **AND** citation Markdown report is rendered from `runtime_inputs.citation_analysis_template_path`

### Requirement: Language Choice SHALL Prefer Prompt Inference Over Immediate zh-CN Default

The skill guidance SHALL state that missing explicit language input is resolved by prompt-language inference before any compatibility fallback to `zh-CN`.

#### Scenario: Prompt does not include explicit target language

- **WHEN** the agent starts a new run without an explicit language override
- **THEN** guidance instructs it to infer the target language from the prompt first
- **AND** only fall back to `zh-CN` if that inference is unstable

### Requirement: LaTeX Input Normalization

The skill SHALL accept a single `.tex` file or a LaTeX project directory as `source_path`.

#### Scenario: Single tex file

- **WHEN** `source_path` points to a readable `.tex` file
- **THEN** `normalize_source` produces fenced `tex` content in `source_documents.normalized_source`

#### Scenario: LaTeX project directory

- **WHEN** `source_path` points to a directory containing LaTeX sources
- **THEN** the runtime detects a main tex entry file, expands `\input` / `\include`, and stores fenced `tex` content in `source_documents.normalized_source`

### Requirement: Raw Bib Source Preservation

When bibliography sources are available as `.bib` files, the runtime SHALL append them to normalized source as fenced `bibtex` blocks.

#### Scenario: Linked bib files exist

- **WHEN** LaTeX input references `.bib` files through bibliography commands
- **THEN** each resolved `.bib` file is appended to normalized source with an explanatory note and a `bibtex` code fence

### Requirement: Deterministic LaTeX Reference Splitting

Stage 4 SHALL deterministically split `\bibitem` and `bibtex` bibliography sources before LLM refinement.

#### Scenario: Bibitem bibliography

- **WHEN** the references scope contains `\bibitem{...}`
- **THEN** `prepare_references_workset` splits entries on `\bibitem` boundaries

#### Scenario: Bibtex bibliography

- **WHEN** the references scope contains fenced bibtex entries
- **THEN** `prepare_references_workset` splits entries on top-level `@type{key,` boundaries and emits deterministic candidates from bib fields

### Requirement: LaTeX Citation Mapping

Stage 5 SHALL support LaTeX citation commands and prefer citekey mapping.

#### Scenario: Cite commands with keys

- **WHEN** normalized source contains `\cite{a,b}`-style markers
- **THEN** `prepare_citation_workset` extracts one mention per citekey and maps them to `reference_items` using citekey metadata when available

### Requirement: Reference Splitting SHALL Avoid Venue False Positives

Reference splitting SHALL NOT treat venue fragments or author initials as strong
reference starts without additional reference-entry evidence.

#### Scenario: Proceedings text inside one reference

- **GIVEN** a reference contains `In Proceedings ...`
- **WHEN** the references workset is prepared
- **THEN** that venue phrase does not by itself create a new reference entry.

#### Scenario: Inline numeric entries

- **GIVEN** one references line contains multiple numeric entries such as
  `[42] ... [43] ...`
- **WHEN** the references workset is prepared
- **THEN** the line is split into separate entries when both numeric markers are
  strong entry starts.

### Requirement: Split Review SHALL Support Stable False-Positive Resolution

Split review SHALL expose the current suspect generation and allow a reviewed
block to be force-kept when the agent confirms the suspicion is false.

#### Scenario: Force keep suspect block

- **GIVEN** `prepare_references_workset` reports a suspect block
- **WHEN** `persist_reference_entry_splits` receives `resolution = force_keep`
- **THEN** the block is accepted as a single reference entry
- **AND** the runtime does not re-enter split review for the same block.

### Requirement: Citation Function Contract SHALL Be Visible

Citation function values SHALL remain a fixed enum and the valid values SHALL
be visible in SKILL and stage guidance.

#### Scenario: Unsupported function value

- **WHEN** `persist_citation_semantics` receives an unsupported function value
- **THEN** the runtime normalizes it to `uncategorized`
- **AND** emits a warning that names the allowed function values.

### Requirement: Citation Timeline SHALL Remain Closed Over Dated Items

Citation timeline validation SHALL require every dated citation item to appear
in exactly one timeline bucket.

#### Scenario: Missing dated citation item

- **WHEN** a dated citation item is missing from `early`, `mid`, and `recent`
- **THEN** `persist_citation_timeline` rejects the payload with a clear missing
  `ref_index` message.

### Requirement: Digest Stage SHALL Persist Optional Representative Image Selection

The digest stage SHALL accept an optional `representative_image` object in addition to `digest_slots` and `section_summaries`.

#### Scenario: Selected Markdown image reference

- **GIVEN** Markdown input contains a real Markdown or HTML image reference in the source text
- **WHEN** `persist_digest` receives `representative_image.status = "selected"` with `source_kind = "markdown_image_ref"`
- **THEN** the runtime persists the representative-image metadata
- **AND** `markdown_src_hint` is preserved exactly as a source-text hint rather than rewritten to an absolute path.

#### Scenario: Selected LaTeX image path hint

- **GIVEN** LaTeX input normalization preserves a textual image path such as `\includegraphics{figures/overview}`
- **WHEN** that path is selected as the representative image location hint
- **THEN** the skill may reuse `source_kind = "markdown_image_ref"`
- **AND** `markdown_src_hint` preserves the original source path hint without extension completion, directory rewriting, or file existence checks.

#### Scenario: No reliable representative image

- **WHEN** `persist_digest` receives `representative_image.status = "none"`
- **THEN** the runtime persists only `{ "status": "none" }`.

#### Scenario: Old digest payload remains valid

- **WHEN** `persist_digest` receives the previous payload shape with only `digest_slots` and `section_summaries`
- **THEN** the payload remains valid
- **AND** no `representative_image` field is required in the final output.

### Requirement: Representative Image Output SHALL Be Optional And Additive

The final stdout JSON and mirrored `literature-digest.result.json` SHALL support an optional `representative_image` field without changing existing required fields.

#### Scenario: Representative image was selected

- **WHEN** final render completes after a selected representative image was persisted
- **THEN** the final JSON includes `representative_image.status = "selected"`
- **AND** includes the persisted label, caption quote, selection reason, confidence, and applicable source hints.

#### Scenario: No image was selected

- **WHEN** final render completes after `{ "status": "none" }` was persisted
- **THEN** the final JSON includes `representative_image.status = "none"`.

#### Scenario: PDF figure-caption metadata

- **WHEN** the source is PDF or PDF-derived text and a figure can only be identified by label, caption, and optional page metadata
- **THEN** the final JSON may use `source_kind = "pdf_figure_caption"`
- **AND** no PDF image file is exported or referenced as an artifact.

### Requirement: Representative Image Selection SHALL Be Evidence-Grounded

Representative-image selection SHALL rely only on textual evidence available in normalized source content, captions, nearby paragraphs, section hints, labels, and page hints.

When at least one candidate has a locatable textual image reference, figure label, caption, or LaTeX image path hint, the skill MUST evaluate those candidates instead of defaulting to `representative_image.status = "none"` merely because image pixels are unavailable.

#### Scenario: Prefer method or architecture figure

- **GIVEN** multiple figure candidates are visible in source text
- **WHEN** selecting a representative image
- **THEN** method, architecture, pipeline, model-structure, overall-experiment-design, or central-result figures are preferred over low-information figures.

#### Scenario: Avoid low-information figures

- **GIVEN** candidates are pure tables, formula-only figures, decorative images, or otherwise low-information images
- **WHEN** no better textual evidence exists
- **THEN** the skill returns `representative_image.status = "none"` rather than fabricating a representative image.

#### Scenario: Low confidence still selects best textual candidate

- **GIVEN** at least one candidate has a locatable figure label, caption, Markdown/HTML image reference, or LaTeX image path hint
- **AND** the candidate is not clearly low-information
- **WHEN** the evidence is sufficient to identify the candidate but not strong enough for high confidence
- **THEN** the skill selects the best candidate with `confidence = "medium"` or `confidence = "low"`
- **AND** does not return `representative_image.status = "none"` solely to avoid a low-confidence choice.

### Requirement: Successful Digest Output SHALL Include Literature Matching Metadata Sidecar

The main `literature-digest` skill SHALL publish a `literature_matching_metadata.json` artifact for successful runs and SHALL return its absolute path as `literature_matching_metadata_path` in stdout and `literature-digest.result.json`.

#### Scenario: Successful run publishes matching metadata path

- **WHEN** a `literature-digest` run completes successfully
- **THEN** stdout includes `literature_matching_metadata_path`
- **AND** the path points to `literature_matching_metadata.json` in the configured output directory
- **AND** `literature-digest.result.json` contains the same path.

#### Scenario: Schema-compatible failure keeps required path field

- **WHEN** a run fails before final render
- **THEN** stdout still includes `literature_matching_metadata_path`
- **AND** its value is an empty string.

### Requirement: Matching Metadata SHALL Use Fixed V1 Shape

The `literature_matching_metadata.json` artifact SHALL contain exactly the v1 matching metadata shape with no generated `bm25_text`.

#### Scenario: Rendered sidecar shape

- **WHEN** `literature_matching_metadata.json` is rendered
- **THEN** it contains `schema = "literature_matching_metadata.v1"`
- **AND** it contains `key_terms`, `methods`, `problems`, `datasets`, and `exclude_terms` arrays
- **AND** it does not contain `bm25_text`.

### Requirement: Matching Metadata SHALL Be Authored During Outline And Scope Stage

Stage 02 SHALL collect matching metadata together with outline and scope decisions.

#### Scenario: Stage 02 payload includes matching metadata

- **WHEN** `persist_outline_and_scopes` is called on the main path
- **THEN** the payload must include `literature_matching_metadata`
- **AND** the runtime persists it before advancing to Stage 03.

### Requirement: Stage 4 Reference Quality Gate

`literature-digest` SHALL classify finalized Stage 4 reference rows before citation workset preparation.

#### Scenario: Hard reference quality issue blocks persistence

- **WHEN** `persist_references` receives any row whose title is empty, a bare identifier or URL, publication metadata only, author-only text, or has no usable title tokens
- **THEN** the runtime SHALL NOT write `reference_items`
- **AND** the workflow SHALL remain at `stage_4_references / persist_references`
- **AND** the gate SHALL return `quality_directives` naming each affected `entry_index`/`ref_index`, stable reason code, evidence fields, and repair recommendation.

#### Scenario: Soft reference quality warning requires explicit review

- **WHEN** `persist_references` receives rows with only soft quality warnings
- **THEN** the runtime SHALL write `reference_items`
- **AND** affected rows SHALL include compatible `metadata.title_quality.status = "warning"` and `flags`
- **AND** the workflow SHALL advance to `stage_4_references / review_reference_quality`
- **AND** the gate SHALL instruct the agent to correct or explicitly accept every warning.

#### Scenario: References artifact remains a bare array

- **WHEN** final artifacts are rendered
- **THEN** `references.json` SHALL remain a JSON array of native reference objects
- **AND** quality metadata SHALL NOT introduce a top-level wrapper.

### Requirement: Preserve Reference Title Language In Quality Gate

`literature-digest` SHALL accept valid reference titles written in CJK or other non-Latin scripts without requiring translation to English.

#### Scenario: Chinese title passes Stage 4 quality gate

- **WHEN** `persist_references` receives a row whose `title` is `基于深度学习的文本分类方法`
- **THEN** the quality classifier SHALL treat the title as having usable title tokens
- **AND** it SHALL NOT emit `no_usable_title_tokens`
- **AND** Stage 4 SHALL be allowed to proceed when no other quality issue exists.

#### Scenario: Quality repair preserves original title script

- **WHEN** the gate returns Stage 4 quality directives
- **THEN** the instructions SHALL tell the agent to recover the cited title in the raw reference's original language/script
- **AND** SHALL NOT imply that translation, Anglicization, or romanization is an acceptable fix.

#### Scenario: Non-title values still fail

- **WHEN** a title is empty, a bare identifier or URL, author-only, publication metadata only, pure numeric, or pure punctuation
- **THEN** the corresponding existing hard quality reason SHALL still block the row.

### Requirement: Stage 4 SHALL Use Deterministic Reference Preprocess v1.7.1

The main `literature-digest` skill SHALL prepare Stage 4 reference entries and parse candidates using the deterministic line-first v1.7.1 behavior, including CJK/fullwidth handling, author-initial protection, IEEE quoted-title parsing, venue-marker parsing, non-reference line filtering, trailing page-marker cleanup, bilingual entry merge, and file-level quality detection.

#### Scenario: CJK reference produces structured candidates

- **WHEN** a references scope contains CJK/fullwidth bibliography lines with type markers
- **THEN** `prepare_references_workset` emits parse candidates that preserve original raw text and include title/year candidates when deterministically recoverable.

#### Scenario: File quality signal is persisted

- **WHEN** `prepare_references_workset` completes
- **THEN** the runtime persists v1.7.1 file-level quality metrics
- **AND** the workset export includes `file_quality` and `file_quality_low`.

### Requirement: Low-Quality Reference Files MAY Be Explicitly Abandoned

When deterministic preprocessing reports file-level reference quality as low, the skill SHALL let the agent explicitly continue reference extraction or abandon it. Abandonment SHALL be allowed only through a gate-directed action and SHALL be auditable in DB state.

#### Scenario: Low-quality file routes to extraction decision

- **GIVEN** deterministic preprocessing produced `file_quality_low = true`
- **WHEN** Stage 4 gate is evaluated
- **THEN** the next action is `decide_reference_extraction`
- **AND** the gate instructions explain both the continue and abandon choices.

#### Scenario: Abandoned references render as an empty array

- **GIVEN** the agent explicitly abandoned reference extraction through the guarded action
- **WHEN** final artifacts are rendered
- **THEN** `references.json` is a bare empty array
- **AND** `citation_analysis.json.meta.reference_extraction.status = "abandoned"`.

### Requirement: Reference-Free Citation Analysis SHALL Skip Ref-Index Mapping Checks Only After Verified Abandonment

Citation analysis SHALL skip `ref_index` mapping requirements only when reference extraction was explicitly abandoned after DB-backed low-quality preprocessing.

#### Scenario: Reference-free citation analysis succeeds

- **GIVEN** reference extraction was abandoned after deterministic low-quality detection
- **WHEN** Stage 5 citation analysis runs
- **THEN** citation mentions are still extracted
- **AND** unresolved mentions are retained with a stable abandon reason
- **AND** semantic items, timeline ref indexes, and summary key refs may be empty.

#### Scenario: Normal citation analysis remains strict

- **GIVEN** reference extraction was not abandoned
- **WHEN** Stage 5 payloads omit required `ref_index` mappings
- **THEN** the runtime rejects them as before.

