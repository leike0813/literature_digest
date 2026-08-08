## 1. Review Form Contract

- [x] 1.1 Extend the canonical rubric with paper-type choices and dimension/criterion prompts, and generate complete locked original and editable draft forms from that single source.
- [x] 1.2 Derive stable source/rubric-bound form identities and preserve an existing draft when prepare is repeated.

## 2. Runtime Validation And Conversion

- [x] 2.1 Validate form identity, locked fields, complete answers, paper-type selection, applicability, score ranges, reasons, summaries, and confidence with structured review reason codes.
- [x] 2.2 Locate evidence quotations with normalized exact matching and bounded n-gram fuzzy matching, derive line ranges, and report below-threshold candidates.
- [x] 2.3 Convert accepted review forms into the existing normalized score computation and persistence path without changing N/A weighting, formulas, SQLite state, or public output.

## 3. Agent-Facing Workflow

- [x] 3.1 Update scoring prepare/status output to return original/draft paths, editable fields, and the direct draft submit command without an expanded criterion payload shape.
- [x] 3.2 Update `SKILL.md`, scoring guidance, and core/runner guidance to describe only the generated-form workflow and current LLM/runtime responsibilities.

## 4. Verification

- [x] 4.1 Extend existing scoring behavior tests for rubric-driven generation, semantic-only submission, validation failures, draft reuse, stale forms, and exact/fuzzy evidence matching.
- [x] 4.2 Verify N/A formulas, full and score-only routing, and public `literature_score.v1` output remain unchanged.
- [x] 4.3 Run focused unittest, Ruff, strict OpenSpec validation, and scoped `git diff --check`; resolve all in-scope failures.
