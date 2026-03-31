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

