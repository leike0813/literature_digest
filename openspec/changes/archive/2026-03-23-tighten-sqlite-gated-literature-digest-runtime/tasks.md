## 1. OpenSpec and Runtime Contract

- [x] 1.1 Add the new change scaffold for `tighten-sqlite-gated-literature-digest-runtime`.
- [x] 1.2 Add delta specs for `literature-digest` and `sqlite-gated-skill-runtime`.
- [x] 1.3 Update `literature-digest/SKILL.md`, `literature-digest/assets/runner.json`, and `docs/dev_paper_digest_skill.md` for the slimmer contract + split reference docs model.

## 2. Templates and Render Schemas

- [x] 2.1 Add final artifact templates under `literature-digest/assets/templates/`.
- [x] 2.2 Add render-context schemas under `literature-digest/assets/render_schemas/`.
- [x] 2.3 Refactor `literature-digest/scripts/render_final_artifacts.py` to validate contexts and render through templates.

## 3. Gate and Reference Docs

- [x] 3.1 Split detailed execution guidance into `literature-digest/references/step_*.md` plus shared reference docs.
- [x] 3.2 Extend `literature-digest/scripts/gate_runtime.py` to emit `instruction_refs`.
- [x] 3.3 Extend `literature-digest/scripts/gate_runtime.py` to emit `sql_examples`.
- [x] 3.4 Add supporting runtime helpers in `literature-digest/scripts/runtime_db.py` as needed for rendering and gate payload assembly.

## 4. Tests and Verification

- [x] 4.1 Update runtime DB / gate / renderer tests for the new payload and templated rendering behavior.
- [x] 4.2 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`.
- [x] 4.3 Run `conda run --no-capture-output -n DataProcessing pytest -q`.
