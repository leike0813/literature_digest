## Context

The previous runtime-ownership change removed subprocess calls to the old stage CLI, but it intentionally kept an imported-function fallback in `analysis_runtime.legacy` and `analysis_runtime.stage_adapter`. Current `source`, `plan`, `digest`, `references`, `citations`, `rendering`, `db`, and `gate_contract` still depend on those shims either directly or indirectly.

The user now requires a strict boundary: `literature-analysis` must not call across skill packages.

## Goals / Non-Goals

**Goals:**

- Remove all runtime imports, dynamic loads, and asset reads from `literature-digest`.
- Keep the existing `run_analysis.py` command surface unchanged.
- Preserve compatible SQLite state and public output artifacts.
- Localize templates and render schemas under `literature-analysis/assets`.
- Add static tests that make the boundary enforceable.

**Non-Goals:**

- Do not modify old `literature-digest`.
- Do not redesign the SQLite schema in this change.
- Do not restore the old gate loop.
- Do not extract a global shared module yet.

## Decisions

### Decision 1: Local fork first, finer domain splitting later

The old deterministic runtime is large and already covered by tests. This change vendors it as local `literature-analysis` code first, then routes the existing domain modules through that local code. That minimizes behavioral risk while satisfying the no-cross-skill boundary.

### Decision 2: Keep public stages coarse

`literature-analysis` continues to expose six agent-facing stages. Internally, local algorithms may retain old private helper names for compatibility, but public commands remain `init_runtime`, `persist_analysis_plan`, `persist_digest`, `persist_references`, `persist_citation_analysis`, `finalize_outputs`, and `status`.

### Decision 3: Assets are runtime dependencies

Templates and render schemas are copied into `literature-analysis/assets`. Rendering must resolve assets from the new skill directory or runtime tmp templates only.

## Risks

- Vendoring creates duplicated algorithm code. This is accepted for now because the immediate requirement is runtime independence.
- Static scans can be too broad if they include docs. The hard no-cross-skill test targets `literature-analysis/scripts/**`, where runtime execution happens.
