## Why

`relax-citation-analysis-validation` made citation analysis tolerant at the payload boundary, but the deterministic citation substeps still reject an empty prepared workset. As a result, a valid run with no stable mapped citations can still fail before rendering any final artifacts.

## What Changes

- Treat `prepare_citation_workset` receipt as the proof that citation preparation ran, even when it produced zero workset items.
- Allow empty citation semantics, timeline, and summary substeps to persist action receipts and DB rows.
- Keep unknown submitted citation references as hard failures.
- Allow exporting an explicitly prepared empty citation workset.
- Add regression tests for empty prepared worksets completing final render.

## Capabilities

### New Capabilities

### Modified Capabilities
- `literature-analysis`: Empty prepared citation worksets complete as best-effort citation artifacts instead of failing the workflow.

## Impact

- Affects citation stage runtime gating, export behavior, guidance docs, and runtime tests.
- No agent payload fields or public artifact schema fields are changed.
