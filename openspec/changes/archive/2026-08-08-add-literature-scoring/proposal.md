## Why

`literature-analysis` currently produces digest, reference, citation, and matching artifacts but cannot express a structured assessment of the paper itself. Adding a source-grounded scoring stage gives downstream automation an auditable quality signal while keeping assessment confidence separate from the observed scientific quality.

## What Changes

- Add a fixed six-dimension literature scoring rubric with criterion-level scores, evidence, rationales, dimension confidence, a weighted quality score, and a confidence-adjusted score.
- Add a DB-backed `persist_literature_score` stage between digest generation and reference extraction in the normal workflow.
- Add `score_only: boolean` so a run can normalize the source, score it, render only `literature_score.json`, and leave all other artifact paths empty.
- Add `literature_score_path` to the stable stdout/result contract and register the score artifact in SQLite.
- Keep the scoring judgment with the agent while making rubric validation, evidence checking, score calculation, persistence, rendering, and state transitions deterministic runtime responsibilities.
- Extend the current Skill instructions only where the new flow requires it; place detailed scoring semantics, examples, and techniques in a dedicated reference document.

## Capabilities

### New Capabilities

- `literature-scoring`: Defines the rubric, semantic assessment payload, evidence rules, N/A handling, deterministic formulas, and public score artifact.

### Modified Capabilities

- `literature-analysis`: Adds the scoring stage, `score_only` parameter, score artifact path, and mode-specific successful output behavior.
- `sqlite-gated-skill-runtime`: Adds score persistence, state transitions, receipts, recovery, and mode-aware rendering prerequisites.

## Impact

- Affects the `literature-analysis` Skill contract, stage references, runner metadata, parameter/output schemas, runtime CLI, SQLite schema, workflow state machine, renderer, and runtime tests.
- Adds one JSON artifact, one rubric asset, one render schema/template pair, one scoring runtime module, and one scoring reference document.
- Introduces no new dependency, network access, development server, Git history change, or external bibliographic lookup.
