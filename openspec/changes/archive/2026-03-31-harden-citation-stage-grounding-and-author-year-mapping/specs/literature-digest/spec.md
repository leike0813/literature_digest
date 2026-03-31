# Delta: literature-digest

## ADDED Requirements

### Requirement: Stage 5 Citation Analysis SHALL Be Script-Grounded

The skill SHALL treat stage 5 citation analysis as complete only when the scripted action chain has been executed in order.

#### Scenario: Gate blocks stage-5 progression without required receipts
- **WHEN** a stage-5 or stage-6 transition is attempted without the required prior stage-5 action receipts
- **THEN** gate blocks progression
- **AND** the missing prerequisite summary names the missing `action_receipts.*` entries

#### Scenario: Render blocks final publication without required receipts
- **WHEN** `render_and_validate --mode render` is called and any required stage-5 receipt is missing
- **THEN** render returns a schema-compatible error JSON
- **AND** it does not publish final public artifacts

### Requirement: Citation Stage SHALL Fail On Empty Review-Like Worksets

The skill SHALL not treat review-like or citation-shaped scopes with zero stable citation workset output as a normal completion state.

#### Scenario: Review-like scope yields zero stable mentions
- **WHEN** `prepare_citation_workset` processes a review-like or citation-shaped scope
- **AND** it produces zero stable mentions or zero citation workset items
- **THEN** the action fails with a citation-stage grounding error

### Requirement: Author-Year Mapping SHALL Support Multi-Token First Authors

The skill SHALL normalize first-author surname aliases so author-year mentions can match references whose first author contains multiple tokens.

#### Scenario: Multi-token first author maps successfully
- **WHEN** a mention uses a surname hint such as `zamir`
- **AND** the matching reference first author is structured as `Waqas Zamir, S.`
- **THEN** author-year matching resolves the mention to that reference item for the same year
