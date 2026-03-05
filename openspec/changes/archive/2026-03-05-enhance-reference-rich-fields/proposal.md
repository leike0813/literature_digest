# Change Proposal: Enhance High-Value Reference Field Extraction

## Background

The current `literature-digest` skill treats only a minimal subset of reference fields as strictly required (`author`, `title`, `year`, `raw`, `confidence`).
In practice, agents tend to stop at this minimum and frequently omit high-value bibliographic details even when those details are clearly present in the source text.

## Problem

When high-value optional fields are omitted, downstream usability drops:
- Reduced value for reference quality and retrieval.
- Lower quality for Zotero alignment and metadata normalization.
- More manual post-processing for users.

## Goal

Keep the **hard-required field contract unchanged**, while strengthening extraction expectations for high-value optional fields so that agents actively extract them whenever evidence exists.

## Non-Goals

- Do not convert optional fields into hard-required fields.
- Do not change the output file protocol (`digest_path`, `references_path`).
- Do not introduce new mandatory top-level output keys.

## Scope

- Update `literature-digest/SKILL.md` wording and behavioral guidance for reference extraction.
- Add explicit priority tiers for optional metadata extraction.
- Add anti-laziness constraints (agent should not stop at minimum required fields if high-value fields are inferable from `raw` evidence).

## Success Criteria

- The spec explicitly states that minimal required fields remain unchanged.
- The spec explicitly prioritizes extraction of high-value optional fields:
  - Venue-like fields (`publicationTitle`, conference/journal/school/container name)
  - Bibliographic fields (`volume`, `issue`, `pages`)
  - Access/identifier fields (`DOI`, `url`, `arxiv`)
  - Publisher/school/institution-like fields when available.
- The spec contains scenario-based requirements that distinguish:
  - “evidence present => should extract”
  - “evidence absent/uncertain => keep optional and do not hallucinate”
