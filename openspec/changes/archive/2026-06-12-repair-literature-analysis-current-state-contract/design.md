## Design

### Current-State Asset Cleanup

`assets/runner.json` and `assets/core_instruction.md` must be aligned with `literature-analysis` rather than the old digest gate flow. They should only mention `scripts/run_analysis.py`, the six public stages, SQLite SSOT, renderer-owned artifacts, and stdout JSON.

### Split Review Adapter

The deterministic runtime already owns entry-split persistence through an internal handler. The `analysis_runtime.references` adapter will translate current agent-facing payload:

- `block_key`
- `action`
- `corrected_reference_texts[]`

into deterministic payload:

- `block_index`
- `resolution`
- `entries[]`

If boundaries change, the adapter returns regenerated review packages and does not persist stale `reference_reviews[]` from the same payload.

### Current-State Guidance

Guidance should not show old payload JSON as examples. It may describe forbidden field principles without preserving full old payload shapes.

### Bytecode

Compiled Python bytecode is not part of the skill package and should be removed from the working tree. Tests should prevent it from reappearing under `literature-analysis`.
