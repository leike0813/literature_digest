## ADDED Requirements

### Requirement: Stage 4 Reference Quality Gate

`literature-digest` SHALL classify finalized Stage 4 reference rows before citation workset preparation.

#### Scenario: Hard reference quality issue blocks persistence

- **WHEN** `persist_references` receives any row whose title is empty, a bare identifier or URL, publication metadata only, author-only text, or has no usable title tokens
- **THEN** the runtime SHALL NOT write `reference_items`
- **AND** the workflow SHALL remain at `stage_4_references / persist_references`
- **AND** the gate SHALL return `quality_directives` naming each affected `entry_index`/`ref_index`, stable reason code, evidence fields, and repair recommendation.

#### Scenario: Soft reference quality warning requires explicit review

- **WHEN** `persist_references` receives rows with only soft quality warnings
- **THEN** the runtime SHALL write `reference_items`
- **AND** affected rows SHALL include compatible `metadata.title_quality.status = "warning"` and `flags`
- **AND** the workflow SHALL advance to `stage_4_references / review_reference_quality`
- **AND** the gate SHALL instruct the agent to correct or explicitly accept every warning.

#### Scenario: References artifact remains a bare array

- **WHEN** final artifacts are rendered
- **THEN** `references.json` SHALL remain a JSON array of native reference objects
- **AND** quality metadata SHALL NOT introduce a top-level wrapper.

