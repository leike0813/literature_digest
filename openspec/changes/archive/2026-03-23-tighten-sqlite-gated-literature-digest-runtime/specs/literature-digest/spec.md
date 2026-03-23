## ADDED Requirements

### Requirement: Final Artifacts SHALL Be Rendered Through Templates

The skill MUST render final artifacts through explicit templates using schema-validated render contexts built from the SQLite runtime database.

#### Scenario: Successful final render
- **WHEN** the runtime reaches render-and-validate
- **THEN** `digest.md`, `references.json`, `citation_analysis.json`, and optional `citation_analysis.md` are rendered through template assets
- **AND** the renderer validates the render context before emitting files.

### Requirement: SKILL Contract SHALL Stay Minimal

`SKILL.md` MUST contain only the durable runtime contract, while detailed step instructions and examples live under `literature-digest/references/`.

#### Scenario: Step-specific guidance
- **WHEN** the agent needs detailed execution instructions for a stage or substep
- **THEN** the relevant guidance is provided through `references/step_*.md`
- **AND** `SKILL.md` does not duplicate those step-level examples.

## MODIFIED Requirements

### Requirement: Optional Citation Report Path SHALL Remain Optional

The stdout contract SHALL treat `citation_analysis_report_path` as an optional field.

#### Scenario: Report path present
- **WHEN** `report_md` is available for the final citation analysis
- **THEN** the stdout object MAY include `citation_analysis_report_path`
- **AND** the file content MUST equal `citation_analysis.json.report_md` exactly.
