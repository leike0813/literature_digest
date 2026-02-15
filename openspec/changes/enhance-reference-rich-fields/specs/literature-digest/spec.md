## ADDED Requirements

### Requirement: Keep Mandatory Reference Contract Unchanged

The skill MUST keep the existing required reference item fields unchanged.

Each reference item MUST still include:
- `author: string[]`
- `title: string`
- `year: number|null`
- `raw: string`
- `confidence: number`

#### Scenario: Preserve required-only compatibility
- **WHEN** the skill outputs references
- **THEN** every item still contains the original required fields above
- **AND** no previously required field is removed or downgraded.

### Requirement: Prioritize High-Value Optional Metadata Extraction

The skill SHOULD aggressively extract high-value optional fields when supported by clear evidence in `raw` text.

Priority order for optional fields:
1. Venue/container information:
   - `publicationTitle`
   - conference/journal/school/container name (mapped to the most appropriate output field)
2. Bibliographic location:
   - `volume`
   - `issue`
   - `pages`
3. Identifiers and links:
   - `DOI`
   - `url`
   - `arxiv`
4. Publisher/institution details:
   - `publisher`
   - school/institution-like publisher info when present

#### Scenario: Evidence-present optional extraction
- **GIVEN** a reference `raw` string includes conference/journal name, volume/issue/pages, DOI or URL
- **WHEN** the skill parses the item
- **THEN** it SHOULD output those optional fields instead of returning only the minimum required fields.

### Requirement: No Minimal-Only Laziness When Evidence Exists

The skill MUST NOT intentionally stop at minimal required fields if high-value optional fields are directly extractable from `raw`.

#### Scenario: Avoid minimum-only output
- **GIVEN** `raw` contains explicit `In: <venue>`, `vol.`, `no.`, `pp.`, `doi`, or URL patterns
- **WHEN** parsing completes
- **THEN** corresponding optional fields SHOULD be populated
- **AND** output SHOULD NOT be limited to only required fields unless extraction is genuinely uncertain.

### Requirement: Optional Fields Stay Optional and Non-Hallucinatory

Optional fields remain non-mandatory.
If evidence is absent or ambiguous, the skill MUST prefer omission over hallucination.

#### Scenario: Missing optional evidence
- **GIVEN** a reference entry lacks trustworthy venue/volume/issue/pages/identifier signals
- **WHEN** parsing the item
- **THEN** optional fields MAY be omitted
- **AND** `confidence` SHOULD reflect uncertainty without fabricating metadata.
