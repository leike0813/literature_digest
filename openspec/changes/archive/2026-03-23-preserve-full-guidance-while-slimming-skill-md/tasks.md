## 1. OpenSpec and Contract Updates

- [x] 1.1 Add the new change scaffold for `preserve-full-guidance-while-slimming-skill-md`.
- [x] 1.2 Add delta specs for `literature-digest` and `sqlite-gated-skill-runtime`.
- [x] 1.3 Update runner and guidance docs so `SKILL.md` is concise but external docs remain full fidelity.

## 2. Guidance Preservation

- [x] 2.1 Build a migration map from the long-form `SKILL.md` into the refactored docs.
- [x] 2.2 Expand `references/step_*.md` with the original detailed guidance instead of summaries.
- [x] 2.3 Expand `references/rendering_contracts.md` and `references/sql_playbook.md` with preserved detail.
- [x] 2.4 Keep `SKILL.md` concise while adding a complete detailed-content index.

## 3. Templates and Runtime Navigation

- [x] 3.1 Expand template files so original template intent is preserved without changing output semantics.
- [x] 3.2 Update gate/runner wording to reference full-content docs rather than summary docs.

## 4. Tests and Verification

- [x] 4.1 Add tests that assert key long-form guidance still exists somewhere in the refactored repo.
- [x] 4.2 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`.
- [x] 4.3 Run `conda run --no-capture-output -n DataProcessing pytest -q`.
