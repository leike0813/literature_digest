## Context

The previous changes created a local runtime fork and removed cross-skill calls. The current package still has migration-era names and several one-function files:

- `db.py` contains runtime initialization rather than low-level DB access.
- `runtime_db.py` contains the real SQLite API.
- `algorithm_core.py` is a large vendored deterministic runtime.
- `local_handlers.py` adapts deterministic handlers.
- `source.py`, `plan.py`, `digest.py`, and `rendering.py` are thin public-stage wrappers.

## Goals / Non-Goals

**Goals:**

- Make file names accurately describe responsibilities.
- Collapse thin wrapper modules where doing so improves readability.
- Preserve all public behavior.
- Keep the change small enough to validate with existing runtime tests.

**Non-Goals:**

- Do not split the 7000-line deterministic algorithm fork.
- Do not split the SQLite access module.
- Do not redesign rendering, references, or citation algorithms.
- Do not modify old `literature-digest`.

## Decisions

### Decision 1: `stages.py` owns simple public stage wrappers

The simple wrappers for source normalization, plan persistence, digest persistence, and final rendering are grouped in `stages.py`. References and citations stay separate because they contain domain-specific workset enrichment and merge orchestration.

### Decision 2: Internal module names are not public API

Only `scripts/run_analysis.py` CLI and `scripts/runtime_db.py` compatibility entrypoint are public. Internal imports can be renamed freely as long as tests continue to cover behavior and package shape.

### Decision 3: Preserve deterministic core intact

The large vendored algorithm module is renamed but not split. This avoids mixing structural cleanup with behavioral refactoring.

## Risks

- Import rewrites can miss one reference. `py_compile` and runtime wrapper tests should catch this quickly.
- Tests that assert exact internal alias names need updating to assert the new intended package shape instead of migration-era names.
