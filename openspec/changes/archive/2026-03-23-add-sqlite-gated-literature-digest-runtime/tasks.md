## 1. OpenSpec and Contract Updates

- [x] 1.1 Add the new change scaffold for `add-sqlite-gated-literature-digest-runtime`.
- [x] 1.2 Add delta specs for `literature-digest`, `citation-preprocess-pipeline`, and `sqlite-gated-skill-runtime`.
- [x] 1.3 Update `literature-digest/assets/output.schema.json` with optional `citation_analysis_report_path`.
- [x] 1.4 Update `literature-digest/assets/runner.json` for the DB+gate runtime flow.
- [x] 1.5 Update `literature-digest/SKILL.md` and `docs/dev_paper_digest_skill.md` to document SQLite SSOT and gate discipline.

## 2. Runtime DB and Gate

- [x] 2.1 Add `literature-digest/scripts/runtime_db.py`.
- [x] 2.2 Add `literature-digest/scripts/init_runtime_db.py`.
- [x] 2.3 Add `literature-digest/scripts/gate_runtime.py`.
- [x] 2.4 Add `literature-digest/scripts/render_final_artifacts.py`.

## 3. Script Integration

- [x] 3.1 Extend `dispatch_source.py` to optionally persist normalized source data into the runtime DB.
- [x] 3.2 Extend `citation_preprocess.py` to optionally persist mention data into the runtime DB.
- [x] 3.3 Extend `validate_output.py` to accept optional `citation_analysis_report_path` and DB-backed consistency checks.

## 4. Tests and Verification

- [x] 4.1 Add runtime DB tests.
- [x] 4.2 Add gate runtime tests.
- [x] 4.3 Add final artifact renderer tests.
- [x] 4.4 Update validator tests for optional `citation_analysis_report_path`.
- [x] 4.5 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`.
- [x] 4.6 Run `conda run --no-capture-output -n DataProcessing pytest -q`.
