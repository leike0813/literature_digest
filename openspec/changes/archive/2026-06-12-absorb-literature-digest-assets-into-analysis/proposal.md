## Why

The first `literature-analysis` phase created a compatible wrapper, but the skill is still too thin to be useful as a direct replacement path. It lacks the old skill's detailed operational guidance and still depends on subprocess calls into `literature-digest` for deterministic runtime work.

This change starts the actual absorption: move reusable instructions into the new skill's own references and move core deterministic algorithms behind local `analysis_runtime` modules.

## What Changes

- Add `literature-analysis/references/` with rewritten, decision-oriented guidance.
- Update `literature-analysis/SKILL.md` to index the new references without becoming a long document.
- Add `literature-analysis/scripts/analysis_runtime/` modules for DB setup, source normalization, reference workset preparation, citation workset preparation, rendering fallback, and legacy loading.
- Update `run_analysis.py` so initialization, reference prepare, and citation prepare use local modules instead of subprocess calls to old `stage_runtime.py`.
- Keep old `literature-digest` unchanged.

## Capabilities

### Modified Capabilities

- `literature-analysis`: gains its own instruction corpus and local runtime modules while preserving the full compatible output contract.

## Impact

- **Code impact**: Adds new references and runtime modules under `literature-analysis/`.
- **Compatibility impact**: Existing stdout and artifact compatibility remains unchanged.
- **Risk**: Some local modules still call imported legacy functions internally. This removes subprocess coupling first; deeper code copying can continue in later changes.
