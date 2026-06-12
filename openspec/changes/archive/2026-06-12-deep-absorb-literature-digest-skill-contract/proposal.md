## Why

`literature-analysis` has a runnable skeleton and its own first-pass guidance, but the guidance is still too shallow compared with the original `literature-digest/SKILL.md`. The old skill's value is not only its scripts; it also contains hard runtime contracts, shared vocabulary, stage cards, failure boundaries, and concrete examples that keep long agent runs from drifting.

This change deeply absorbs that contract into `literature-analysis` without restoring the old gate-first workflow.

## What Changes

- Upgrade `literature-analysis/SKILL.md` from a thin index into a high-density execution contract.
- Preserve the six `literature-analysis` agent-facing stages:
  - `init_runtime`
  - `persist_analysis_plan`
  - `persist_digest`
  - `persist_references`
  - `persist_citation_analysis`
  - `finalize_outputs`
- Add explicit background automation, stdout, input/output, SQLite SSOT, LLM/script boundary, unified vocabulary, stage-card, success JSON, and failure JSON contracts.
- Deepen `literature-analysis/references/` with old skill rules rewritten for the new six-stage workflow.
- Add guidance regression tests that prevent the new skill from sliding back to a shallow index or importing old gate-only main-path requirements.

## Capabilities

### Modified Capabilities

- `literature-analysis`: gains a complete agent-facing execution contract and deeper reference guidance while keeping the compatible output contract.

## Impact

- **Guidance impact**: `literature-analysis` becomes directly runnable by an agent without needing the old `literature-digest/SKILL.md` as an implicit manual.
- **Runtime impact**: No intended runtime behavior change. This is a documentation-contract and test-hardening change.
- **Compatibility impact**: Existing `literature-digest` and `literature-digest-lite` remain unchanged.
