## Context

Both active skills already render arbitrary-length arrays, and neither the digest schema nor renderer defines maximum item counts. The limiting behavior comes from journal-sized numeric guidance repeated across active instruction files. `literature-analysis` carries detailed digest guidance in a stage reference, while `literature-digest` keeps the complete digest contract in one `SKILL.md`.

The OpenSpec main specs are also misaligned with the current directory layout: `lite-skill` describes the active digest-only implementation, while `literature-digest` describes the archived full-analysis implementation.

## Goals / Non-Goals

**Goals:**

- Give the LLM enough freedom to preserve distinct content from long, information-dense sources.
- Keep numeric guidance useful for ordinary papers without turning it into validation policy.
- Keep each active skill's numeric guidance in one authoritative location.
- Make OpenSpec capability names match the active skill names.

**Non-Goals:**

- Add page, character, token, or line-count tiers.
- Add a digest-length input field, runtime warning, gate, or payload validation rule.
- Change the five semantic slots, renderer templates, public artifacts, or stdout schemas.
- Add instruction-text snapshot tests or a formal LLM evaluation suite.

## Decisions

### Decision 1: Semantic scaling remains an LLM judgment

The agent evaluates substantive source length and information density together. Signals include additional independent methods, experiments, findings, limitations, chapters, and subtopics. Layout length, appendices, and repetition do not force expansion.

This keeps the policy responsive to academic structure. Fixed page or character tiers were rejected because PDF conversion, LaTeX expansion, appendices, and formatting make those measures unreliable proxies for digest value.

### Decision 2: Use widened soft ranges with an explicit escape clause

The active guidance uses these shared reference ranges:

- `tldr.paragraphs`: about 8-20 informative lines or paragraphs.
- `research_question_and_contributions.contributions`: 2-8 items.
- `method_highlights.items`: 3-12 items.
- `key_results.items`: 2-10 items.
- `limitations_and_reproducibility.items`: 1-6 items.

The ranges describe common outputs, not acceptable-payload boundaries. Long, information-dense sources may exceed them. Short or sparse sources must not be padded to reach them.

Removing all numeric guidance was rejected because it would make ordinary-paper output less consistent across agents. Raising hard caps was rejected because it would recreate the same failure at a larger document size.

### Decision 3: Scale section summaries by substantive structure

An ordinary paper may use roughly eight or more section/subsection blocks. Longer sources follow their substantive chapter/subchapter structure, split multi-theme chapters, and add items where distinct evidence requires it. There is no upper limit. Repetition, synonymous bullets, and unsupported detail are explicitly discouraged.

### Decision 4: Preserve the current architectures and payloads

`literature-analysis` remains SQLite-backed and automation-facing; its main stage card states the adaptive rule and routes detailed counts to `references/digest_generation.md`. `literature-digest` remains script-assisted and automation-facing; its one `SKILL.md` holds a single language-neutral density section. Scripts, schemas, templates, and public interfaces stay unchanged.

### Decision 5: Realign OpenSpec capabilities through deltas

The `literature-digest` delta removes requirements owned by the archived full-analysis workflow and adds the current digest-only contract. The `lite-skill` delta removes its duplicated requirements; `retire_capabilities: true` authorizes deletion once the capability becomes empty. The existing main `literature-digest` Purpose is updated directly because OpenSpec does not apply Purpose changes from a delta for an existing capability.

## Risks / Trade-offs

- [Different agents may choose different lengths for the same source] -> Keep widened reference ranges, explicit semantic signals, and anti-padding rules.
- [Long digests may consume more model context] -> Expand only for distinct grounded content; avoid page-count-based expansion and repeated coverage.
- [Capability realignment creates a large removal delta] -> Match every existing requirement name exactly and validate the change in strict mode before implementation and archive.
- [The main spec remains historically misaligned until sync/archive] -> Record the retirement marker and validate archive readiness after all tasks complete.

## Migration Plan

1. Add and strictly validate the three capability deltas.
2. Update the two active skills without changing runtime code or public contracts.
3. Update the existing `literature-digest` main-spec Purpose to the current digest-only capability.
4. When the change is synced or archived, replace the old `literature-digest` requirements and retire `lite-skill`.
5. Roll back by reverting the change artifacts and guidance edits before archive; after archive, restore the affected main specs from version control if required.
