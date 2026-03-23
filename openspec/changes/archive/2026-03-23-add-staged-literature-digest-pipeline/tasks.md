## 1. OpenSpec and Skill Contract Updates

- [x] 1.1 Add the new change scaffold for `add-staged-literature-digest-pipeline`.
- [x] 1.2 Add delta specs for `literature-digest` and `citation-preprocess-pipeline`.
- [x] 1.3 Update `literature-digest/SKILL.md` with hidden staged artifacts, batching rules, atomic publish, and stage-level error codes.
- [x] 1.4 Update `literature-digest/assets/runner.json` so the prompt requires staged execution rather than one-shot generation.
- [x] 1.5 Update `docs/dev_paper_digest_skill.md` to document the staged internal pipeline while keeping the public contract unchanged.

## 2. References Staging Implementation

- [x] 2.1 Add `literature-digest/scripts/references_staging.py`.
- [x] 2.2 Implement references scope detection and entry splitting.
- [x] 2.3 Implement fixed-size part emission (`15` entries per part max).
- [x] 2.4 Implement deterministic merge and atomic publish for `references.json`.

## 3. Citation Staging Implementation

- [x] 3.1 Add `literature-digest/scripts/citation_staging.py`.
- [x] 3.2 Merge `citation.parts/part-*.json` deterministically into a single `citation_merged.json`.
- [x] 3.3 Enforce `mention_id` uniqueness, `ref_index` uniqueness, and mention-coverage equality against `citation_preprocess.json`.
- [x] 3.4 Require `report_md` aggregation to succeed before publishing `citation_analysis.json`.

## 4. Validation and Tests

- [x] 4.1 Extend `literature-digest/scripts/validate_output.py` with stage-aware error validation and staged artifact checks.
- [x] 4.2 Add `tests/test_references_staging.py`.
- [x] 4.3 Add `tests/test_citation_staging.py`.
- [x] 4.4 Extend `tests/test_validate_output.py` for stage error codes and publish behavior.
- [x] 4.5 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`.
- [x] 4.6 Run `conda run --no-capture-output -n DataProcessing pytest -q`.
