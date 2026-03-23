## ADDED Requirements

### Requirement: SQLite Runtime SHALL Be the Only Process Truth

The skill MUST persist process data and final artifact payload data into a SQLite runtime database under `<cwd>/.literature_digest_tmp/` before rendering final files.

#### Scenario: Final files rendered from DB
- **WHEN** the skill completes successfully
- **THEN** `digest.md`, `references.json`, and `citation_analysis.json` are rendered from database state
- **AND** no intermediate hidden file is required as process truth.

### Requirement: Optional Citation Report Path SHALL Remain Optional

The stdout contract SHALL treat `citation_analysis_report_path` as an optional field.

#### Scenario: Report path present
- **WHEN** `report_md` is available for the final citation analysis
- **THEN** the stdout object MAY include `citation_analysis_report_path`
- **AND** the file content MUST equal `citation_analysis.json.report_md` exactly.

## MODIFIED Requirements

### Requirement: Artifact File Protocol

Artifacts MUST be written to the directory of `source_path` using fixed filenames:
- `digest.md`
- `references.json`
- `citation_analysis.json`
- `citation_analysis.md` (optional sidecar report)

#### Scenario: Public output contract remains compatible
- **WHEN** the DB-first runtime succeeds
- **THEN** all existing required stdout fields remain present
- **AND** `citation_analysis_report_path` remains optional.
