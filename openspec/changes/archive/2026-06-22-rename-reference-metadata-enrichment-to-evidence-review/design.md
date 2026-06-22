## Design Notes

- The second `persist_references` submit round remains the reference metadata round, but the agent-facing name is Reference Metadata Evidence Review.
- Subagents must use only batch-local evidence: `locked_reference`, `existing_metadata`, `metadata_context_text`, and raw/source text present in the batch JSON.
- Runtime validates exact-evidence fields such as DOI, URL, archiveID, ISBN, ISSN, pages, volume, and issue.
- Publication/container names can still be extracted from visible context, but external lookup is forbidden.
- Existing internal SQLite tables and deterministic handler names are not renamed in this change to avoid broad migration risk.

## Non-Goals

- No new CLI command.
- No change to final `references.json`.
- No network lookup or automatic external metadata discovery.
