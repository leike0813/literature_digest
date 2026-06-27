## 1. Runtime Gates

- [x] 1.1 Change citation semantics persistence to require prepare receipt instead of non-empty workset items.
- [x] 1.2 Change citation timeline persistence to require semantics receipt instead of non-empty citation items.
- [x] 1.3 Change citation summary persistence to require timeline receipt instead of non-empty citation items.
- [x] 1.4 Allow export of a prepared empty citation workset.

## 2. Guidance

- [x] 2.1 Update `SKILL.md` to state that empty prepared worksets can be completed with an empty citation payload.
- [x] 2.2 Update `references/citation_analysis.md` recovery notes for empty prepared worksets.

## 3. Tests

- [x] 3.1 Add end-to-end regression test for empty prepared citation workset rendering final artifacts.
- [x] 3.2 Add test that submit-before-prepare still fails.
- [x] 3.3 Add test that exporting a prepared empty workset succeeds.
- [x] 3.4 Run the targeted regression suite.
