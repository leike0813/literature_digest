# Change: Improve Reference Rich Metadata Retention

## Summary

Improve `literature-digest` Stage 4 so Zotero-like optional reference metadata submitted in `persist_references` is retained through DB persistence and final rendering, and add soft quality guidance when raw references visibly contain rich metadata evidence that the agent did not capture.

## Motivation

The reference contract allows optional fields such as `publicationTitle`, `conferenceName`, `DOI`, `url`, `pages`, and publisher/place identifiers. Current guidance mentions these fields, but the main `persist_references` path builds a normalized item from only the minimum fields plus `metadata`, so top-level optional fields in the agent payload are discarded. The most visible examples also show minimum-only payloads, which makes agents under-extract useful metadata.

## Scope

- Preserve allowed rich metadata fields from top-level `persist_references` payloads.
- Keep the fields optional and evidence-based; do not invent missing metadata.
- Add a soft warning when obvious raw evidence exists but corresponding rich fields are absent.
- Update Stage 4 command examples and docs to show rich metadata as the expected path when evidence exists.

## Out Of Scope

- No changes to `literature-digest-lite`.
- No new public artifact or `references.json` wrapper.
- No hard block for missing optional metadata.
- No external bibliographic lookup.
