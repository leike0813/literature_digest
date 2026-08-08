## Context

`literature-analysis` is an automation-facing Tier-6 SQLite state-machine Skill. `run_analysis.py` is the public stage wrapper, SQLite is the process source of truth, and final artifacts are runtime-rendered. The current wrapper routes `persist_digest` directly to reference preparation and the full renderer assumes digest, reference, citation, and matching data all exist. Detailed semantic guidance lives in stage references while `SKILL.md` carries the minimum complete executable contract.

The scoring capability is holistic semantic judgment over the normalized paper. It must remain source-grounded, must not be replaced by deterministic keyword rules, and must produce a stable machine-readable artifact in both full and score-only runs.

## Goals / Non-Goals

**Goals:**

- Add scoring without creating a second orchestration path or a second scoring source of truth.
- Keep all semantic assessment with the agent and all validation, arithmetic, persistence, routing, and rendering with scripts.
- Make full and score-only runs recoverable from SQLite and self-consistent after context loss.
- Preserve existing Skill instructions verbatim except where the new flow requires a direct edit.

**Non-Goals:**

- Configurable dimensions, weights, score scales, or user-authored rubrics.
- External lookup, citation metrics, venue ranking, author reputation, or fact-checking against outside sources.
- A Markdown score report or subagent-per-dimension scoring.
- Reworking existing reference/citation semantics or cleaning unrelated documentation drift.

## Decisions

### 1. Use one canonical rubric asset and one per-run snapshot

`assets/scoring_rubric.json` owns dimension order, weights, criterion keys, display names, and maximum points. Initialization copies it into the runtime temporary directory and stores the snapshot path in SQLite, matching the existing runtime-template pattern. The scoring reference explains semantic interpretation but does not become executable configuration.

This avoids hard-coded numeric copies across scoring logic, templates, and prompts while ensuring a resumed run cannot silently switch rubric mid-execution.

### 2. Store one normalized computed score document

SQLite gains a single-row `literature_score` table with `rubric_id`, `content_json`, and `updated_at`. `content_json` holds the normalized assessment plus script-derived fields and is the render source.

A more normalized criterion-per-row design would support ad hoc SQL analysis but adds joins, ordering rules, and partial-write states without a current consumer. Keeping the small assessment atomic is safer and simpler.

### 3. Put score-specific behavior in `analysis_runtime/scoring.py`

The new module owns rubric loading, JIT context creation, payload coverage/type/range validation, source evidence validation, N/A normalization, decimal calculation, DB persistence, score rendering, and score-only completion. Existing orchestration modules only route to this cohesive interface. `deterministic_core.py` receives the minimum integration edits for its existing state, receipt, render, and output validators; scoring semantics do not enter that monolith.

### 4. Use a prepare/submit interface

Calling `persist_literature_score` without a payload writes a small JIT context under `.literature_analysis_tmp/agent_work/` and returns paths rather than inlining the normalized paper or rubric. Calling it with `--payload-file` validates and persists the semantic decision.

This matches the existing path-oriented automation pattern, keeps stdout bounded, and lets the scoring reference focus on semantic technique rather than duplicating run-specific data.

### 5. Keep one public result shape across modes

`literature_score_path` becomes a required stdout key. In a full success all required artifact paths are populated. In score-only success only the score path is populated; the existing required artifact keys remain present as empty strings and the optional citation report key is absent. Failures leave every artifact path empty.

The runtime knows the persisted mode and performs mode-aware validation; no separate output schema or alternate result file is introduced.

### 6. Separate applicability from evidence confidence

Every canonical criterion remains present. `not_applicable` removes a criterion from its dimension denominator; weak or missing reporting is still a scored case and lowers the semantic confidence as appropriate. Whole-dimension N/A redistributes only that dimension's weight proportionally over active dimensions and emits a warning. The runtime derives all weights and totals, eliminating contradictory agent calculations.

### 7. Scoring order is a workflow contract, not a new reference dependency

Normal status routes digest to scoring and scoring to references. Reference preparation remains independently callable for its existing diagnostic/tests behavior, but full rendering requires score state and a scoring receipt. Score-only explicitly blocks unrelated semantic actions because those writes would contradict the selected mode.

### 8. Preserve `SKILL.md` by surgical edits

The main file receives only the new input/output fields, fixed artifact, reference route, scoring command, stage ordering, mode branch, and recovery requirements. Existing wording, sections, examples, and subagent instructions are not compressed, moved, or rewritten. Detailed scoring guidance is isolated in `references/paper_scoring.md`.

## Risks / Trade-offs

- **[Risk] Scores across different paper types may be less directly comparable after N/A renormalization.** → Persist paper type, every N/A decision, configured/effective weights, and confidence so consumers can interpret the number.
- **[Risk] Absence-of-reporting judgments cannot quote missing text.** → Allow empty evidence only with an explicit reason; use dimension confidence to represent uncertainty.
- **[Risk] Exact quote validation can be brittle after PDF normalization.** → Compare within declared normalized-source lines after limited whitespace normalization, not raw byte equality.
- **[Risk] Adding a required score path changes downstream expectations.** → Keep every existing key and use empty strings in score-only mode; update the schema, runner, core instruction, and tests together.
- **[Risk] Stage renumbering touches a large legacy runtime module.** → Keep arithmetic and semantic validation outside it, make string changes mechanical, and exercise receipt repair and both render modes in behavior tests.

## Migration Plan

1. Add rubric, score schema/template, scoring reference, and DB table APIs.
2. Add scoring module and its prepare/submit contract.
3. Integrate mode persistence, state routing, receipts, and render paths.
4. Update Skill/runner/schema contracts with surgical edits only.
5. Extend runtime tests and run strict OpenSpec validation.

Existing databases are migrated through `CREATE TABLE IF NOT EXISTS`. On resume, a run with downstream receipts but no score is routed to scoring before its next render. Rollback consists of reverting the change files; no external data or service migration is involved.
