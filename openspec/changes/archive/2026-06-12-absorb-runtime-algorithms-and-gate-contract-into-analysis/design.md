## Context

The current `literature-analysis/scripts/run_analysis.py` still has `_run_legacy`, which shells out to `literature-digest/scripts/stage_runtime.py` for plan, digest, reference submit, metadata enrichment, and citation submit. Prepare paths already use local facades, but those facades call imported legacy functions.

The old runtime is large, so copying every deterministic algorithm in one change is too risky. The first ownership step is to remove subprocess orchestration and make the local domain modules the normal interface.

## Goals / Non-Goals

**Goals:**

- Remove `_run_legacy` subprocess usage from the normal path.
- Add local modules for plan, digest, citation submit, reference submit, rendering, and gate/status contract.
- Make `status` return local instruction refs and useful next-action guidance.
- Keep public CLI and output contract compatible.

**Non-Goals:**

- Do not delete imported legacy fallback yet.
- Do not rewrite the full 7k-line old stage runtime in one change.
- Do not modify old `literature-digest`.
- Do not restore the old gate loop as the new skill workflow.

## Decisions

### Decision 1: Direct function fallback is allowed, subprocess fallback is not

This phase can call audited legacy functions through `analysis_runtime.legacy`, but `run_analysis.py` should not spawn the old stage CLI or load old runtime DB directly.

### Decision 2: Domain modules own command handlers

`run_analysis.py` should only parse CLI, read payload files, call domain modules, and print JSON. Domain modules own stage-specific persistence and validation orchestration.

### Decision 3: Gate semantics become status guidance

`gate_contract.py` produces `next_action`, `missing_prerequisites`, `execution_note`, `instruction_refs`, `quality_directives`, warnings, and error. It does not require agents to run a gate loop.

## Risks

- Direct function fallback still depends on old private functions. Tests document the allowed boundary and prevent a return to subprocess calls.
- Status guidance may be less complete than old gate output. It should cover the new six-stage workflow and can be expanded in later changes.
