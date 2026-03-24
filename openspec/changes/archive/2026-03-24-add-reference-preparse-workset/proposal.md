# Proposal: add-reference-preparse-workset

## Why

The current references stage asks the agent to turn raw reference entries directly into final `reference_items`. In practice this is unstable for lower-capability models, especially on multi-author colon-style entries where only the first author is retained and the remaining author tail leaks into `title`.

## What Changes

- Split stage 4 into two actions:
  - `prepare_references_workset`
  - `persist_references`
- Add deterministic references preparse that:
  - extracts raw entries from `references_scope`
  - detects numbering
  - generates and stores multiple pattern candidates per entry
  - exports a full workset and a lightweight review view
- Change `persist_references` so it only accepts refined items keyed by `entry_index` plus `selected_pattern`
- Add `reference_parse_candidates` as the candidate SSOT for references refinement
- Update gate, docs, and tests to use the new two-step stage-4 flow

## Impact

- Public artifacts remain unchanged:
  - `references.json` schema and file name stay the same
- Internal runtime contracts change:
  - old `persist_references(entries + batches + items)` payload is rejected
  - stage 4 now requires `prepare_references_workset` before `persist_references`
