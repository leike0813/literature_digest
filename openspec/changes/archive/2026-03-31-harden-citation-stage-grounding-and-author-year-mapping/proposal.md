# Proposal

## Summary

Harden stage 5 so citation analysis can no longer be bypassed by direct SQLite writes, and fix author-year mapping for multi-token first-author names such as `Waqas Zamir`.

## Why

The latest run failure was not caused by a general citation-regex breakdown. The runtime could already extract and map most mentions from the SOPSeg sample, but the execution chain was bypassed: `citation_summary`, `citation_timeline`, and `workflow_state` were written directly to SQLite, and render was invoked without a valid stage-5 script trail.

At the same time, one real mapping gap remains: author-year matching currently normalizes the reference-side first author too aggressively, which misses names like `Waqas Zamir, S.` when the mention-side surname hint is `zamir`.

## Goals

- Persist verifiable action receipts for scripted main-path actions.
- Require a complete stage-5 receipt chain before gate or render will allow final publication.
- Fail `prepare_citation_workset` when review-like or citation-shaped scopes produce zero stable mentions/workset items.
- Ground timeline and summary ref-index validation on persisted `citation_items`, not merely `citation_workset_items`.
- Normalize first-author surname aliases so multi-token names map reliably in author-year mode.
- Update guidance and regression tests to reflect the stricter stage-5 contract.

## Non-Goals

- No change to public artifact filenames.
- No change to public stdout schema.
- No automatic repair that silently fabricates missing stage-5 data.
