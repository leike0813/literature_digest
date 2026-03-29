# Design

## Decision

Stage 4 keeps `prepare_references_workset` as the deterministic entrypoint, but no longer assumes deterministic splitting is always sufficient. The runtime now supports a second stage-4 action, `persist_reference_entry_splits`, which is only invoked when grouped-entry suspicion remains after deterministic splitting.

## Runtime Behavior

- `prepare_references_workset`
  - splits references into raw entries
  - classifies the workset as `numeric`, `author-year`, or `mixed`
  - detects grouped-entry suspicion
  - writes the draft workset and either:
    - advances directly to `persist_references`, or
    - advances to `persist_reference_entry_splits`
- `persist_reference_entry_splits`
  - accepts only ordered `entries[*].raw`
  - requires the reviewed raws to preserve the original references scope text exactly
  - rebuilds `reference_entries`, `reference_parse_candidates`, and `reference_batches`
  - blocks if grouped-entry suspicion still remains

## Guardrails

- Split review is boundary-only; it must not extract `author`, `title`, or `year`
- `persist_references` remains unchanged in purpose and still operates on prepared candidates only
- Stage 4 must not silently continue when grouped-entry suspicion remains in author-year references
