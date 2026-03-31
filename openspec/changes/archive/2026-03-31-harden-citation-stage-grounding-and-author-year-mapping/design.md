# Design

## Action receipts as execution proof

Add an internal `action_receipts` table keyed by `action_name`. Every successful main-path action writes one receipt containing:

- `action_name`
- `stage`
- `status`
- `metadata_json`
- `updated_at`

Receipts are invalidated downstream whenever an earlier main-path action reruns. This keeps the receipt chain aligned with the current DB state instead of treating old stage-5 writes as still valid after upstream changes.

## Stage-5 receipt chain enforcement

Stage 5 and stage 6 no longer rely only on table counts.

Required stage-5 receipts:

- `prepare_citation_workset`
- `persist_citation_semantics`
- `persist_citation_timeline`
- `persist_citation_summary`

Enforcement rules:

- Gate blocks `persist_citation_semantics` if `prepare_citation_workset` receipt is missing.
- Gate blocks `persist_citation_timeline` if `persist_citation_semantics` receipt is missing.
- Gate blocks `persist_citation_summary` if `persist_citation_timeline` receipt is missing.
- Gate blocks `render_and_validate` if any required stage-5 receipt is missing.
- Render mode repeats the same receipt-chain check before producing artifacts, so hand-written `workflow_state` changes cannot bypass the contract.

## Citation grounding hardening

`prepare_citation_workset` becomes stricter in review-like or citation-shaped scopes:

- If the scope title looks like review/background/related-work material, or the scope text contains citation-shaped signals, zero stable mentions/workset items is treated as failure.
- The returned error code is `citation_mentions_not_found`.

Grounding for later stage-5 actions is also tightened:

- `persist_citation_timeline.timeline.*.ref_indexes` must resolve against persisted `citation_items`.
- `persist_citation_summary.basis.key_ref_indexes` must resolve against persisted `citation_items`.

This prevents timeline or summary rows from referencing citations that never completed item-level semantic analysis.

## Author-year first-author alias normalization

Reference-side first-author matching now derives an alias set rather than a single naive token.

For the first author string, generate aliases from:

- the full pre-comma segment, normalized to lowercase
- the last surname-like token inside that pre-comma segment

Examples:

- `Cheng, G.` -> `cheng`
- `Waqas Zamir, S.` -> `waqas zamir`, `zamir`

Mention-side surname extraction keeps its current “last surname-like token” behavior. Matching succeeds when the mention-side surname hint appears in the reference-side alias set for the same year.

## Guidance alignment

Guidance changes stay lightweight and reinforce runtime behavior rather than replacing it:

- stage 5 must be advanced only through scripted actions
- timeline and summary must be grounded on persisted `citation_items`
- author-year matching uses first-author surname aliases instead of a first-token shortcut
