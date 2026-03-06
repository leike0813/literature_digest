## 1. OpenSpec and Skill Contract Updates

- [x] 1.1 Update `literature-digest/SKILL.md` to define mandatory multi-stage citation workflow.
- [x] 1.2 Define `citation_scope` as a single scope-definition object (no dual `review_scopes + analysis_scope` output), while allowing multi-chapter coverage.
- [x] 1.3 Add explicit scope-quality constraints in `SKILL.md` (parent chapter implies child-subsection coverage; under-coverage fallback).
- [x] 1.4 Add explicit post-preprocess semantic-task rules (mapping priorities, evidence constraints, summary rules).
- [x] 1.5 Add mention-accounting gate and boundary fallback matrix in `SKILL.md`.
- [x] 1.6 Update script-boundary language in `SKILL.md` so scope decision belongs to LLM/agent while packaged preprocess scripts remain allowed.

## 2. Deterministic Preprocess Implementation

- [x] 2.1 Implement `literature-digest/scripts/citation_preprocess.py` to extract normalized citation mentions within agent-provided `citation_scope`.
- [x] 2.2 Implement numeric citation normalization including range expansion.
- [x] 2.3 Implement author-year citation normalization including multi-cite splitting.
- [x] 2.4 Write preprocess artifacts to `<cwd>/.literature_digest_tmp/` with stable filenames and no auto-cleanup.

## 3. Citation Analysis Integration

- [x] 3.1 Integrate preprocess output consumption into citation-analysis generation flow.
- [x] 3.2 Enforce full mention accounting (`mapped + unmapped == extracted`) before success output.
- [x] 3.3 Ensure ambiguous/low-confidence mappings are routed to `unmapped_mentions` with reason codes.
- [x] 3.4 Keep output schema and artifact protocol unchanged (`citation_analysis_path` contract intact).

## 4. Validation and Tests

- [x] 4.1 Extend `tests/test_validate_output.py` with mention-accounting and boundary-case scenarios.
- [x] 4.2 Add `tests/test_citation_preprocess.py` for numeric and author-year extraction/normalization.
- [x] 4.3 Run `conda run --no-capture-output -n DataProcessing mypy literature-digest/scripts`.
- [x] 4.4 Run `conda run --no-capture-output -n DataProcessing pytest -q`.
