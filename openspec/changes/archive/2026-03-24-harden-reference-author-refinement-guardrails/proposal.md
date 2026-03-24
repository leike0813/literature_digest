# Proposal: harden-reference-author-refinement-guardrails

## Why

The stage-4 references workset now prepares correct `author_candidates`, but weaker models can still split a prepared author boundary a second time during `persist_references`. This produces malformed `author[]` arrays such as `["Al-Rfou", "R.", ...]` even though the prepared candidate already contained `["Al-Rfou, R.", ...]`.

## What Changes

- Strengthen stage-4 guidance so selected `pattern_candidate.author_candidates` becomes the authoritative author-boundary source when it is already stable
- Add runtime validation in `persist_references` that rejects clear second-pass author over-splitting instead of writing malformed `reference_items`
- Add explicit positive/negative examples for multi-author comma-style entries in `SKILL.md`, `step_04_references_extraction.md`, and `stage_runtime_interface.md`
- Add regression tests for the real weak-model failure pattern

## Impact

- Public `references.json` stays unchanged
- Stage-4 actions stay unchanged:
  - `prepare_references_workset`
  - `persist_references`
- Runtime behavior changes:
  - obvious author over-splitting now fails fast with `reference_author_refinement_invalid`
