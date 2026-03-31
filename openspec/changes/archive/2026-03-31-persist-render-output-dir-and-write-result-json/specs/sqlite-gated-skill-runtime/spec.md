# Delta: sqlite-gated-skill-runtime

## ADDED Requirements

### Requirement: Render Output Directory SHALL Be DB-Authoritative

The DB-authoritative final render mode SHALL derive its output directory from `runtime_inputs.output_dir` instead of accepting a late output-directory override.

#### Scenario: Final render uses DB output directory
- **WHEN** `render_and_validate --mode render` runs and `runtime_inputs.output_dir` exists
- **THEN** the runtime writes the fixed artifact filenames into that directory
- **AND** the final stdout payload reports those actual artifact paths

#### Scenario: Final render falls back to current working directory
- **WHEN** `render_and_validate --mode render` runs and `runtime_inputs.output_dir` is missing or empty
- **THEN** the runtime writes the fixed artifact filenames into the current working directory

#### Scenario: Final render rejects late output-directory override
- **WHEN** `render_and_validate --mode render` receives `--out-dir`
- **THEN** the runtime returns a schema-compatible error payload
- **AND** it does not treat the CLI override as authoritative
