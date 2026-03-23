## Context

`literature-digest` now has a DB-first runtime, but the operating contract still leaks across too many places. We need a sharper separation between:

- runtime truth and rendering,
- core instructions and detailed operational guidance,
- and gate decisions versus implementation examples.

This change tightens the runtime without changing the meaning of the public artifacts.

## Goals / Non-Goals

**Goals**
- Make final artifact rendering template-driven and schema-validated.
- Reduce `SKILL.md` to the minimum durable contract.
- Split step guidance into multiple targeted reference files.
- Make the gate payload more executable by attaching doc references and SQL examples.

**Non-Goals**
- Changing output filenames or public artifact meaning.
- Reintroducing hidden intermediate files.
- Expanding the public stdout schema beyond the already optional `citation_analysis_report_path`.

## Decisions

1. Template-driven rendering
- Decision: Store templates in `literature-digest/assets/templates/` and render-context schemas in `literature-digest/assets/render_schemas/`.
- Rationale: Runtime assets belong with the renderer, not with prose guidance docs.

2. Render context validation
- Decision: Build explicit render contexts from SQLite data and validate them before rendering.
- Rationale: Makes rendering failures crisp and keeps prompt/docs/scripts aligned.

3. Split reference docs by stage
- Decision: Replace one large step guide with multiple `references/step_*.md` files.
- Rationale: The gate should be able to point the agent at a narrow, relevant document instead of a monolith.

4. Gate references + SQL examples
- Decision: Add `instruction_refs` and `sql_examples` to every gate response.
- Rationale: The gate already decides the next action, so it should also point to the right doc and show the minimum safe SQL shape.

5. Minimal SQL examples only
- Decision: `sql_examples` are scoped to the current `next_action`, not the whole stage.
- Rationale: Avoid noisy payloads and keep the gate directive tight.

## Risks / Trade-offs

- Templated JSON rendering introduces another failure point if schemas or templates drift.
- Splitting docs increases file count and requires stronger cross-link discipline.
- Gate SQL examples can become stale if action semantics drift.

Mitigations:
- Validate render contexts with `jsonschema` and validate rendered JSON by parsing it back.
- Keep the split docs short and scoped, with the gate owning reference selection.
- Generate SQL examples from a single in-code mapping keyed by `next_action`.
