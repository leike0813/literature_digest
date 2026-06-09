# Tasks

- [x] Add OpenSpec delta specs for `literature-digest` and `sqlite-gated-skill-runtime`.
- [x] Replace ASCII-only reference title tokenization with Unicode-aware logic.
- [x] Preserve existing hard rejects for empty title, bare identifiers, author-only title, metadata-only title, and no usable nonnumeric text.
- [x] Update quality recommendations and gate command examples to preserve original title language/script.
- [x] Update `assets/core_instruction.md`, `SKILL.md`, and Stage 4/runtime docs with language-protection guidance.
- [x] Add tests for CJK title acceptance and remaining hard rejects.
- [x] Add guidance/gate tests for no-translation prompts.
- [x] Run strict OpenSpec validation and relevant pytest suite.
