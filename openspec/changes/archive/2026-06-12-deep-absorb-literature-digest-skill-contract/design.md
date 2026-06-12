## Context

The original `literature-digest/SKILL.md` is a dense operating contract. It contains:

- background automation rules
- stdout and artifact schemas
- SQLite-as-SSOT discipline
- LLM versus script responsibility boundaries
- a project-wide parameter vocabulary
- per-stage cards with commands, payloads, examples, success conditions, and failure branches
- detailed reference and citation guardrails

`literature-analysis` should absorb those strengths, but it must not inherit the old 18-action gate shape or agent-facing SQL/gate playbooks.

## Goals / Non-Goals

**Goals:**

- Make `literature-analysis/SKILL.md` sufficient to guide one complete run.
- Keep long examples and edge-case details in `literature-analysis/references/`.
- Preserve the six agent-facing stages and SQLite single-writer discipline.
- Capture reference and citation high-risk rules as explicit hard constraints.
- Add tests that guard the new document depth and block old gate-only wording.

**Non-Goals:**

- Do not modify old `literature-digest`.
- Do not migrate more runtime algorithms in this change.
- Do not expose old `gate_runtime_interface.md` or `sql_playbook.md` as normal `literature-analysis` instructions.
- Do not re-expand the new workflow into the old 18 runtime-only actions.

## Decisions

### Decision 1: SKILL.md becomes a dense contract

`literature-analysis/SKILL.md` should contain the hard contract, shared vocabulary, and stage cards. It should be longer than the first skeleton because an agent must be able to execute the skill without inferring hidden rules from old documents.

### Decision 2: References hold deep examples

The five `literature-analysis/references/*.md` files hold longer examples and detailed edge cases for source planning, digest generation, reference extraction, citation analysis, and recovery. The entry document indexes them by stage and error class.

### Decision 3: Rewrite, do not copy gate discipline

Rules from old gate and SQL playbooks are absorbed only when they describe durable payload, validation, recovery, or SQLite integrity constraints. Old next-action and re-gate instructions do not become the new main path.

### Decision 4: Tests check semantic anchors

Guidance tests assert durable section names, key fields, rule anchors, and forbidden old-gate strings. They intentionally avoid exact large snapshots so the docs remain maintainable.

## Risks

- Guidance tests can become too text-sensitive if they assert prose. The tests therefore check stable headings, field names, and rule codes rather than paragraphs.
- A dense `SKILL.md` increases entry size. This is intentional for the hard contract; deep format examples still live in references.
