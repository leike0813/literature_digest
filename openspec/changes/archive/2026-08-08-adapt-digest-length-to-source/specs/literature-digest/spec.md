## ADDED Requirements

### Requirement: Digest-Only Input And Output Contract

`literature-digest` SHALL read `source_path` and `language` from the prompt payload, SHALL use `source_path` as its only content source, and SHALL emit exactly one stdout JSON object with `digest_path`, provenance, warnings, and error fields.

#### Scenario: Digest succeeds

- **WHEN** a supported source is normalized and a valid structured digest payload is rendered
- **THEN** the skill writes `digest.md` beside `source_path`
- **AND** stdout contains an absolute `digest_path`, `provenance.generated_at`, `provenance.input_hash`, `warnings`, and `error = null`

#### Scenario: Digest fails

- **WHEN** the source cannot be read or normalized, the payload is invalid, or rendering fails
- **THEN** stdout retains the stable result shape with an empty `digest_path` and a structured `error`

### Requirement: Supported Sources SHALL Be Normalized Before Digest Generation

The skill SHALL detect and normalize Markdown, UTF-8 plain text, PDF, a single LaTeX file, and a LaTeX project directory before the LLM writes digest content.

#### Scenario: Supported source is provided

- **WHEN** `source_path` points to any supported source form
- **THEN** normalize mode returns normalized text, an input hash, source metadata, warnings, and error state for downstream digest generation

### Requirement: Digest Content SHALL Use A Fixed Structured Payload

The LLM SHALL submit `digest_slots` containing `tldr`, `research_question_and_contributions`, `method_highlights`, `key_results`, and `limitations_and_reproducibility`, plus outline-ordered `section_summaries` entries containing `source_heading` and `items`.

#### Scenario: Structured digest is generated

- **WHEN** the LLM finishes reading the normalized source
- **THEN** it supplies all five semantic slots and ordered section summaries
- **AND** it does not submit pre-rendered Markdown sections in place of the structured payload

### Requirement: Rendered Digest SHALL Use Fixed Section Structure

The final digest SHALL use the fixed section order for the selected language and SHALL NOT add a top-level title or paper metadata block.

#### Scenario: Chinese digest is rendered

- **WHEN** `language` starts with `zh`
- **THEN** the final headings are `## TL;DR`, `## 研究问题与贡献`, `## 方法要点`, `## 关键结果`, `## 局限与可复现性线索`, and `## 分章节总结` in that order

#### Scenario: English digest is rendered

- **WHEN** `language` starts with `en`
- **THEN** the final headings are `## TL;DR`, `## Research Question & Contributions`, `## Method Highlights`, `## Key Results`, `## Limitations & Reproducibility`, and `## Section-by-Section Summary` in that order

### Requirement: Other Languages SHALL Use Agent-Translated Runtime Templates

For a language that starts with neither `en` nor `zh`, the agent SHALL translate only the fixed heading text of the repository template and SHALL preserve all Jinja syntax, variables, comments, and loop structure.

#### Scenario: Another language is requested

- **WHEN** the selected language starts with neither `en` nor `zh`
- **THEN** the agent prepares a translated runtime template without changing template behavior or payload field names

### Requirement: LLM And Script Responsibilities SHALL Remain Separate

The LLM SHALL own semantic digest writing and non-English/non-Chinese heading translation. Scripts SHALL own source normalization, payload-shape validation, template rendering, file output, provenance, and stdout JSON stability.

#### Scenario: Digest workflow executes

- **WHEN** the skill produces a digest
- **THEN** no script performs summarization, outline interpretation, semantic classification, or an external LLM API call
- **AND** the LLM does not bypass the renderer by writing the final artifact directly

### Requirement: Digest Depth SHALL Adapt To Source Length And Information Density

The LLM SHALL choose digest depth from the source's substantive length and information density. Documented item counts SHALL be soft reference ranges, not payload limits or validation thresholds.

#### Scenario: Ordinary paper uses the normal depth

- **WHEN** the source is an ordinary journal or conference paper with conventional content breadth
- **THEN** the digest stays near the documented reference ranges without unnecessary expansion

#### Scenario: Long information-dense source expands

