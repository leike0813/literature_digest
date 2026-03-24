# Proposal: add-citation-keywords-and-timeline-analysis

## Why

The current citation-analysis stage still leaves too much room for weak models to produce shallow outputs: item-level summaries are often generic, the rendered Markdown is hard for humans to scan, and the old “ordered citations” section does not actually explain how the reviewed field evolved over time.

## What Changes

- Extend `persist_citation_semantics.items[*]` to require `keywords`.
- Add a new stage-5 action `persist_citation_timeline` between item semantics and the global summary.
- Add top-level `timeline` to `citation_analysis.json`.
- Render richer citation items with:
  - `citation_label`
  - `author_year_label`
  - `title`
  - `keywords`
  - `summary`
- Replace the old “按引用编号/作者-年份列举” section with “时间线分析”, using fixed buckets `early`, `mid`, and `recent`.
- For author-year style citations without a numeric reference number, synthesize stable labels as `[AY-k]` in first-mention order.

## Impact

- Public file names stay unchanged.
- Top-level stdout fields stay unchanged.
- `citation_analysis.json` gains a required top-level `timeline` field.
- `citation_analysis.json.items[]` exposes richer derived display fields such as `keywords`, `citation_label`, and `author_year_label`.
- Stage 5 becomes stricter and intentionally rejects under-specified payloads that omit `keywords` or timeline structure.
