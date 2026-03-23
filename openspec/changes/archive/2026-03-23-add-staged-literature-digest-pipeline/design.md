## Context

The existing skill already writes final public artifacts to the source directory and already uses deterministic helper scripts for normalization and validation. The missing piece is a staged workflow for the two long-running semantic outputs:

- `references.json`
- `citation_analysis.json`

The design keeps the external contract stable and only changes internal workflow, temporary artifacts, and validation policy.

Constraints:
- Do not change `output.schema.json`.
- Do not modify server/runtime timeout behavior.
- Keep the workflow fully non-interactive.
- Preserve strict failure semantics.

## Goals / Non-Goals

**Goals:**
- Prevent long silent single-round generation for references and citation analysis.
- Make intermediate progress explicit through hidden staged artifacts.
- Publish final public artifacts only after deterministic merge and validation succeed.
- Provide stage-specific failure codes.

**Non-Goals:**
- Changing public output file names.
- Adding partial-success semantics.
- Moving orchestration into runtime/server code.

## Decisions

1. Hidden temporary artifact directory
- Decision: All staged internal artifacts live under `<cwd>/.literature_digest_tmp/`.
- Rationale: Keeps debugging material local to the skill and out of the public artifact contract.
- Temporary artifact set:
  - `outline.json`
  - `references_scope.json`
  - `references.parts/part-*.json`
  - `references_merged.json`
  - `citation_scope.json`
  - `citation_preprocess.json`
  - `citation.parts/part-*.json`
  - `citation_merged.json`
  - `citation_report.md`

2. References batching
- Decision: References are split by detected entries, not by raw character size.
- Batch rule:
  - max `15` reference entries per part
  - one extremely long entry may occupy a batch alone
  - merged order follows the original references order
- Rationale: Entry-level batching is stable, auditable, and independent of prose length.

3. Citation three-stage workflow
- Decision: Citation analysis is decomposed into:
  1. `citation_scope.json`
  2. `citation_preprocess.json` plus semantic part files
  3. final `report_md` aggregation
- Part batching rule:
  - max `12` grouped citation items per part
  - or max `30` mentions per part
  - whichever limit is hit first
- Rationale: Separates scope choice, deterministic extraction, and semantic summarization into bounded steps.

4. Deterministic merge and gate checks
- Decision: Final citation merge enforces:
  - globally unique `mention_id`
  - one final item per `ref_index`
  - total consumed mentions equals `citation_preprocess.json stats.total_mentions`
- Decision: Final references merge enforces schema-valid arrays and preserves part order by part number.
- Rationale: Merge is the final correctness gate before publish.

5. Atomic publish
- Decision: `digest.md` may still be written directly, but `references.json` and `citation_analysis.json` are published only after merge validation succeeds, using `os.replace`.
- Rationale: Prevents callers from observing half-written public artifacts.

6. Stage-level error codes
- Decision: Final schema-compatible failures must use these codes when applicable:
  - `references_stage_failed`
  - `references_merge_failed`
  - `citation_scope_failed`
  - `citation_semantics_failed`
  - `citation_report_failed`
  - `citation_merge_failed`
- Rationale: Callers need to distinguish failure stage without changing the public schema.

## Risks / Trade-offs

- More stages mean more files and more orchestration complexity.
- Deterministic batching cannot solve semantic extraction quality by itself.
- Strict merge gates may increase failure rate initially, but that is preferable to publishing false-success artifacts.

Mitigations:
- Keep helper scripts narrow and deterministic.
- Keep stage outputs retained for diagnosis.
- Cover merge behavior with focused unit tests.
