## ADDED Requirements

### Requirement: Preserve Reference Title Language In Quality Gate

`literature-digest` SHALL accept valid reference titles written in CJK or other non-Latin scripts without requiring translation to English.

#### Scenario: Chinese title passes Stage 4 quality gate

- **WHEN** `persist_references` receives a row whose `title` is `基于深度学习的文本分类方法`
- **THEN** the quality classifier SHALL treat the title as having usable title tokens
- **AND** it SHALL NOT emit `no_usable_title_tokens`
- **AND** Stage 4 SHALL be allowed to proceed when no other quality issue exists.

#### Scenario: Quality repair preserves original title script

- **WHEN** the gate returns Stage 4 quality directives
- **THEN** the instructions SHALL tell the agent to recover the cited title in the raw reference's original language/script
- **AND** SHALL NOT imply that translation, Anglicization, or romanization is an acceptable fix.

#### Scenario: Non-title values still fail

- **WHEN** a title is empty, a bare identifier or URL, author-only, publication metadata only, pure numeric, or pure punctuation
- **THEN** the corresponding existing hard quality reason SHALL still block the row.

