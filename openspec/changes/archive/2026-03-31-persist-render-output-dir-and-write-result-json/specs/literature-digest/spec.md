# Delta: literature-digest

## ADDED Requirements

### Requirement: Step 1 Persists Final Public Artifact Directory

The skill MUST determine the final public artifact directory during `bootstrap_runtime_db` and persist it in the runtime database.

#### Scenario: Explicit output directory at bootstrap
- **WHEN** `bootstrap_runtime_db` receives `--output-dir`
- **THEN** it stores that normalized directory path in `runtime_inputs.output_dir`
- **AND** later stages treat it as the authoritative public artifact directory

#### Scenario: Bootstrap default output directory
- **WHEN** `bootstrap_runtime_db` runs without `--output-dir`
- **THEN** it stores the current working directory in `runtime_inputs.output_dir`

### Requirement: Final Render Mirrors Stdout JSON To A Fixed Result File

The final render path MUST write the same stdout-compatible JSON object to a fixed sidecar file in the current working directory.

#### Scenario: Render success writes result mirror
- **WHEN** `render_and_validate --mode render` succeeds
- **THEN** it writes `literature-digest.result.json` into the current working directory
- **AND** the file content exactly matches the JSON printed to stdout

#### Scenario: Render failure writes result mirror
- **WHEN** `render_and_validate --mode render` returns a schema-compatible failure JSON
- **THEN** it also writes that same JSON object into `literature-digest.result.json`
