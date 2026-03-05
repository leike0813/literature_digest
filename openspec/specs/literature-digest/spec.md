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

