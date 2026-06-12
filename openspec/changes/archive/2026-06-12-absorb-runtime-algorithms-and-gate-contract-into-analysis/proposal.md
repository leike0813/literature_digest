## Why

`literature-analysis` now has a strong instruction contract, but its runtime still treats the old `literature-digest` stage CLI as the execution backend for several normal-path submits. That keeps behavior compatible, but it prevents the new skill from owning its runtime boundary.

This change starts runtime ownership by removing normal-path subprocess calls, moving stage operations behind local `analysis_runtime` modules, and absorbing the useful gate contract as local status guidance.

## What Changes

- Add local runtime modules for plan persistence, digest persistence, gate/status contract, and direct stage handler adaptation.
- Update `run_analysis.py` so each public command calls `analysis_runtime` modules instead of `_run_legacy` subprocesses.
- Keep imported legacy function fallback explicit and audited for algorithms not yet fully copied.
- Extend tests to prove normal submit paths do not call `_run_legacy` subprocesses and that status uses local instruction refs.
- Keep old `literature-digest` unchanged.

## Capabilities

### Modified Capabilities

- `literature-analysis`: owns the normal CLI orchestration and gate/status guidance while preserving compatible outputs.

## Impact

- **Runtime impact**: normal `literature-analysis` paths no longer shell out to old `stage_runtime.py`.
- **Compatibility impact**: public commands and artifacts remain unchanged.
- **Migration impact**: deterministic algorithms may still be reached through imported legacy function fallback in this phase; later changes can copy those algorithms into local modules.