- **WHEN** the source contains substantially more grounded methods, experiments, results, limitations, chapters, or independent subtopics
- **THEN** the LLM expands the relevant slot items and section summaries
- **AND** it may exceed the soft reference ranges without failing or warning solely because of item count

#### Scenario: Long but sparse source does not inflate mechanically

- **WHEN** source length comes mainly from layout, appendices, repetition, or other low-density content
- **THEN** the LLM does not use a page, character, or line threshold to force expansion
- **AND** it avoids padding, synonymous bullets, repeated claims, and unsupported details

### Requirement: Section Summaries SHALL Track Substantive Source Structure

Section summaries SHALL follow reliable source headings in order, split long multi-theme chapters into meaningful subtopics, and use segment labels only when headings cannot be recovered reliably.

#### Scenario: Reliable outline exists

- **WHEN** the source has reliable chapter or section headings
- **THEN** section summaries cover the substantive non-reference structure in order
- **AND** long or information-dense sections receive additional entries or items as needed

#### Scenario: Reliable outline is unavailable

- **WHEN** the source outline cannot be recovered reliably
- **THEN** the LLM uses ordered segment labels and chooses enough segments to preserve substantive coverage

## REMOVED Requirements

### Requirement: Keep Mandatory Reference Contract Unchanged

**Reason**: This requirement describes the archived full-analysis skill rather than the current digest-only skill.
**Migration**: Use the `literature-analysis` capability for references and citation analysis.

### Requirement: Prioritize High-Value Optional Metadata Extraction

**Reason**: Reference metadata extraction is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: No Minimal-Only Laziness When Evidence Exists

**Reason**: Reference metadata extraction is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Optional Fields Stay Optional and Non-Hallucinatory

**Reason**: Reference metadata extraction is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Add Citation Analysis Artifact (Introduction Only)

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Artifact File Protocol

**Reason**: This artifact protocol belongs to the archived full-analysis implementation.
**Migration**: Use the new digest-only output contract in this capability and `literature-analysis` for multi-artifact analysis.

### Requirement: Source Input SHALL Be Normalized Before Analysis

**Reason**: The archived requirement couples normalization to the full-analysis workflow.
**Migration**: Use `Supported Sources SHALL Be Normalized Before Digest Generation` in this capability.

### Requirement: Citation Analysis Scope = Introduction (Chapter 1)

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Support Numeric and Author-Year Citations

**Reason**: Citation processing is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: `citation_analysis.json` Minimum Schema

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Citation Analysis SHALL Follow Explicit Multi-Stage Workflow

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Citation Scope Decision SHALL Be Agent-Owned and Single-Object

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Mention Accounting Gate

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Semantic Tasks MUST Be Grounded on Preprocess Evidence

**Reason**: This requirement belongs to the archived citation workflow.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Fallback Behavior for Boundary Cases

**Reason**: This requirement belongs to the archived full-analysis workflow.
**Migration**: Use the current digest-only failure contract or the `literature-analysis` capability as appropriate.

### Requirement: Guidance Refactors SHALL Preserve Detailed Content

**Reason**: This requirement governs archived full-analysis guidance.
**Migration**: Use the current active skill contracts.

### Requirement: SKILL Contract SHALL Be Concise But Indexed

**Reason**: This requirement governs archived full-analysis guidance.
**Migration**: Use the current active skill contracts.

### Requirement: Gate Payload SHALL Include Execution Notes

**Reason**: The current digest-only skill has no gate runtime.
**Migration**: Use the `literature-analysis` runtime where staged persistence is required.

### Requirement: Final Render Guidance SHALL Be Scoped To Stage 6 Gate Output

**Reason**: The current digest-only skill has no Stage 6 gate.
**Migration**: Use the digest-only renderer contract in this capability.

### Requirement: Stage 4 SHALL Support Author-Year Entry Split Review

**Reason**: Reference review is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Split Review SHALL Preserve Raw Text Exactly

**Reason**: Reference review is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Stage 5 Citation Analysis SHALL Be Script-Grounded

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Citation Stage SHALL Fail On Empty Review-Like Worksets

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Author-Year Mapping SHALL Support Multi-Token First Authors

**Reason**: Citation mapping is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Normal-path gate payloads use command examples instead of SQL examples

