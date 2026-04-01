## ADDED Requirements

### Requirement: Runtime Paths SHALL Be Confirmed Before Bootstrap

New runs MUST confirm runtime directories before bootstrap persists source inputs.

#### Scenario: Startup confirms shell cwd first
- **WHEN** a new run starts
- **THEN** the first runtime action is `confirm_runtime_paths`
- **AND** it persists `working_dir`, `tmp_dir`, `db_path`, `result_json_path`, and `output_dir`
- **AND** `bootstrap_runtime_db` runs only after that confirmation step.

### Requirement: Final Public Output Paths SHALL Be Absolute

The final stdout payload SHALL emit absolute artifact paths.

#### Scenario: Render succeeds
- **WHEN** `render_and_validate --mode render` completes successfully
- **THEN** `digest_path`, `references_path`, `citation_analysis_path`, and `citation_analysis_report_path` (when present) are absolute paths.
