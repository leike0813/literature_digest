## ADDED Requirements

### Requirement: Hidden Staged Artifacts SHALL Drive Long-Running Outputs

The skill MUST execute references and citation analysis through hidden staged artifacts under `<cwd>/.literature_digest_tmp/` before publishing final public artifacts.

#### Scenario: Temporary staged artifacts are emitted
- **WHEN** the skill processes a valid source document
- **THEN** it writes internal staging artifacts under `<cwd>/.literature_digest_tmp/`
- **AND** those artifacts MAY include `outline.json`, `references_scope.json`, `references.parts/part-*.json`, `references_merged.json`, `citation_scope.json`, `citation_preprocess.json`, `citation.parts/part-*.json`, `citation_merged.json`, and `citation_report.md`
- **AND** those staging artifacts are not part of the public output contract.

### Requirement: References SHALL Be Batched Before Final Publish

The skill MUST split references into entry-based batches before producing the final `references.json`.

#### Scenario: Fixed-size reference batches
- **WHEN** a references section contains more than `15` detected entries
- **THEN** the skill writes multiple `references.parts/part-*.json` files
- **AND** each part contains at most `15` entries
- **AND** the final merged output preserves the original references order.

### Requirement: Citation Analysis SHALL Use Three Explicit Stages

The skill MUST generate citation analysis through three stages: scope decision, semantic parts grounded on preprocess output, and final report aggregation.

#### Scenario: Citation staging order
- **WHEN** citation analysis is generated
- **THEN** `citation_scope.json` is produced before semantic part generation
- **AND** semantic parts are grounded on `citation_preprocess.json`
- **AND** `report_md` is generated only after part merging data is available.

### Requirement: Final Public Artifacts SHALL Be Atomically Published

The skill MUST only publish `references.json` and `citation_analysis.json` after staged merge validation succeeds.

#### Scenario: Merge failure blocks publish
- **WHEN** references merge or citation merge fails validation
- **THEN** the corresponding final public artifact is not published
- **AND** hidden staged artifacts MAY remain for diagnosis
- **AND** the task returns a schema-compatible error result.

### Requirement: Stage-Level Error Codes SHALL Be Exposed

Schema-compatible failure results MUST distinguish stage failures through `error.code`.

#### Scenario: References stage failure code
- **WHEN** the references staging step fails before merge
- **THEN** `error.code` is `references_stage_failed`.

#### Scenario: Citation report failure code
- **WHEN** semantic parts succeed but final report aggregation fails
- **THEN** `error.code` is `citation_report_failed`
- **AND** `citation_analysis_path` is empty.

## MODIFIED Requirements

### Requirement: Artifact File Protocol

Artifacts MUST be written to the directory of `source_path` using fixed filenames:
- `digest.md`
- `references.json`
- `citation_analysis.json`

#### Scenario: Staged internal workflow preserves public names
- **WHEN** the staged pipeline completes successfully
- **THEN** the public artifact filenames remain unchanged
- **AND** callers still receive only `digest_path`, `references_path`, and `citation_analysis_path`.

### Requirement: Citation Analysis SHALL Follow Explicit Multi-Stage Workflow

For citation analysis generation, the system MUST follow an explicit staged workflow defined in `literature-digest/SKILL.md`: scope decision, preprocess extraction, semantic part generation, deterministic merge, report aggregation, and final gate checks.

#### Scenario: Merge gates are mandatory
- **WHEN** semantic citation part files are available
- **THEN** the system merges them deterministically
- **AND** it verifies `mention_id` uniqueness, `ref_index` uniqueness, and preprocess mention coverage before publishing the final artifact.
