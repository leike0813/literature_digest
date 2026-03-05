# Tasks: Enhance High-Value Reference Field Extraction

1. Add OpenSpec delta for `literature-digest` that preserves current hard-required fields and adds stronger optional-field extraction behavior.
2. Update `literature-digest/SKILL.md` reference extraction section to:
   - keep mandatory fields unchanged,
   - add high-value optional field priority tiers,
   - add anti-laziness guidance (extract when evidence exists).
3. Ensure wording explicitly forbids hallucinating optional fields when evidence is missing.
4. (Optional doc sync) Update `literature-digest/README.md` if needed so behavior expectations are consistent with `SKILL.md`.
5. Verify OpenSpec change structure is complete:
   - `proposal.md`
   - `tasks.md`
   - `specs/literature-digest/spec.md`
