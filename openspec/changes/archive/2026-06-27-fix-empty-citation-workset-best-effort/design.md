## Context

The citation wrapper already normalizes missing or empty `citation_semantic_reviews` into an empty internal semantics payload. The lower-level deterministic handlers still gate on non-empty `citation_workset_items` and non-empty `citation_items`, which contradicts the intended best-effort behavior.

## Goals / Non-Goals

**Goals:**
- Complete citation semantics, timeline, summary, and rendering after a prepared empty workset.
- Preserve hard validation for unknown submitted ref indexes and unsafe fields.
- Preserve the distinction between “prepare never ran” and “prepare ran and found nothing stable.”

**Non-Goals:**
- Do not synthesize fallback citation items.
- Do not relax unknown-key or forbidden-field validation.
- Do not change public output schemas.

## Decisions

- Use action receipts as stage completion facts. `prepare_citation_workset` receipt proves the workset was prepared; `persist_citation_semantics` receipt proves an empty semantics result is intentional.
- Keep DB rows as render prerequisites for timeline and summary. Empty rows are valid; missing rows are still invalid.
- Leave reference-free mode behavior compatible with the same receipt-based checks.

## Risks / Trade-offs

- Empty citation artifacts can be produced for papers with extractor gaps -> warnings remain the audit surface.
- Agents may overuse empty payloads -> unknown/non-empty submitted keys still validate against workset items, and docs continue to say not to fabricate semantic content.
