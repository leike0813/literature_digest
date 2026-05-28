## ADDED Requirements

### Requirement: Successful Digest Output SHALL Include Literature Matching Metadata Sidecar

The main `literature-digest` skill SHALL publish a `literature_matching_metadata.json` artifact for successful runs and SHALL return its absolute path as `literature_matching_metadata_path` in stdout and `literature-digest.result.json`.

#### Scenario: Successful run publishes matching metadata path

- **WHEN** a `literature-digest` run completes successfully
- **THEN** stdout includes `literature_matching_metadata_path`
- **AND** the path points to `literature_matching_metadata.json` in the configured output directory
- **AND** `literature-digest.result.json` contains the same path.

#### Scenario: Schema-compatible failure keeps required path field

- **WHEN** a run fails before final render
- **THEN** stdout still includes `literature_matching_metadata_path`
- **AND** its value is an empty string.

### Requirement: Matching Metadata SHALL Use Fixed V1 Shape

The `literature_matching_metadata.json` artifact SHALL contain exactly the v1 matching metadata shape with no generated `bm25_text`.

#### Scenario: Rendered sidecar shape

- **WHEN** `literature_matching_metadata.json` is rendered
- **THEN** it contains `schema = "literature_matching_metadata.v1"`
- **AND** it contains `key_terms`, `methods`, `problems`, `datasets`, and `exclude_terms` arrays
- **AND** it does not contain `bm25_text`.

### Requirement: Matching Metadata SHALL Be Authored During Outline And Scope Stage

Stage 02 SHALL collect matching metadata together with outline and scope decisions.

#### Scenario: Stage 02 payload includes matching metadata

- **WHEN** `persist_outline_and_scopes` is called on the main path
- **THEN** the payload must include `literature_matching_metadata`
- **AND** the runtime persists it before advancing to Stage 03.
