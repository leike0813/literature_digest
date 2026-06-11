## ADDED Requirements

### Requirement: Preserve Optional Reference Metadata

`literature-digest` SHALL retain supported Zotero-like optional reference metadata submitted during Stage 4 reference persistence.

#### Scenario: Rich fields persist to rendered references

- **WHEN** `persist_references` receives supported top-level rich fields such as `publicationTitle`, `volume`, `issue`, `pages`, `DOI`, or `url`
- **THEN** the runtime SHALL persist those fields
- **AND** final `references.json` SHALL expose them on the corresponding reference object.

#### Scenario: Empty rich fields are ignored

- **WHEN** a supported rich field value is `null`, an empty string, an empty array, or an empty object
- **THEN** the runtime SHALL NOT write that field to the rendered reference.

#### Scenario: Citation key is not a public reference field

- **WHEN** `persist_references` receives `citationKey`
- **THEN** the runtime SHALL NOT expose `citationKey` in `references.json`.

### Requirement: Missing Rich Metadata Evidence Emits Soft Warning

`literature-digest` SHALL warn when a raw reference visibly contains rich metadata evidence that is absent from the structured item.

#### Scenario: Obvious DOI URL pages venue evidence requires review

- **WHEN** a raw reference contains obvious DOI, URL, pages, venue, archive, volume, issue, or university evidence
- **AND** the corresponding supported rich metadata field is missing
- **THEN** `persist_references` SHALL write the row but emit a `rich_metadata_evidence_missing` warning
- **AND** the workflow SHALL route to `review_reference_quality`.

#### Scenario: No clear evidence does not warn

- **WHEN** a raw reference does not contain clear supported rich metadata evidence
- **THEN** the rich metadata warning SHALL NOT be emitted solely because optional fields are absent.
