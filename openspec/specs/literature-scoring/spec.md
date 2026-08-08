## Purpose
Define a source-grounded, auditable paper scoring capability that separates observed scientific quality from assessment confidence and renders one stable machine-consumable artifact.

## Requirements
### Requirement: Scoring SHALL Use A Fixed Six-Dimension Rubric

The scorer SHALL evaluate methodological rigor at 25%, evidence completeness at 20%, reproducibility at 15%, innovation signals at 15%, research impact potential at 15%, and writing quality at 10% using the canonical rubric distributed with the Skill.

#### Scenario: Complete empirical-paper assessment

- **WHEN** the agent submits every canonical criterion with an applicable score
- **THEN** the runtime computes all six dimension scores on a 0–100 scale
- **AND** computes the quality total from the configured dimension weights.

#### Scenario: Agent submits runtime-owned scoring fields

- **WHEN** the semantic payload contains weights, maximum scores, dimension totals, effective weights, or overall totals
- **THEN** the runtime rejects the payload with `score_payload_invalid`.

### Requirement: Scoring SHALL Separate Quality And Confidence

The public score artifact SHALL expose `overall_score`, `confidence`, and `confidence_adjusted_score`, where the adjusted score is the product of the first two values.

#### Scenario: Score calculation succeeds

- **WHEN** the semantic scoring payload is valid
- **THEN** `overall_score` is the effective-weighted mean of active dimension scores
- **AND** `confidence` is the effective-weighted mean of active dimension confidences
- **AND** `confidence_adjusted_score` equals `overall_score * confidence`.

#### Scenario: Values require rounding

- **WHEN** a derived score has more precision than the public contract allows
- **THEN** scores are rounded half-up to one decimal place
- **AND** confidence is rounded half-up to two decimal places.

### Requirement: Scoring SHALL Support Inapplicable Criteria

The scorer SHALL distinguish a genuinely inapplicable criterion from a low-scoring or weakly evidenced criterion.

#### Scenario: Some criteria in a dimension are inapplicable

- **WHEN** at least one criterion in a dimension is `not_applicable` and at least one is `scored`
- **THEN** the dimension score is normalized over the applicable maximum points
- **AND** the dimension retains its configured weight.

#### Scenario: Entire dimension is inapplicable

- **WHEN** every criterion in one dimension is `not_applicable`
- **THEN** the public dimension has null score and confidence with zero effective weight
- **AND** its configured weight is redistributed proportionally over active dimensions
- **AND** the runtime records a warning.

#### Scenario: Nothing is scorable

- **WHEN** all six dimensions have no applicable criteria
- **THEN** the runtime rejects the payload with `score_payload_invalid`.

### Requirement: Scoring SHALL Be Grounded In Normalized Source Evidence

Every positive source quotation submitted as evidence SHALL resolve to the declared line range in the normalized source, and scoring SHALL NOT depend on external reputation or impact signals.

#### Scenario: Evidence matches source lines

- **WHEN** an evidence quote appears in the declared normalized-source line range after whitespace normalization
- **THEN** the runtime accepts that evidence item.

#### Scenario: Evidence is fabricated or misplaced

- **WHEN** an evidence line range is invalid or its quote does not occur in that range
- **THEN** the runtime rejects the payload with `score_payload_invalid`
- **AND** reports the affected dimension and criterion.

#### Scenario: Paper does not report a property

- **WHEN** a criterion is scored from the absence of reporting
- **THEN** its evidence array may be empty
- **AND** its reason must explicitly state the observed absence.

### Requirement: Scoring SHALL Validate Complete Canonical Coverage

The semantic payload SHALL contain each canonical dimension and each of its canonical criteria exactly once, using the allowed paper-type and criterion-status enums.

#### Scenario: Coverage is exact

- **WHEN** every expected dimension and criterion key occurs exactly once with valid field types and ranges
- **THEN** the runtime persists the normalized computed assessment.

#### Scenario: Coverage or enum is invalid

- **WHEN** a key is missing, unknown, duplicated, or uses an unsupported enum value
- **THEN** the runtime rejects the payload with structured `score_payload_invalid` details.

### Requirement: Runtime SHALL Render One Stable Score Artifact

The scorer SHALL render `literature_score.json` from DB-backed score state, validate it, register it, and expose its absolute path as `literature_score_path`.

#### Scenario: Score artifact is rendered

- **WHEN** valid scoring state is finalized
- **THEN** `literature_score.json` contains rubric identity, paper type, all three aggregate values, all six dimensions, and every canonical criterion
- **AND** `artifact_registry` records its absolute path.

#### Scenario: A criterion is inapplicable

- **WHEN** a canonical criterion is `not_applicable`
- **THEN** it remains present in the public artifact
- **AND** its score is null while its maximum score and reason remain visible.