## MODIFIED Requirements

### Requirement: Deterministic Citation-Scope Preprocess

The system MUST run a deterministic preprocessing stage before citation semantic analysis. The stage MUST consume agent-provided `citation_scope`, operate on normalized markdown, and persist mention data into the SQLite runtime database.

#### Scenario: Mention data persisted to DB
- **WHEN** preprocess executes successfully
- **THEN** extracted mention rows and mention statistics are written to the runtime database
- **AND** any JSON export is at most a derived debugging view, not the process truth.

### Requirement: Mention Count Authority

Expected mention coverage for final citation merge MUST come from the runtime database.

#### Scenario: Coverage check uses DB count
- **WHEN** the final citation artifact is rendered
- **THEN** mention coverage is checked against the persisted DB mention count
- **AND** a mismatch causes failure instead of best-effort repair.
