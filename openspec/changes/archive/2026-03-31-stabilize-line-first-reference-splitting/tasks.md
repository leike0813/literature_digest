# Tasks

- [x] Rework stage 4 deterministic splitting to be line-first.
- [x] Stop deterministic multiline auto-merge and emit suspect block diagnostics instead.
- [x] Change `persist_reference_entry_splits` to block-level `blocks[]` review with `split` / `keep` / `merge`.
- [x] Regenerate reference workset state from reviewed blocks before `persist_references`.
- [x] Update stage 4 guidance and interface docs to use `suspect_blocks`.
- [x] Add regression coverage for grouped single-line references and multiline continuation review.
