# Change: Add Reference Metadata Enrichment Stage

## Summary

Add a dedicated Stage 4 reference metadata enrichment step after core reference rows and reference quality review are complete. This keeps deterministic preprocessing focused on reference row preparation and moves optional Zotero-like metadata completion into a DB-backed agent enrichment workset.

## Motivation

Optional metadata such as venue, pages, DOI, URL, publisher, and identifiers is useful in `references.json`, but asking the same `persist_references` payload to finalize core rows and rich metadata creates a workflow bottleneck. The preprocessor should not become a full bibliographic parser, and missing optional metadata should not be routed through title quality review.

## Scope

- Add `prepare_reference_metadata_enrichment` and `persist_reference_metadata_enrichment`.
- Require normal reference extraction runs to complete enrichment before Stage 5 citation workset preparation.
- Keep reference-free abandoned runs on the existing Stage 5 path without enrichment.
- Use a single-writer subagent pattern: subagents may draft enrichment fragments, but only the main agent submits the merged DB write.
- Preserve the existing `references.json` array structure.

## Out Of Scope

- No multi-writer SQLite/gate concurrency.
- No deterministic rich metadata parser in `prepare_references_workset`.
- No changes to `literature-digest-lite`.
