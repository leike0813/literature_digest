## 1. OpenSpec artifacts

- [x] 1.1 Create proposal, design, tasks, and delta spec

## 2. Reference payload and work packages

- [x] 2.1 Add reference review packages and allowed parse pattern JIT output
- [x] 2.2 Accept only `reference_reviews[]` agent submit payload
- [x] 2.3 Convert reference reviews to deterministic internal persistence
- [x] 2.4 Aggregate reference payload validation errors
- [x] 2.5 Add split review package fields for suspect blocks

## 3. Citation payload and work packages

- [x] 3.1 Add citation work packages with `citation_work_key` and source reference number
- [x] 3.2 Accept only `citation_semantic_reviews[]` plus `timeline_summaries`
- [x] 3.3 Convert citation semantic reviews to deterministic internal persistence
- [x] 3.4 Derive timeline buckets from years
- [x] 3.5 Aggregate citation payload validation errors

## 4. Guidance

- [x] 4.1 Rewrite SKILL reference and citation stage cards
- [x] 4.2 Rewrite reference extraction guidance for current payload and subagents
- [x] 4.3 Rewrite citation analysis guidance for current payload and subagents
- [x] 4.4 Ensure guidance does not describe old payload compatibility

## 5. Tests and validation

- [x] 5.1 Update runtime tests for new payloads
- [x] 5.2 Add validation tests for invalid patterns and rejected old fields
- [x] 5.3 Add citation work key and derived timeline tests
- [x] 5.4 Run targeted tests and OpenSpec status
