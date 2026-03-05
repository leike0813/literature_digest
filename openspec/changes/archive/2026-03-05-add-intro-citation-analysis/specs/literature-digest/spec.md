## ADDED Requirements

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

Artifacts MUST be written to the directory of `md_path` using fixed filenames:
- `digest.md`
- `references.json`
- `citation_analysis.json`

#### Scenario: Avoid stdout truncation
- **GIVEN** large outputs (digest and analysis)
- **WHEN** producing stdout
- **THEN** stdout MUST remain a single JSON object containing only file paths and audit fields.

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