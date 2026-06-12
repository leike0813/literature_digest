## Why

`literature-digest` has accumulated a SQLite-gated runtime with many runtime-only stages, deeply nested payloads, and frequent mechanical command handoffs. Recent long-running skill experience suggests a better pattern: keep SQLite as the auditable SSOT, but expose stages only at agent decision points and cascade deterministic runtime work inside scripts.

The new `literature-analysis` skill will be added in parallel so the existing `literature-digest` and `literature-digest-lite` behavior remains unchanged while the new architecture is built and compared safely.

## What Changes

- Add a new OpenSpec capability for `literature-analysis`.
- Add a new `literature-analysis/` skill skeleton with a short `SKILL.md`.
- Add a new runtime entrypoint, `scripts/run_analysis.py`, that wraps and reuses mature `literature-digest` runtime logic.
- Keep SQLite as the runtime SSOT, but expose the first-phase stages as:
  - `init_runtime`
  - `persist_analysis_plan`
  - `persist_digest`
  - `persist_references`
  - `persist_citation_analysis`
  - `finalize_outputs`
- Keep `digest` and `references` as separate agent-facing stages.
- Preserve the existing full output contract and fixed artifact filenames.

## Capabilities

### New Capabilities

- `literature-analysis`: a full literature analysis skill that reuses the old runtime's deterministic normalization, reference preprocessing, citation preprocessing, and rendering behavior while exposing a simpler agent-facing workflow.

### Modified Capabilities

None. Existing `literature-digest` and `literature-digest-lite` behavior is intentionally left unchanged.

## Impact

- **Code impact**: Adds a new skill package and tests. Does not modify the old skill runtime.
- **Compatibility impact**: Successful stdout and public artifact filenames remain compatible with the existing full `literature-digest` contract.
- **Migration impact**: First phase builds a runnable skeleton. Deeper absorption and shared-module cleanup can be done in later changes.
