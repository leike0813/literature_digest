## Context

The existing `literature-digest` runtime contains useful deterministic capabilities:

- input detection and source normalization
- SQLite persistence helpers
- reference entry splitting and parse candidate generation
- citation mention extraction and workset generation
- public artifact rendering and validation

The new skill should reuse those mature pieces instead of rebuilding them. The architectural change is at the agent-facing workflow boundary: stages should align with semantic decisions, not with every runtime action needed to advance a state machine.

## Goals / Non-Goals

**Goals:**

- Add `literature-analysis` as an independent skill.
- Preserve full output compatibility with `literature-digest`.
- Keep SQLite as the auditable SSOT.
- Split `digest` and `references` into separate agent-facing stages.
- Collapse deterministic runtime-only chains behind fewer commands.
- Provide explicit subagent work package guidance for reference and citation batches.

**Non-Goals:**

- Do not replace, delete, proxy, or mark `literature-digest` as legacy.
- Do not extract a shared library in the first phase.
- Do not reimplement mature deterministic parsers or renderers.
- Do not solve every legacy gate edge case in the skeleton.

## Decisions

### Decision 1: Thin wrapper first

Use `literature-analysis/scripts/run_analysis.py` as a thin wrapper around `literature-digest/scripts/stage_runtime.py`.

Rationale:

- Reuses tested deterministic behavior immediately.
- Avoids copying large parser/render code.
- Keeps the first phase focused on workflow shape and compatibility.

### Decision 2: SQLite schema reuse in phase 1

Reuse the old runtime DB schema through the old `runtime_db.py` module.

Rationale:

- Existing render context builders expect that schema.
- It allows `finalize_outputs` to reuse old rendering without translating state.

### Decision 3: Agent decision stages

Expose these commands:

- `init_runtime`: confirms paths, bootstraps DB, persists render templates, normalizes source.
- `persist_analysis_plan`: persists outline, references scope, citation scope, and matching metadata.
- `persist_digest`: persists digest slots and section summaries only.
- `persist_references`: without payload prepares reference worksets; with payload persists reviewed references and completes default metadata enrichment if the caller does not provide enrichment items.
- `persist_citation_analysis`: without payload prepares citation worksets; with payload persists citation semantics/timeline/summary and automatically renders outputs.
- `finalize_outputs`: explicit compatibility render command for recovery or manual finalization.

### Decision 4: Subagent guidance is data, not scheduling

The runtime returns batch-oriented `subagent_prompt` guidance for reference and citation worksets, but it does not directly spawn subagents.

Rationale:

- Skill execution remains portable across agent frameworks.
- The main agent remains the only writer to SQLite.

## Risks / Trade-offs

- The first-phase wrapper still inherits some old DB receipt requirements. The new script hides the most mechanical chains but does not yet fully replace the old gate model.
- Default metadata enrichment in phase 1 may mark rows as `confirmed_existing` or `no_metadata_found` when no enrichment payload is provided. Later phases should make richer enrichment work packages the preferred path.
- Because the old renderer is reused, output compatibility is strong, but deeper schema simplification is deferred.
