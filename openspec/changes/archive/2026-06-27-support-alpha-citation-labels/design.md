## Context

The runtime already maps LaTeX `\cite{...}` mentions through `citekey_hint`, numeric mentions through `ref_number_hint`, and author-year mentions through surname/year hints. Markdown converted from PDFs can contain BibTeX-style alpha labels such as `[RNSS18]`, but those labels are currently neither extracted from references nor emitted as citation mention hints.

## Goals / Non-Goals

**Goals:**
- Treat source-local bracket-alpha labels as deterministic mapping hints.
- Keep alpha label handling internal to runtime preparation and rendering.
- Avoid guessing when labels are unknown or ambiguous.

**Non-Goals:**
- Do not change agent-submitted citation semantic payload fields.
- Do not add public artifact schema fields.
- Do not infer labels from author names when the source does not expose a label.

## Decisions

- Reuse the existing citekey-style join path by adding a normalized `citation_label_hint` and reference alias map. This avoids introducing a new semantic payload concept.
- Store detected labels in reference item metadata and citation workset metadata. The DB schema already preserves unknown mention metadata and workset metadata as JSON.
- Prefer original source label for rendering when present. Numeric labels remain `[n]`; author-year-only items remain `[AY-k]`.
- Ambiguous duplicate labels are not mapped. This prevents silently attaching a citation to the wrong reference.

## Risks / Trade-offs

- OCR/TeX normalization can miss severely corrupted labels -> unmatched labels remain unmapped rather than guessed.
- Very short all-letter labels can look like ordinary bracketed text -> only labels that match a persisted reference alias are mapped into workset items.
- Duplicate labels reduce recall -> ambiguity warnings make the failure auditable without unsafe mapping.
