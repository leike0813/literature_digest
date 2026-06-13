## ADDED Requirements

### Requirement: Split Review Conservation SHALL Use Token Coverage

The runtime SHALL validate split review text preservation using token coverage instead of exact normalized string equality.

#### Scenario: Harmless text-shape differences
- **WHEN** `split_reviews[].corrected_reference_texts` preserve the source block's core tokens
- **AND** only differ by whitespace, line breaks, Unicode normalization, fullwidth/halfwidth punctuation, quote style, dash style, or punctuation style
- **THEN** split review validation succeeds.

#### Scenario: Missing protected evidence
- **WHEN** corrected split texts drop a URL, DOI, arXiv identifier, year, author token, or title keyword from the suspect block
- **THEN** split review validation fails with `reference_entry_splitting_failed`
- **AND** the error includes token conservation diagnostics.

### Requirement: Post-Review Boundary Suspicion SHALL Be Warning-Only

After token conservation succeeds, remaining deterministic boundary suspicion SHALL NOT hard-block reference persistence by itself.

#### Scenario: Heuristic suspicion remains after reviewed split
- **WHEN** split review passes token conservation
- **AND** a subsequent reference preprocess still reports suspect blocks
- **THEN** runtime continues and returns regenerated reference review packages
- **AND** records `reference_boundary_suspicion_after_review` warnings.

### Requirement: Web Resource References SHALL Be Allowed Without Year

References that are web resources, software repositories, project pages, or URLs SHALL be allowed to proceed without a publication year.

#### Scenario: No-year URL reference
- **WHEN** a reviewed reference entry contains a URL or resource link but no publication year
- **THEN** reference persistence may proceed with `publication_year=null`
- **AND** later timeline/citation stages may warn about missing year without requiring invented metadata.
