# Design: improve-citation-analysis-guidance-and-summary-quality

## Overview

This change keeps the existing stage order:

1. `prepare_citation_workset`
2. `persist_citation_semantics`
3. `persist_citation_summary`
4. `render_and_validate --mode render`

The main change is that stage 5 payloads carry a little more structure so the agent has to think in terms of topic, usage, and key references before rendering.

## Stage-5 payload design

### `persist_citation_semantics`

Each item remains keyed by `ref_index`, but now must include:

- `ref_index`
- `function`
- `topic`
- `usage`
- `summary`
- `is_key_reference`
- `confidence`

Rationale:

- `function` remains the coarse bucket
- `topic` says what this cited work represents in the review
- `usage` says how the source paper uses it
- `summary` becomes a concise prose consequence of the first two
- `is_key_reference` lets the renderer surface a small set of key papers

### `persist_citation_summary`

The global summary still stores a natural-language `summary`, but `basis` is now required:

- `research_threads`
- `argument_shape`
- `key_ref_indexes`

Rationale:

- weak models need a lightweight scaffold before writing a coherent summary
- the renderer can reuse `key_ref_indexes` for a stable “Key References” section

## Validation strategy

This change does not attempt brittle text-quality scoring.

Instead it validates:

- field presence
- non-empty strings for `topic`, `usage`, and `summary`
- boolean type for `is_key_reference`
- minimum list sizes for `research_threads` and `argument_shape`
- existence of every `key_ref_indexes` entry in the current citation workset

## Rendering changes

`report_md` remains renderer-derived only.

The report render context now includes:

- `summary`
- `summary_basis`
- `key_references`
- grouped citation items
- ordered citation items
- unmapped mentions

The Markdown report adds a short “Key References” section between the overall summary and the grouped analysis.

## Compatibility

- No public file names change.
- Top-level stdout keys stay unchanged.
- `citation_analysis.json.items[]` can surface extra optional fields without breaking existing required fields.
- Old stage-5 payloads that omit the new fields are intentionally rejected.
