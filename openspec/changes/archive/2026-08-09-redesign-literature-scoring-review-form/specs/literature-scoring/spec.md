## MODIFIED Requirements

### Requirement: Scoring SHALL Use A Fixed Six-Dimension Rubric

The scorer SHALL evaluate methodological rigor at 25%, evidence completeness at 20%, reproducibility at 15%, innovation signals at 15%, research impact potential at 15%, and writing quality at 10% using the canonical rubric distributed with the Skill. The canonical rubric SHALL be the sole definition of paper-type choices and descriptions, dimension and criterion keys, display names, prompts, ordering, configured weights, and maximum scores used by the agent-facing review form.

#### Scenario: Complete empirical-paper assessment

- **WHEN** the agent submits a complete generated review form with every canonical criterion applicable and scored
- **THEN** the runtime computes all six dimension scores on a 0–100 scale
- **AND** computes the quality total from the configured dimension weights.

#### Scenario: Review form is generated from the rubric

- **WHEN** the scoring stage is prepared
- **THEN** the runtime prepopulates every rubric-owned paper-type, dimension, and criterion field in rubric order
- **AND** the agent does not need to author enum values, stable keys, maximum scores, or configured weights.

#### Scenario: Agent changes a runtime-owned scoring field

- **WHEN** a submitted draft changes a rubric-owned field or removes a canonical form entry
- **THEN** the runtime rejects the draft with `score_review_invalid`
- **AND** identifies the failure with `locked_field_changed` or `incomplete_answer` as applicable.

#### Scenario: Agent submits runtime-owned scoring fields

- **WHEN** the submitted draft changes weights, maximum scores, names, keys, prompts, ordering, or any other locked rubric field
- **THEN** the runtime rejects the draft with `score_review_invalid`
- **AND** reports `locked_field_changed`.

### Requirement: Scoring SHALL Be Grounded In Normalized Source Evidence

Every positive source quotation submitted as evidence SHALL resolve to the normalized source, and scoring SHALL NOT depend on external reputation or impact signals. The runtime SHALL derive the public evidence line range from the located quotation.

#### Scenario: Evidence matches source lines

- **WHEN** an evidence quote matches the normalized source after NFKC normalization, case folding, whitespace normalization, and punctuation normalization
- **THEN** the runtime accepts that evidence item
- **AND** records the earliest matching source line range.

#### Scenario: Evidence requires fuzzy location

- **WHEN** no exact normalized match exists and the normalized quotation contains at least 8 characters
- **THEN** the runtime searches continuous one-to-five-line windows using character bigrams for 8–11 characters and character trigrams for longer quotations
- **AND** accepts the earliest best match when similarity is at least 0.45.

#### Scenario: Evidence is fabricated or misplaced

- **WHEN** an evidence quote has no acceptable exact or fuzzy source match
- **THEN** the runtime rejects the form with `score_review_invalid`
- **AND** reports the criterion, evidence index, best similarity, and candidate line range.

#### Scenario: Paper does not report a property

- **WHEN** a criterion is scored from the absence of reporting
- **THEN** its evidence quotation array may be empty
- **AND** its reason must explicitly state the observed absence.

### Requirement: Scoring SHALL Validate Complete Canonical Coverage

The runtime SHALL generate a self-describing review form for the exact canonical rubric and source snapshot. The agent SHALL select exactly one generated paper-type choice and SHALL only supply paper-type reasoning, dimension confidence and summaries, criterion applicability, scores, reasons, and evidence quotations.

#### Scenario: Review form is prepared

- **WHEN** scoring prerequisites exist and the agent prepares the scoring stage
- **THEN** the runtime writes an immutable original form and an editable draft to distinct temporary paths
- **AND** returns both paths, the editable field set, and a submit command without inlining every criterion.

#### Scenario: Prepare is repeated for the same form

- **WHEN** prepare is called again with the same normalized-source and rubric snapshot hashes
- **THEN** the runtime returns the same form identity and paths
- **AND** does not overwrite an existing draft.

#### Scenario: Form source or rubric is stale

- **WHEN** a submitted form identity does not match the current normalized-source and rubric snapshot hashes
- **THEN** the runtime rejects the draft with `score_review_invalid`
- **AND** reports `stale_form`.

#### Scenario: Coverage or enum is invalid

- **WHEN** the draft selects zero or multiple paper types, leaves a required semantic answer incomplete, supplies an invalid applicable score, or supplies a score for an inapplicable criterion
- **THEN** the runtime rejects the draft with `score_review_invalid`
- **AND** reports `invalid_selection` or `incomplete_answer` with the affected field.

#### Scenario: Coverage is exact

- **WHEN** locked fields match, exactly one paper type is selected, and all editable answers are valid
- **THEN** the runtime derives criterion statuses and evidence line ranges
- **AND** persists the same normalized computed assessment used by the public `literature_score.v1` artifact.
