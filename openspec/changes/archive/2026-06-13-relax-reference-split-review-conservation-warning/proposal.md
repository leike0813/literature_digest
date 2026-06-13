## Why

`literature-analysis` currently rejects split review payloads unless corrected entries preserve a suspect block as an exactly equal normalized string. This is stricter than the intended safety goal and can reject harmless Unicode, punctuation, or line-break differences. After a split review succeeds, the runtime also reruns boundary heuristics and hard-fails when the same heuristic suspicion remains, which can create an impossible loop for valid no-year web/resource references.

## What Changes

- Replace exact string equality for split review preservation with token coverage conservation.
- Keep hard failures for missing core tokens, added invented content, translation/rewrite, or deletion of URL/DOI/arXiv/year/author/title evidence.
- Downgrade post-review boundary heuristic suspicion to warnings after token conservation passes.
- Keep `persist_references` CLI and `split_reviews[]` payload shape unchanged.
- Document that web/resource references may lack author or year and should flow to core review/metadata review with warnings instead of blocking split review.

## Impact

- Agents can repair split boundaries without matching runtime's exact Unicode and punctuation normalization.
- Runtime remains protected against fabricated or rewritten split text.
- Valid no-year web resources no longer block reference persistence or citation analysis.
