## Why

A real `literature-analysis` run succeeded, but the agent-facing payloads exposed too many internal runtime details. The agent had to manually choose private candidate pattern names, map source reference numbers to internal `ref_index` values, maintain timeline closure, and hand-edit large JSON payloads.

This change hard-cuts the agent-facing interface to semantic, flat payloads and makes batch delegation explicit for reference review, metadata review, and citation semantic analysis.

## What Changes

- Replace old submit shapes with current-state payloads:
  - references use `reference_reviews[]`
  - citations use `citation_semantic_reviews[]` and `timeline_summaries`
- Prepare responses include JIT guidance, allowed parse pattern enumerations, work packages, and subagent prompt templates.
- Runtime normalizers map agent-friendly identifiers to internal IDs and deterministic handlers.
- Timeline buckets are derived by runtime from dated citation items.
- Instructions describe only the current payload contract.

## Capabilities

### Modified Capabilities

- `literature-analysis`: exposes safer agent-facing payloads and explicit subagent batch workflow while keeping the public CLI and final artifacts unchanged.

## Impact

- **Agent-facing impact**: breaking change to payload shape.
- **Runtime impact**: normalizers translate semantic payloads to internal deterministic persistence.
- **Artifact impact**: final `digest.md`, `references.json`, `citation_analysis.json`, `citation_analysis.md`, and matching metadata remain compatible.
