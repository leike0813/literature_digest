# Design: High-Value Optional Reference Field Extraction

## Context

Current behavior allows compliant output with only required fields:
- `author`, `title`, `year`, `raw`, `confidence`

This is contract-safe but often under-delivers metadata quality when richer information is present in source references.

## Design Goals

1. Preserve backward compatibility of required fields.
2. Increase extraction coverage for high-value optional fields.
3. Prevent two failure modes:
   - minimal-only laziness (agent outputs only required fields despite clear evidence),
   - hallucination (agent fabricates optional metadata without evidence).

## Non-Goals

1. Do not promote optional fields to hard-required fields.
2. Do not change output transport contract (`digest_path`, `references_path`).
3. Do not require parser-specific implementation changes in this OpenSpec change.

## Decision

### 1) Keep required contract unchanged

Reason:
- downstream consumers already depend on existing required fields;
- forcing more required fields would reduce robustness on noisy references.

### 2) Add prioritized optional extraction policy

Optional metadata is grouped by value:
1. container/venue (`publicationTitle`, conference/journal/school/institution container)
2. bibliographic location (`volume`, `issue`, `pages`)
3. identifiers (`DOI`, `url`, `arxiv`)
4. publisher/institution details (`publisher`, school/institution-like publisher info)

Reason:
- these fields provide highest practical retrieval and metadata utility.

### 3) Explicit anti-laziness rule

If direct textual evidence exists in `raw`, parser SHOULD populate corresponding optional fields.

Reason:
- removes ambiguity that previously allowed minimum-only outputs.

### 4) Explicit anti-hallucination rule

If evidence is weak/absent, optional fields remain optional and may be omitted.

Reason:
- preserves correctness under noisy OCR/format variation.

## Behavioral Impact

Expected changes in outputs:
- More frequent `publicationTitle`, `volume/issue/pages`, `DOI/url/arxiv`, `publisher` when present.
- No increase in fabricated metadata.
- Required-field compatibility remains unchanged.

## Acceptance Criteria

1. Spec contains requirement that required fields are unchanged.
2. Spec contains prioritized optional extraction requirement.
3. Spec contains anti-laziness scenario.
4. Spec contains anti-hallucination scenario.
