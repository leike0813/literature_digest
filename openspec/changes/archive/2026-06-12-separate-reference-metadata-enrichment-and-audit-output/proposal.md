## Why

`literature-analysis` currently lets agents place rich metadata inside `reference_reviews[]`, which bypasses the metadata enrichment workset and weakens the intended separation between core reference parsing and metadata review. It also leaks internal parse audit fields such as `selected_pattern` and `pattern_candidate` into public `references.json`.

This change makes the reference stage stricter and cleaner: core bibliographic review, metadata enrichment, runtime audit, and public artifacts become separate layers.

## What Changes

- Split `persist_references` into two agent-facing submit rounds under the same CLI command: core `reference_reviews[]`, then metadata `metadata_reviews[]`.
- Reject `reference_reviews[].metadata` and require rich metadata through the metadata enrichment workset.
- Move `allowed_metadata_fields` and `locked_fields` to instruction-level payloads instead of repeating them per item.
- Remove parse/debug fields from public `references.json`.
- Add a runtime audit sidecar for parse choices and candidates.

## Capabilities

### New Capabilities

- `literature-analysis`: Separate reference core review, metadata enrichment, audit data, and public reference artifacts.

### Modified Capabilities

None.

## Impact

- **Public CLI**: unchanged command names.
- **Agent-facing payloads**: `reference_reviews[].metadata` is no longer accepted; `metadata_reviews[]` becomes the second required reference-stage submit round.
- **Public artifacts**: `references.json` no longer includes parse audit fields.
- **Runtime tmp artifacts**: new audit sidecar captures selected parse pattern and candidate details.
- **Old skill**: unchanged.
