## Why

`citation_analysis` quality is currently inconsistent: citation recall is low and semantic summaries are often generic. This limits its usefulness for literature review drafting, even when using strong reasoning models.

## What Changes

- Define a strict multi-stage citation workflow in `literature-digest/SKILL.md`:
- Add deterministic preprocess stage for `citation_scope` citation extraction before semantic analysis.
- Define `citation_scope` as a single scope-definition object (not dual `review_scopes + analysis_scope` output), while allowing coverage across multiple review chapters (e.g., `Introduction + Related Works`).
- Require child-subsection coverage when a parent review chapter is selected; treat under-coverage as invalid scope.
- Add explicit semantic-task instructions after preprocess (mapping policy, evidence usage, summarization rules).
- Add coverage gate and fallback rules to avoid silently dropping mentions.
- Define fixed temporary artifact location as `<cwd>/.literature_digest_tmp/` and keep generated temporary files by default.
- Allow skill-packaged deterministic helper scripts for preprocessing while keeping the no-runtime-script-generation rule.
- Keep output schema unchanged and do not modify `literature-digest/assets/runner.json`.

## Capabilities

### New Capabilities
- `citation-preprocess-pipeline`: Deterministic preprocessing contract and mention-accounting gate for citation analysis.

### Modified Capabilities
- `literature-digest`: Tighten citation-analysis workflow requirements, fallback behavior, and temporary artifact policy.

## Impact

- Affected docs:
- `literature-digest/SKILL.md`
- `openspec/specs/literature-digest/spec.md` (delta)
- New helper script expected:
- `literature-digest/scripts/citation_preprocess.py`
- Optional validator/test alignment:
- `literature-digest/scripts/validate_output.py`
- `tests/test_validate_output.py`
- `tests/test_citation_preprocess.py`
