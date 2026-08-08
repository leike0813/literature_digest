## ADDED Requirements

### Requirement: Runtime SHALL Persist Source Identity As Structured State

The SQLite runtime SHALL persist the analysis-plan source identity separately from runtime parameters and SHALL expose one deterministic effective identity for reference API resolution.

#### Scenario: Parameter identity takes precedence
- **WHEN** both a valid runtime parameter identity and a persisted analysis-plan identity exist
- **THEN** the effective identity is the runtime parameter identity
- **AND** the identity source is recorded for audit

#### Scenario: No effective identity exists
- **WHEN** neither source provides a valid DOI or arXiv identifier
- **THEN** API resolution is recorded as skipped
- **AND** reference preparation continues normally

### Requirement: Provider Fetches SHALL Be Cached And Auditable

The runtime SHALL persist provider status, bounded response data, response hash, fetch time, and error details per canonical source identifier so repeated preparation in one run is deterministic.

#### Scenario: Stable boundaries are re-prepared
- **WHEN** a provider was already attempted for the effective identifier in the current run
- **THEN** runtime reuses the persisted outcome instead of repeating the network request

#### Scenario: Provider response is malformed or unavailable
- **WHEN** a provider returns an unusable response or request failure
- **THEN** runtime persists a failed or empty fetch outcome
- **AND** emits a warning without setting the workflow error

### Requirement: API Match Decisions SHALL Be DB-Backed

The runtime SHALL persist one resolution decision per local reference entry, including acceptance status, provider record identity, match basis, match score, and normalized candidate data.

#### Scenario: Match is accepted
- **WHEN** a provider candidate satisfies the deterministic completeness, uniqueness, and quality gates
- **THEN** its accepted normalized item is persisted with internal resolution provenance

#### Scenario: Match is unresolved
- **WHEN** a candidate is incomplete, ambiguous, conflicting, or below threshold
- **THEN** the local entry remains unresolved
- **AND** the reason is available in the API audit state

### Requirement: API Resolution Receipts SHALL Respect Reference Invalidation

The runtime SHALL record API resolution as a scripted substep and invalidate match decisions whenever prepared reference boundaries or effective source identity change.

#### Scenario: Split review changes boundaries
- **WHEN** corrected reference boundaries are persisted
- **THEN** prior per-entry match decisions and downstream reference receipts are cleared
- **AND** a cached provider response for the same effective identity remains reusable

#### Scenario: Split workset is filtered by accepted coverage
- **WHEN** API resolution runs against prepared suspect blocks
- **THEN** each suspect block maps to stable local entry indexes
- **AND** prepare receipts and workflow state count only blocks with at least one unresolved entry
- **AND** a submitted partial split review is combined transactionally with runtime-owned keep decisions for fully accepted blocks

#### Scenario: Effective identity changes
- **WHEN** the effective DOI or arXiv identity changes before reference resolution
- **THEN** prior provider cache and match decisions no longer authorize reference persistence

### Requirement: Partial Reference Persistence SHALL Preserve Single-Writer Semantics

API-resolved items and agent-reviewed unresolved items SHALL be combined through one runtime-owned transactional persistence path.

#### Scenario: Agent submits unresolved reviews
- **WHEN** the payload covers every unresolved reference key exactly once
- **THEN** runtime validates the combined set
- **AND** replaces `reference_items` atomically with the complete local-order result

#### Scenario: Agent attempts to submit an API-resolved key
- **WHEN** `reference_reviews[]` includes a protected API-resolved key
- **THEN** runtime rejects it as outside the active workset
