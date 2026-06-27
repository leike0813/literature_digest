## MODIFIED Requirements

### Requirement: Citation analysis persists best-effort artifacts
The `literature-analysis` runtime SHALL complete the citation analysis stage and render final artifacts after citation workset preparation has run, even when the prepared workset contains no stable mapped citation items. Empty citation semantics, timeline summaries, and global summary SHALL be valid persisted results.

#### Scenario: Empty prepared workset completes final render
- **WHEN** citation workset preparation succeeds with zero citation packages and the agent submits an empty citation payload
- **THEN** the runtime SHALL persist empty citation semantics, timeline, and summary records and SHALL render final artifacts with an empty citation item list

#### Scenario: Missing preparation still fails
- **WHEN** the agent submits citation semantics before citation workset preparation has completed
- **THEN** the runtime SHALL fail and require citation workset preparation

#### Scenario: Unknown submitted references still fail
- **WHEN** a citation semantics payload contains a ref index or citation work key outside the prepared workset
- **THEN** the runtime SHALL reject the payload rather than inventing a mapping

#### Scenario: Empty prepared workset export succeeds
- **WHEN** citation workset preparation completed with empty mentions and items
- **THEN** exporting the citation workset SHALL return empty arrays instead of reporting the workset as missing
