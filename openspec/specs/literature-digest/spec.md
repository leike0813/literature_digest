# literature-digest Specification

## Purpose

Define the digest-only `literature-digest` skill contract for source normalization, LLM-authored structured summaries, template rendering, and stable Markdown/JSON outputs.

## Requirements
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