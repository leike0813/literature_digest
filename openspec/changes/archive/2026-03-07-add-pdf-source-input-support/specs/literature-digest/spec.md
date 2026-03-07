## ADDED Requirements

### Requirement: PDF Conversion SHALL Fall Back Gracefully
When `source_path` is detected as PDF, the skill MUST first attempt conversion via `pymupdf4llm`. If that path is unavailable or fails, the skill MUST attempt a Python-standard-library fallback before returning an error.

#### Scenario: Optional dependency unavailable
- **WHEN** `source_path` is detected as PDF and `pymupdf4llm` cannot be imported or raises during conversion
- **THEN** the skill MUST attempt a standard-library fallback conversion
- **AND** the skill MUST continue execution if fallback produces usable markdown
- **AND** the skill MUST record a warning that fallback conversion was used

#### Scenario: Both PDF conversion paths fail
- **WHEN** `source_path` is detected as PDF and both `pymupdf4llm` and fallback conversion fail
- **THEN** the skill MUST return a schema-compatible error result
- **AND** it MUST NOT emit a false-success digest/references/citation output

## MODIFIED Requirements

### Requirement: Artifact File Protocol

Artifacts MUST be written to the directory of `source_path` using fixed filenames:
- `digest.md`
- `references.json`
- `citation_analysis.json`

#### Scenario: Avoid stdout truncation
- **GIVEN** large outputs (digest and analysis)
- **WHEN** producing stdout
- **THEN** stdout MUST remain a single JSON object containing only file paths and audit fields.

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
