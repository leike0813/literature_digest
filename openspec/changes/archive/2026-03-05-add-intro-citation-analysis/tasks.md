# Tasks: Add Introduction-Scoped Citation Analysis Artifact

1. Create OpenSpec delta spec for `literature-digest` documenting:
   - new `citation_analysis_path` output key,
   - `citation_analysis.json` schema,
   - Introduction-only scope definition,
   - numeric + author-year requirements and mapping rules.
2. Update `literature-digest/SKILL.md`:
   - stdout keys: add `md_path/language/citation_analysis_path`,
   - add “Citation Analysis（Introduction only）” section with templates and constraints,
   - include `citation_analysis.json` in file materialization rules.
3. Update deterministic validator:
   - `literature-digest/scripts/validate_output.py`
   - remove legacy required keys and add citation analysis materialization + validation + scope consistency check.
4. Update tests:
   - `tests/test_validate_output.py` for new required keys and citation analysis file.
5. Update Skill-Runner assets:
   - `literature-digest/assets/output.schema.json` add fields and required list,
   - `literature-digest/assets/runner.json` prompt update,
   - `literature-digest/assets/skill-runner_file_protocol.md` add artifact field example.
6. Docs sync:
   - `docs/dev_paper_digest_skill.md`
   - `docs/dev_overview.md`
   - `literature-digest/README.md`
7. Verification:
   - run `unittest` + `mypy` under `DataProcessing` conda env.

