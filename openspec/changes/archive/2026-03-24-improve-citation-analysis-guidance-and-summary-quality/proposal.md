# Proposal: improve-citation-analysis-guidance-and-summary-quality

## Why

Stage 5 citation analysis is still too easy for weak models to satisfy with generic, repetitive prose. In practice this produces summaries that only count citation categories or repeat the same template sentence, which wastes the semantic-analysis phase and weakens the final artifact.

## What Changes

- Strengthen the stage-5 semantic payload so each citation item must include:
  - `topic`
  - `usage`
  - `is_key_reference`
- Strengthen the global citation summary payload so `basis` is required and must include:
  - `research_threads`
  - `argument_shape`
  - `key_ref_indexes`
- Keep `report_md` renderer-derived only; the agent still cannot write it directly.
- Update stage-5 guidance in `SKILL.md`, `step_05_citation_pipeline.md`, and `stage_runtime_interface.md` so weak models are instructed to explain how the source paper uses cited work, not merely what category it belongs to.
- Render a small “Key References” section from the structured summary basis.

## Impact

- Public file names and stdout top-level fields stay unchanged.
- `citation_analysis.json.items[]` may now expose additional optional fields:
  - `topic`
  - `usage`
  - `is_key_reference`
- Internal stage-5 payload contracts become stricter and intentionally reject the old under-specified forms.
