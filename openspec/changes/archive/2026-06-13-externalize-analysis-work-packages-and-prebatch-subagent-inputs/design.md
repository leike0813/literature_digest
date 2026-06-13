## Design Notes

- Batch files are agent-facing inputs, not public artifacts. They live in the runtime tmp directory and may be regenerated.
- Existing `workset_path` and `review_path` remain audit sidecars; they are not subagent delegation boundaries.
- Manifests expose coverage keys, batch paths, merge contract, subagent policy, and payload submit shape.
- Batch files include the package subset, allowed enum subset, required return shape, forbidden fields, subagent prompt, merge notes, and suggested draft output path.
- Batch size is fixed at 10 for reference core review, metadata enrichment, and citation semantic review.

## Non-Goals

- No change to `reference_reviews[]`, `metadata_reviews[]`, or `citation_semantic_reviews[]` submit payloads.
- No new CLI stage.
- No change to final public artifact schema.
- No attempt to automate subagent execution from runtime.
