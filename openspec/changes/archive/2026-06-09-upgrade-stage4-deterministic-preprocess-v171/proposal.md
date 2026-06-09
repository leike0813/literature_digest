# Change: Upgrade Stage 4 Deterministic Reference Preprocess v1.7.1

## Summary

Upgrade `literature-digest` Stage 4 reference preprocessing to the deterministic line-first v1.7.1 behavior validated in experiments. The runtime will generate stronger parse candidates, persist DB-backed file-level reference quality signals, and expose a guarded decision point that lets the agent continue reference extraction or explicitly abandon it only when deterministic preprocessing proves the file quality is too low.

## Motivation

The current Stage 4 candidate generation is weaker than the latest deterministic experiment branch, especially for CJK/fullwidth references, IEEE-style quoted titles, author initials, and noisy non-reference lines. Severe OCR/noisy files also need an auditable path where citation analysis can continue without unreliable `ref_index` mapping, but only when the runtime has produced a trustworthy file-level low-quality signal.

## Scope

- Migrate deterministic preprocessing capabilities from `line_first_v171.py` into `literature-digest` runtime code without importing from `experiments/`.
- Persist file-level reference preprocess quality in SQLite.
- Add `decide_reference_extraction` for low-quality files.
- Add reference-free citation mode after an explicit, DB-verified abandon decision.
- Update gate payload guidance, runtime docs, and regression tests.

## Out Of Scope

- No changes to `literature-digest-lite`.
- No new third-party tokenizer/parser dependency.
- No wrapper around `references.json`.
- No automatic abandonment; the agent must choose through the gate-directed action.
