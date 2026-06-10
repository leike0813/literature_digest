## ADDED Requirements

### Requirement: Reject Placeholder Reference Titles

`literature-digest` SHALL hard-block Stage 4 reference rows whose entire `title` is a placeholder value rather than a cited work title.

#### Scenario: Placeholder title blocks reference persistence

- **WHEN** `persist_references` receives a row whose normalized title is `none`, `null`, `undefined`, `n/a`, `na`, `not available`, `unknown`, or `untitled`
- **THEN** the runtime SHALL NOT write `reference_items`
- **AND** it SHALL emit a hard quality issue with reason code `placeholder_title`
- **AND** the workflow SHALL remain at `stage_4_references / persist_references`.

#### Scenario: Placeholder words inside real titles are allowed

- **WHEN** `persist_references` receives a title such as `Unknown Unknowns` or `Untitled Document Classification`
- **THEN** the placeholder rule SHALL NOT hard-block the row solely because it contains a placeholder word.

#### Scenario: JSON null title remains an empty-title issue

- **WHEN** `persist_references` receives JSON `title: null`
- **THEN** the existing `empty_title` hard reason SHALL continue to apply.
