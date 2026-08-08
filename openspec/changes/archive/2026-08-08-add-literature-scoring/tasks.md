## 1. Scoring Contracts And Assets

- [x] 1.1 Add the canonical scoring rubric, score render template, and score render-context schema.
- [x] 1.2 Extend parameter, output, runner, and core-instruction assets for `score_only`, the scoring stage, and `literature_score_path`.

## 2. DB And Scoring Runtime

- [x] 2.1 Add DB persistence and public artifact-path support for the normalized literature score.
- [x] 2.2 Implement scoring prepare/submit, canonical coverage validation, source-evidence validation, N/A normalization, deterministic arithmetic, and score rendering in a cohesive scoring module.
- [x] 2.3 Persist per-run score template/rubric snapshots and the immutable `score_only` runtime input.

## 3. Workflow Integration

- [x] 3.1 Add the `persist_literature_score` CLI and mode guards to `run_analysis.py`.
- [x] 3.2 Integrate scoring into stages, gate/status guidance, workflow state, receipts, recovery, and mode-aware render prerequisites.
- [x] 3.3 Ensure full finalization includes the score artifact and score-only finalization emits the stable sparse output shape and result mirror.

## 4. Skill Guidance

- [x] 4.1 Add the detailed paper-scoring reference with rubric semantics, evidence guidance, N/A handling, confidence calibration, examples, and failure recovery.
- [x] 4.2 Surgically update `SKILL.md` and affected existing stage references without compressing or rewriting unrelated instructions.
- [x] 4.3 Update project-level `AGENTS.md` only where the current literature-analysis runtime, scoring input, and output contracts require it.

## 5. Verification

- [x] 5.1 Extend runtime behavior tests for full scoring, score-only runs, formulas, validation failures, state recovery, rendering, and artifact paths.
- [x] 5.2 Remove only the obsolete fixed-stage-heading guidance assertion and keep scoring prose out of static instruction tests.
- [x] 5.3 Run the focused unittest suites, strict OpenSpec validation, and `git diff --check`; fix all in-scope failures.