**Reason**: The current digest-only skill has no gate runtime.
**Migration**: Use the `literature-analysis` runtime where staged persistence is required.

### Requirement: Repair gate payloads keep SQL examples

**Reason**: The current digest-only skill has no gate runtime.
**Migration**: Use the `literature-analysis` runtime where repair is required.

### Requirement: Runtime Paths SHALL Be Confirmed Before Bootstrap

**Reason**: This path-bootstrap contract belongs to the archived full-analysis runtime.
**Migration**: Use the `literature-analysis` runtime or the digest-only CLI contract as appropriate.

### Requirement: Final Public Output Paths SHALL Be Absolute

**Reason**: This multi-artifact requirement belongs to the archived full-analysis runtime.
**Migration**: Use the digest-only output contract in this capability and `literature-analysis` for multi-artifact analysis.

### Requirement: Runtime Markdown Templates SHALL Be Persisted Before Normalization

**Reason**: Template persistence belongs to the archived SQLite runtime.
**Migration**: Use the digest-only runtime-template behavior in this capability.

### Requirement: Render SHALL Use DB-Backed Runtime Templates

**Reason**: The current digest-only skill has no runtime database.
**Migration**: Use the digest-only renderer contract in this capability.

### Requirement: Language Choice SHALL Prefer Prompt Inference Over Immediate zh-CN Default

**Reason**: The requirement is replaced by the consolidated digest-only input contract.
**Migration**: Use `Digest-Only Input And Output Contract` in this capability.

### Requirement: LaTeX Input Normalization

**Reason**: The requirement is replaced by the consolidated supported-source contract.
**Migration**: Use `Supported Sources SHALL Be Normalized Before Digest Generation` in this capability.

### Requirement: Raw Bib Source Preservation

**Reason**: Bibliography analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Deterministic LaTeX Reference Splitting

**Reason**: Reference splitting is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: LaTeX Citation Mapping

**Reason**: Citation mapping is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Reference Splitting SHALL Avoid Venue False Positives

**Reason**: Reference splitting is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Split Review SHALL Support Stable False-Positive Resolution

**Reason**: Reference split review is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Citation Function Contract SHALL Be Visible

**Reason**: Citation semantics are outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Citation Timeline SHALL Remain Closed Over Dated Items

**Reason**: Citation timeline analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Digest Stage SHALL Persist Optional Representative Image Selection

**Reason**: Representative-image persistence belongs to the archived full-analysis runtime and is not part of the current digest-only payload.
**Migration**: Use the `literature-analysis` capability when representative-image selection is required.

### Requirement: Representative Image Output SHALL Be Optional And Additive

**Reason**: Representative-image output is not part of the current digest-only stdout contract.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Representative Image Selection SHALL Be Evidence-Grounded

**Reason**: Representative-image selection is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Successful Digest Output SHALL Include Literature Matching Metadata Sidecar

**Reason**: Matching metadata is outside the current digest-only output contract.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Matching Metadata SHALL Use Fixed V1 Shape

**Reason**: Matching metadata is outside the current digest-only output contract.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Matching Metadata SHALL Be Authored During Outline And Scope Stage

**Reason**: The current digest-only skill has no outline-and-scope persistence stage.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Stage 4 Reference Quality Gate

**Reason**: Reference quality review is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Preserve Reference Title Language In Quality Gate

**Reason**: Reference quality review is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Stage 4 SHALL Use Deterministic Reference Preprocess v1.7.1

**Reason**: Reference preprocessing is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Low-Quality Reference Files MAY Be Explicitly Abandoned

**Reason**: Reference processing is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Reference-Free Citation Analysis SHALL Skip Ref-Index Mapping Checks Only After Verified Abandonment

**Reason**: Citation analysis is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Reject Placeholder Reference Titles

**Reason**: Reference processing is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Preserve Optional Reference Metadata

**Reason**: Reference metadata processing is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Missing Rich Metadata Evidence Emits Soft Warning

**Reason**: Reference metadata processing is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Reference Metadata Enrichment Stage

**Reason**: Reference metadata enrichment is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.

### Requirement: Reference Quality Review

**Reason**: Reference quality review is outside the current digest-only skill.
**Migration**: Use the `literature-analysis` capability.
