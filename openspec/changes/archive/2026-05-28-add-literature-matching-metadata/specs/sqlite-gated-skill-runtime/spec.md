## ADDED Requirements

### Requirement: Runtime SHALL Persist Matching Metadata In SQLite

The SQLite-gated runtime SHALL store literature matching metadata in a dedicated DB table and use that table as the only render source for the public sidecar.

#### Scenario: Matching metadata persistence succeeds

- **WHEN** `persist_outline_and_scopes` receives valid matching metadata
- **THEN** the runtime writes it to SQLite
- **AND** subsequent render reads the DB value instead of recomputing it.

#### Scenario: Invalid matching metadata is rejected

- **WHEN** matching metadata is missing required fields, uses the wrong schema, has non-array fields, has non-string array items, or exceeds field limits
- **THEN** `persist_outline_and_scopes` fails
- **AND** the workflow does not advance.

### Requirement: Runtime SHALL Render And Validate Matching Metadata Artifact

The final render path SHALL materialize, register, and validate `literature_matching_metadata.json`.

#### Scenario: Render registers matching metadata artifact

- **WHEN** `render_and_validate --mode render` completes
- **THEN** `artifact_registry` contains `literature_matching_metadata_path`
- **AND** `build_public_output_payload()` returns that absolute path.

#### Scenario: Check mode validates matching metadata file

- **WHEN** `render_and_validate --mode check` receives a non-empty `literature_matching_metadata_path`
- **THEN** it validates the referenced JSON object against the v1 shape.
