# literature-analysis Delta Specification

## Requirements

### Requirement: Runtime SHALL NOT Depend On Old Skill Package

`literature-analysis/scripts/**` SHALL NOT import, dynamically load, or read runtime code or runtime assets from `literature-digest`.

#### Scenario: Runtime code is inspected
- **WHEN** `literature-analysis/scripts/**` is scanned
- **THEN** it contains no runtime references to `literature-digest/scripts`
- **AND** it contains no migration fallback modules such as `legacy.py` or `stage_adapter.py`.

### Requirement: Algorithms SHALL Be Owned Locally

The normal `literature-analysis` command path SHALL execute deterministic source, plan, digest, reference, citation, status, and render algorithms from modules inside `literature-analysis`.

#### Scenario: Public command runs
- **WHEN** any public `run_analysis.py` command runs
- **THEN** the command is handled by local `analysis_runtime` code
- **AND** no old skill module is loaded by path.

### Requirement: Runtime Assets SHALL Be Owned Locally

Render templates and render schemas used by `literature-analysis` SHALL be resolved from `literature-analysis/assets` or runtime temporary paths derived from those local assets.

#### Scenario: Outputs are finalized
- **WHEN** `finalize_outputs` or citation analysis submit renders public artifacts
- **THEN** `digest.md`, `references.json`, `citation_analysis.json`, `citation_analysis.md`, and `literature_matching_metadata.json` are produced from local assets and DB state.
