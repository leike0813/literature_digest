## Context

The previous deep-absorption change made `literature-analysis/SKILL.md` much stronger, but the detailed reference files remained comparatively thin. The old reference corpus shows a consistent pattern:

- define the stage role and source of truth
- define payload shape and field semantics
- provide legal and illegal examples
- name validation failures and recovery choices
- distinguish DB/runtime truth from sidecar or rendered artifacts

The new reference files should preserve that pattern, rewritten for the six `literature-analysis` stages.

## Goals / Non-Goals

**Goals:**

- Deepen the five `literature-analysis/references/*.md` files.
- Keep the stage split aligned to `init_runtime`, `persist_analysis_plan`, `persist_digest`, `persist_references`, `persist_citation_analysis`, and `finalize_outputs`.
- Absorb old reference and citation quality rules, examples, failure semantics, and recovery checklists.
- Add tests for stable semantic anchors.

**Non-Goals:**

- Do not change runtime scripts or algorithms.
- Do not modify old `literature-digest`.
- Do not expose old SQL or gate playbooks as normal `literature-analysis` instructions.
- Do not re-expand the workflow into the old 18 runtime actions.

## Decisions

### Decision 1: Stage manuals, not appendices

Each new reference file should be useful on its own after the agent has read `SKILL.md`. It should state what the stage reads, what it writes, what the payload looks like, common legal/illegal shapes, and failure/recovery rules.

### Decision 2: Keep old rules as anchors, rewrite old control flow

Rules such as `placeholder_title`, `reference_author_refinement_invalid`, `citation_false_positive_filtered`, timeline closure, and `report_md` derivation are durable and should be preserved. Old gate-loop sequencing and SQL playbooks should not be copied into the normal instructions.

### Decision 3: Tests assert concepts, not prose

Guidance tests should check stable terms, examples, and forbidden old-main-path strings. They should not assert complete paragraphs or full snapshots.

## Risks

- The reference files become longer. This is acceptable because they are loaded stage-by-stage.
- Some old phrasing may accidentally reintroduce old script commands. Tests guard against direct old script paths and old gate-only main-path strings.
