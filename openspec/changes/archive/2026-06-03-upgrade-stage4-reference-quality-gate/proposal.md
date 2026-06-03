# Change: Upgrade Stage 4 Reference Quality Gate

## Summary

Upgrade `literature-digest` Stage 4 so extracted reference rows are classified for stable title/reference quality issues before citation analysis can proceed. Hard quality issues block `persist_references` and return actionable gate directives. Soft quality issues are persisted as warnings and routed through an explicit `review_reference_quality` action before Stage 5.

## Motivation

Stage 4 can currently accept rows whose `title` is actually a DOI, URL, venue string, author text, or other unusable fragment. Those rows degrade citation matching and downstream discovery. Existing failures are script-level errors or runtime warnings, but they do not consistently tell the agent which rows are problematic or how to repair them. This change makes reference quality review DB-backed and gate-visible.

## Scope

- Add DB-backed `reference_quality_issues` as the durable source for Stage 4 quality instructions.
- Add a plugin-compatible classifier contract in `stage_runtime.py`.
- Block hard quality issues before writing `reference_items`.
- Allow soft warnings to write references, attach compatible `metadata.title_quality`, then route to `review_reference_quality`.
- Expose hard and soft issues through `gate_runtime.py` as `quality_directives`.
- Keep `references.json` as a bare array of native reference objects.

## Out Of Scope

- No changes to `literature-digest-lite`.
- No import or runtime dependency on plugin TS/MJS code.
- No top-level wrapper around `references.json`.
- No change to citation analysis semantics.

