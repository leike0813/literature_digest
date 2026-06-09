# Design: Deterministic Reference Preprocess v1.7.1

## Runtime Flow

`prepare_references_workset` remains the only source of deterministic reference preprocessing. It writes reference entries, parse candidates, batches, warnings, and a new one-row `reference_preprocess_quality` snapshot. If that snapshot has `file_quality_low=false`, Stage 4 continues to `persist_references`. If it has `file_quality_low=true`, Stage 4 routes to `decide_reference_extraction`.

`decide_reference_extraction` accepts `decision=continue` or `decision=abandon`. The stage script reads DB state and only allows `abandon` when `reference_preprocess_quality.file_quality_low=true` and the snapshot was produced by the deterministic v1.7.1 preprocess path. Payload-provided quality fields are ignored.

## Reference-Free Citation Mode

When the decision row is `status=abandoned`, citation analysis enters reference-free mode. Stage 5 still extracts mentions from the persisted citation scope, but does not require stable `ref_index` mapping. Unresolved mentions are persisted with a stable reason code, semantic items may be empty, timeline buckets may have empty `ref_indexes`, and summary basis may have empty `key_ref_indexes`.

Normal mode remains strict. Empty citation items, missing workset items, or invalid `ref_index` references are accepted only in reference-free mode.

## File Quality Signals

The v1.7.1 file-level signal set is preserved:

- `fallback_best_ratio > 0.50`
- `year_ratio < 0.20`
- `warning_density > 1.0`
- `numbering_anomaly = true`
- `empty_title_ratio > 0.30`

At least four of five signals must trigger before `file_quality_low=true`.

## Compatibility

`references.json` remains a bare array. In abandoned mode it renders as `[]`. `citation_analysis.json` keeps the existing top-level shape and adds `meta.reference_extraction` so downstream readers can detect reference-free analysis.
