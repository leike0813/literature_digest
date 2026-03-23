## Context

Before this consolidation, the DB-first runtime already had a clear conceptual structure:

- `gate_runtime.py` decided what to do next,
- SQLite stored process truth,
- and multiple small scripts performed deterministic stage work.

The problem was not capability coverage, but interface sprawl. The runtime exposed too many separate Python entrypoints for actions that the gate and state machine already treated as one staged workflow.

This change records the completed consolidation to a three-layer runtime:

- `gate_runtime.py`
- `stage_runtime.py`
- `runtime_db.py`

## Goals / Non-Goals

**Goals**
- Make `stage_runtime.py` the only stage-action CLI.
- Make `next_action` map directly to executable subcommands.
- Reduce duplicated helper logic across runtime scripts.
- Keep the public output contract unchanged.

**Non-Goals**
- Changing output filenames or stdout schema.
- Changing the SQLite schema shape beyond what the consolidation already reuses.
- Reintroducing compatibility wrappers for removed scripts.

## Decisions

1. Single stage-action entrypoint
- Decision: `stage_runtime.py` owns all deterministic stage actions.
- Rationale: The state machine already advances in stage units, so the executable surface should match that model.

2. Gate remains separate
- Decision: `gate_runtime.py` does not execute work and only emits `next_action`, `instruction_refs`, and `sql_examples`.
- Rationale: Keeps orchestration separate from mutation.

3. DB layer remains separate
- Decision: `runtime_db.py` remains the only shared persistence/query layer.
- Rationale: Prevents SQL duplication between gate and stage execution.

4. No wrapper compatibility
- Decision: Removed standalone scripts are not preserved as thin wrappers.
- Rationale: A wrapper layer would keep the old interface alive and weaken the consolidation.

5. Render + validate stays inside the stage runtime
- Decision: `render_and_validate` absorbs final rendering, public payload construction, and stdout contract checking.
- Rationale: Final publication is itself a stage action and should live in the unified stage executor.

## Subcommand Surface

The consolidated stage runtime exposes these subcommands:

- `bootstrap_runtime_db`
- `normalize_source`
- `persist_outline_and_scopes`
- `persist_digest`
- `persist_references`
- `prepare_citation_mentions`
- `persist_citation_semantics`
- `render_and_validate`

These are the canonical values for gate `next_action`.

## Risks / Trade-offs

- A larger unified script can become harder to navigate.
- Removing legacy CLIs means any stale internal docs/tests break immediately.
- `render_and_validate` now owns more responsibilities than the earlier split scripts.

Mitigations:

- Keep detailed interface docs in `references/gate_runtime_interface.md` and `references/stage_runtime_interface.md`.
- Keep `runtime_db.py` as the single shared helper layer to prevent internal duplication.
- Keep gate/state logic separate from stage execution logic.
