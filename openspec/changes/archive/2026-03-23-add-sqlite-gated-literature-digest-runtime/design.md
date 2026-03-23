## Context

`literature-digest` currently relies on file-oriented staged helpers plus prompt discipline. That was sufficient for the first reliability pass, but it does not give us one auditable runtime truth or a strict execution gate.

This change upgrades the skill to a DB-first runtime while preserving downstream compatibility.

Constraints:
- keep the existing required stdout fields,
- add only one optional public field: `citation_analysis_report_path`,
- do not retain intermediate hidden artifacts,
- keep the runtime non-interactive,
- use SQLite from the standard library.

## Goals / Non-Goals

**Goals**
- Make SQLite the only runtime truth for process and payload data.
- Add a gate script that constrains stage/substep progression.
- Render final artifacts from DB state only.
- Keep external callers compatible.

**Non-Goals**
- Changing the meaning of `citation_analysis.json`.
- Adding a new mandatory stdout field.
- Moving orchestration into server/runtime infrastructure outside the skill.

## Decisions

1. SQLite as SSOT
- Decision: Store all runtime data under `<cwd>/.literature_digest_tmp/literature_digest.db`.
- Rationale: One durable, queryable truth for recovery, gating, and rendering.

2. No retained intermediate files
- Decision: Intermediate artifacts are stored as database rows only.
- Rationale: Avoid split-brain truth between DB and files.

3. Stage + substep state machine
- Decision: Use coarse stages with explicit substeps rather than one enum per tiny action.
- Rationale: Strong enough to constrain the agent without exploding schema complexity.

4. Gate script as the only legal next-step source
- Decision: `gate_runtime.py` is the only authoritative source of `next_action`.
- Rationale: Prevents the agent from skipping ahead based on memory.

5. Final render-only files
- Decision: Final files are rendered from DB state by `render_final_artifacts.py`.
- Rationale: Keeps public outputs deterministic and auditable.

6. Optional report path
- Decision: Add optional `citation_analysis_report_path` pointing to `citation_analysis.md`.
- Rationale: Exposes the human-readable report without changing `citation_analysis.json`.

## Risks / Trade-offs

- DB-first runtime increases implementation surface area.
- A strict gate can block flows that previously “sort of worked”.
- There is temporary duplication while legacy helper scripts remain alongside the new runtime modules.

Mitigations:
- Keep the DB schema narrow and explicit.
- Cover gate rules with focused unit tests.
- Keep legacy helpers functional while the runner switches to the new path.
