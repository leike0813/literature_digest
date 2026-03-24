# Design: add-citation-keywords-and-timeline-analysis

## Overview

Stage 5 expands from three semantic steps to four:

1. `prepare_citation_workset`
2. `persist_citation_semantics`
3. `persist_citation_timeline`
4. `persist_citation_summary`
5. `render_and_validate --mode render`

The key idea is to keep `report_md` renderer-derived while asking the agent for slightly richer structured inputs: per-item `keywords` and a separate time-ordered narrative of the cited field.

## Citation semantics payload

Each `persist_citation_semantics.items[*]` entry remains keyed by `ref_index` and now must include:

- `ref_index`
- `function`
- `topic`
- `usage`
- `summary`
- `keywords`
- `is_key_reference`
- `confidence`

`keywords` are short phrases, not sentences. They summarize the topic, method, task, or object that this cited work represents inside the current review scope.

## Timeline payload

`persist_citation_timeline` stores one structured object:

- `timeline.early`
- `timeline.mid`
- `timeline.recent`

Each bucket must contain:

- `summary`
- `ref_indexes`

The runtime does not impose fixed year thresholds. The agent decides the bucket boundaries semantically, but every citation item with a stable year must appear in exactly one bucket. Items with `year == null` may be omitted and should produce a warning.

## Rendering changes

The final report render context grows in three ways:

- richer citation item display fields:
  - `citation_label`
  - `author_year_label`
  - `title`
  - `keywords`
- top-level `timeline`
- stable synthetic labels for author-year citation styles:
  - numeric references keep `[n]`
  - non-numeric references get `[AY-k]`, ordered by earliest mention location

The Markdown report now renders:

- a narrative overall summary
- a “关键文献 / Key References” section
- grouped analysis with nested per-item details
- a “时间线分析 / Timeline Analysis” section with `早期 / 中期 / 近期`

The old “按引用编号/作者-年份列举” section is removed because it was mostly redundant after grouped analysis and did not explain chronological development.

## Validation strategy

The runtime adds structure checks, not brittle text scoring:

- `keywords` must be a non-empty array of non-empty strings
- `timeline` must contain `early`, `mid`, and `recent`
- the same `ref_index` cannot appear in multiple buckets
- every citation item with a stable year must appear in exactly one bucket
- `persist_citation_summary` cannot run before timeline state exists

## Compatibility

- Public file names stay unchanged.
- Top-level stdout keys stay unchanged.
- `citation_analysis.json` becomes richer but remains backward-compatible at the file name level.
- Old stage-5 payloads that omit `keywords` or skip timeline are intentionally rejected.
