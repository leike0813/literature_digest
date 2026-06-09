# Change: Fix CJK Reference Title Quality Gate

## Summary

Fix the Stage 4 reference quality gate so CJK and other non-Latin original titles are accepted as usable reference titles, and add explicit language-preservation guidance so agents do not translate, Anglicize, or romanize reference titles to pass validation.

## Motivation

The current quality classifier tokenizes titles with an ASCII-only regex. A valid Chinese title such as `基于深度学习的文本分类方法` produces no content tokens and is hard-blocked as `no_usable_title_tokens`. This makes English translation the easiest path through the gate, even though references should preserve the cited work title as it appears in the raw reference.

## Scope

- Replace the ASCII-only title token detector with Unicode-aware logic using stdlib `unicodedata`.
- Keep existing identifier, metadata-only, author-only, numeric-only, and symbol-only rejection behavior.
- Add language/script preservation guidance to core instructions, gate notes, and Stage 4 docs.
- Add regression coverage for CJK titles and language-protection prompts.

## Out Of Scope

- Do not change `prepare_references_workset` candidate parsing regexes.
- Do not change `references.json` artifact shape.
- Do not add tokenizer dependencies.

