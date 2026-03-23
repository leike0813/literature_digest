## Context

The runtime already uses SQLite as SSOT for workflow state and most intermediate process data, but two final-content paths still behaved like “LLM fills in near-final text”:

- digest persistence stored section blocks that looked close to final markdown,
- citation semantics persistence accepted `report_md` directly from the agent.

This change closes that gap so the renderer consumes only structured DB content.

## Goals / Non-Goals

**Goals**

- Make final artifact rendering fully database-driven.
- Make digest storage structural instead of markdown-section based.
- Make citation report generation script-derived instead of LLM-written.
- Keep public output filenames and stdout schema unchanged.

**Non-Goals**

- Changing `references.json` structure.
- Preserving compatibility for old internal `sections[]` / `report_md` payloads.
- Supporting resumption of old in-progress databases created under the previous internal model.

## Decisions

1. Digest slots replace markdown sections
- Decision: `persist_digest` accepts `digest_slots + section_summaries`.
- Rationale: lets the renderer own headings, ordering, and final markdown formatting.

2. Citation report is renderer-derived
- Decision: `persist_citation_semantics` no longer accepts `report_md`.
- Rationale: `report_md` is final artifact content and should be generated from stored citation semantics, not injected as a ready-made string.

3. Same rendered string feeds JSON and Markdown citation outputs
- Decision: render the citation report once, inject it into `citation_analysis.json.report_md`, and write the same string to `citation_analysis.md`.
- Rationale: guarantees byte-for-byte equality between the two public outputs.

4. Direct cutover
- Decision: reject deprecated internal payload keys rather than silently converting them.
- Rationale: the new model is simpler and avoids shadow compatibility paths.

5. Step guidance follows DB truth, not text-generation flow
- Decision: `references/step_01` through `references/step_06` must describe the stage-local DB inputs, writes, and render responsibilities in the same terms as the runtime.
- Rationale: if the runtime is database-driven but the step docs still read like “LLM writes near-final text”, the operator guidance becomes internally contradictory.

## Data Model

### Digest

New active SSOT tables:

- `digest_slots`
  - `slot_key`
  - `content_json`
- `digest_section_summaries`
  - `position`
  - `source_heading`
  - `items_json`

Fixed digest slot keys:

- `tldr`
- `research_question_and_contributions`
- `method_highlights`
- `key_results`
- `limitations_and_reproducibility`

### Citation

Active citation SSOT remains:

- `section_scopes`
- `citation_mentions`
- `citation_batches`
- `citation_items`
- `citation_unmapped_mentions`

`citation_reports` is no longer an active SSOT input to publication.

## Rendering Flow

### Digest

1. Fetch `digest_slots`
2. Fetch `digest_section_summaries`
3. Validate against `digest.schema.json`
4. Render `digest.zh-CN.md.j2` or `digest.en-US.md.j2`

### Citation

1. Fetch `citation_items`, `citation_unmapped_mentions`, and `section_scopes.citation_scope`
2. Build structured report context
3. Validate against `citation_analysis_report.schema.json`
4. Render report markdown once
5. Inject the rendered string into the final citation JSON context
6. Validate citation JSON context
7. Render `citation_analysis.json`
8. Write the same rendered report string to `citation_analysis.md`

## Risks / Trade-offs

- Internal callers using old `sections[]` or `report_md` payloads now fail fast.
- Digest and citation rendering logic move more responsibility into Python templates and helper builders.

Mitigations:

- Keep the structured payload shape explicit in docs and tests.
- Make `stage_runtime.py` reject deprecated keys with clear error codes.
- Keep render-context schemas aligned with the new storage model.
