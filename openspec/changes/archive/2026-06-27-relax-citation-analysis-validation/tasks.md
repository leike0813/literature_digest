## 1. Runtime Validation

- [x] 1.1 Relax citation workset preparation so valid citation scopes with no stable mapped workset return success with warnings.
- [x] 1.2 Split citation submit handling into hard validation and tolerant normalization.
- [x] 1.3 Accept empty and partial citation semantic reviews without creating placeholder items.
- [x] 1.4 Merge duplicate known citation review keys deterministically.
- [x] 1.5 Allow empty timeline summaries, empty global summary, and empty summary basis.
- [x] 1.6 Relax render prerequisites and public citation validation for empty citation items and empty summary text.

## 2. Guidance

- [x] 2.1 Update `SKILL.md` and stage guidance to describe tolerant best-effort citation persistence.
- [x] 2.2 Update runner/core instruction text to avoid strict full-coverage wording.

## 3. Tests

- [x] 3.1 Add or adjust runtime tests for empty payload, partial reviews, empty fields, duplicate merges, and empty worksets.
- [x] 3.2 Preserve hard-failure tests for unknown citation keys and forbidden internal fields.
- [x] 3.3 Run the targeted pytest suite and fix regressions.
