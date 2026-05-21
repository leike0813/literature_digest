## ADDED Requirements

### Requirement: Digest Stage SHALL Persist Optional Representative Image Selection

The digest stage SHALL accept an optional `representative_image` object in addition to `digest_slots` and `section_summaries`.

#### Scenario: Selected Markdown image reference

- **GIVEN** Markdown input contains a real Markdown or HTML image reference in the source text
- **WHEN** `persist_digest` receives `representative_image.status = "selected"` with `source_kind = "markdown_image_ref"`
- **THEN** the runtime persists the representative-image metadata
- **AND** `markdown_src_hint` is preserved exactly as a source-text hint rather than rewritten to an absolute path.

#### Scenario: Selected LaTeX image path hint

- **GIVEN** LaTeX input normalization preserves a textual image path such as `\includegraphics{figures/overview}`
- **WHEN** that path is selected as the representative image location hint
- **THEN** the skill may reuse `source_kind = "markdown_image_ref"`
- **AND** `markdown_src_hint` preserves the original source path hint without extension completion, directory rewriting, or file existence checks.

#### Scenario: No reliable representative image

- **WHEN** `persist_digest` receives `representative_image.status = "none"`
- **THEN** the runtime persists only `{ "status": "none" }`.

#### Scenario: Old digest payload remains valid

- **WHEN** `persist_digest` receives the previous payload shape with only `digest_slots` and `section_summaries`
- **THEN** the payload remains valid
- **AND** no `representative_image` field is required in the final output.

### Requirement: Representative Image Output SHALL Be Optional And Additive

The final stdout JSON and mirrored `literature-digest.result.json` SHALL support an optional `representative_image` field without changing existing required fields.

#### Scenario: Representative image was selected

- **WHEN** final render completes after a selected representative image was persisted
- **THEN** the final JSON includes `representative_image.status = "selected"`
- **AND** includes the persisted label, caption quote, selection reason, confidence, and applicable source hints.

#### Scenario: No image was selected

- **WHEN** final render completes after `{ "status": "none" }` was persisted
- **THEN** the final JSON includes `representative_image.status = "none"`.

#### Scenario: PDF figure-caption metadata

- **WHEN** the source is PDF or PDF-derived text and a figure can only be identified by label, caption, and optional page metadata
- **THEN** the final JSON may use `source_kind = "pdf_figure_caption"`
- **AND** no PDF image file is exported or referenced as an artifact.

### Requirement: Representative Image Selection SHALL Be Evidence-Grounded

Representative-image selection SHALL rely only on textual evidence available in normalized source content, captions, nearby paragraphs, section hints, labels, and page hints.

#### Scenario: Prefer method or architecture figure

- **GIVEN** multiple figure candidates are visible in source text
- **WHEN** selecting a representative image
- **THEN** method, architecture, pipeline, model-structure, overall-experiment-design, or central-result figures are preferred over low-information figures.

#### Scenario: Avoid low-information figures

- **GIVEN** candidates are pure tables, formula-only figures, decorative images, or otherwise low-information images
- **WHEN** no better textual evidence exists
- **THEN** the skill returns `representative_image.status = "none"` rather than fabricating a representative image.
