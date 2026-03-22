## Why

`literature-digest` currently tends to enter a long silent phase after `digest.md` is produced. The most expensive work happens while generating `references.json` and `citation_analysis.json`, and that single long semantic round can exceed downstream SSE idle timeout expectations.

The public output contract is already correct and downstream consumers depend on it. The problem is not the schema; it is the lack of staged internal progress and atomic publish semantics.

## What Changes

- Add an internal staged pipeline for `literature-digest` while keeping the public output schema unchanged.
- Introduce hidden intermediate artifacts under `<cwd>/.literature_digest_tmp/`.
- Split references generation into entry-batched parts with deterministic merge and atomic final publish.
- Split citation analysis into `citation_scope` decision, preprocess-driven semantic parts, and final `report_md` aggregation.
- Add stage-level failure codes so callers can distinguish references-stage, merge-stage, citation-scope, citation-semantics, citation-report, and citation-merge failures.
- Update runner instructions, skill documentation, validators, and helper scripts to reflect the staged workflow.

## Capabilities

### Modified Capabilities
- `literature-digest`
- `citation-preprocess-pipeline`

## Impact

- Affected docs:
  - `literature-digest/SKILL.md`
  - `docs/dev_paper_digest_skill.md`
  - `literature-digest/assets/runner.json`
- New helper scripts:
  - `literature-digest/scripts/references_staging.py`
  - `literature-digest/scripts/citation_staging.py`
- Updated validation/tests:
  - `literature-digest/scripts/validate_output.py`
  - `tests/test_references_staging.py`
  - `tests/test_citation_staging.py`
  - `tests/test_validate_output.py`
