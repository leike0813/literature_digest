## 1. OpenSpec Traceability

- [x] 1.1 Add the new change scaffold for `consolidate-stage-runtime-scripts`.
- [x] 1.2 Add delta specs for `literature-digest` and `sqlite-gated-skill-runtime`.
- [x] 1.3 Record this change as an already-implemented runtime consolidation rather than a future plan.

## 2. Runtime Consolidation

- [x] 2.1 Add `literature-digest/scripts/stage_runtime.py` as the unified stage-action entrypoint.
- [x] 2.2 Remove the old standalone runtime entry scripts without compatibility wrappers.
- [x] 2.3 Update `literature-digest/scripts/gate_runtime.py` so `next_action` maps directly to `stage_runtime.py` subcommands.
- [x] 2.4 Keep `literature-digest/scripts/runtime_db.py` as the shared DB/query helper layer.

## 3. Guidance and Runner Alignment

- [x] 3.1 Update `literature-digest/SKILL.md` and `literature-digest/assets/runner.json` to the three-layer runtime model.
- [x] 3.2 Update `literature-digest/references/*.md` and `docs/dev_paper_digest_skill.md` to describe `gate_runtime.py` / `stage_runtime.py` / `runtime_db.py`.
- [x] 3.3 Add runtime interface docs for `gate_runtime.py` and `stage_runtime.py`.

## 4. Tests and Verification

- [x] 4.1 Add `tests/test_stage_runtime.py` and migrate affected runtime tests to the unified entrypoint.
- [x] 4.2 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`.
- [x] 4.3 Run `conda run --no-capture-output -n DataProcessing pytest -q`.
