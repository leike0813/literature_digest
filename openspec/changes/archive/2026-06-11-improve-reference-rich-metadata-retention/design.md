# Design: Reference Rich Metadata Retention

## Runtime Pass-Through

`persist_references` treats the following payload top-level fields as allowed rich reference metadata:

- `publicationTitle`, `conferenceName`, `archiveID`, `university`
- `volume`, `issue`, `pages`, `numPages`
- `DOI`, `url`
- `publisher`, `place`, `ISBN`, `ISSN`

Non-empty values are copied into `reference_items.metadata_json`. Existing `fetch_reference_items()` behavior expands metadata back into top-level rendered references, so `references.json` retains these fields without schema changes. Empty strings, `null`, empty arrays, and empty objects are ignored. Top-level `doi` remains migrated to `DOI`; `citationKey` is not persisted.

## Soft Quality Guidance

The Stage 4 classifier adds warning reason `rich_metadata_evidence_missing` when raw text contains obvious evidence for a rich field but the normalized item lacks that field. Initial evidence detection is conservative:

- DOI and URL patterns.
- arXiv/archive identifiers.
- `pages` / `pp.` evidence.
- `vol.` / `volume` evidence.
- `no.` / `issue` evidence.
- `In <venue>` / `In: <venue>` evidence.
- `University` evidence.

Warnings use existing `reference_quality_issues` and `review_reference_quality`. The agent can correct rows by adding fields, or explicitly `accept_warning` when the evidence is unreliable.

## Guidance

Stage 4 examples should show rich metadata fields in normal `persist_references` payloads. Minimum-only examples remain valid only when raw evidence does not contain clear optional metadata.
