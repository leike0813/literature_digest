## Why

Subagents have interpreted the reference metadata round as a discovery/enrichment task and used web search or external databases. That is too slow and outside the intended contract. The stage should be framed as local evidence review: extract only metadata supported by the runtime-provided batch JSON.

## What Changes

- Rename agent-facing reference metadata enrichment concepts to Reference Metadata Evidence Review.
- Replace `metadata_reviews[]` with `metadata_evidence_reviews[]` and replace old status values with local-evidence status values.
- Return `metadata_evidence_review_manifest_path` and `metadata_evidence_batch_paths`.
- Add explicit evidence policy to manifest and batch JSON files with `external_lookup_allowed=false`.
- Reject old `metadata_reviews[]` payloads and metadata values that lack local evidence for mechanically matchable fields.

## Impact

- Public CLI stages and final artifacts stay unchanged.
- Internal deterministic handler names may remain unchanged, but stdout, manifest, batch files, and skill guidance use current evidence-review terminology.
