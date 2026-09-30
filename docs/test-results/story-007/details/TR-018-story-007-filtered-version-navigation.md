# Test Result Report

**Test Run ID:** TR-018
**Coverage Story or Stories:** STORY-007
**Execution-owning Story:** STORY-007
**Validated commit:** `5a5ae138dac96d0bb3c571f935f50a50fff610ee`
**Branch:** `li-siyang-supreme-memory`
**Report path:** `docs/test-results/story-007/details/TR-018-story-007-filtered-version-navigation.md`

## Overall Status

**PASSED**

## Summary

- Approved blocking STORY-007 Test Cases: 8
- Passed: 8
- Failed: 0
- Blocked: 0
- Manual-only: 0
- Not yet automated: 0
- Independent STORY-007 acceptance suite:
  `python -m pytest tests/acceptance/test_story_007_replacement_versions.py -q`
  — **12 passed**.
- Targeted acceptance and Developer-owned tests:
  `python -m pytest tests/acceptance/test_story_007_replacement_versions.py tests/test_decision_records.py tests/test_audit.py -q`
  — **93 passed**.
- Full backend regression: `python -m pytest tests -q` — **225 passed,
  1 skipped**.

This retest targets the exact production commit named above, which is the
pushed PR head at execution. It independently retests review finding
`discussion_r4140120785` and the related STORY-007 acceptance/regression scope.
No production code was changed during validation.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-011; CR-BR-004–005 | AC-009 | STORY-007 | STORY-007 | Blocking completion | TC-007-01 | **PASSED** — acceptance suite rerun; direct editing of Accepted records remains denied and retained content unchanged. |
| CR-FR-012; CR-BR-005, CR-BR-013–014 | AC-010 | STORY-007 | STORY-007 | Blocking completion | TC-007-02 | **PASSED** — acceptance suite rerun; administrator replacement creation remains linked and leaves the original Accepted. |
| CR-FR-012; CR-BR-013–014 | AC-003, AC-025 | STORY-007 | STORY-007 | Blocking completion | TC-007-03 | **PASSED** — acceptance suite rerun; authorization and single-active-replacement constraints remain enforced. |
| CR-FR-013; CR-BR-006 | AC-011, AC-039 | STORY-007 | STORY-007 | Blocking completion | TC-007-04 | **PASSED** — acceptance suite rerun; accepting a replacement supersedes the prior Accepted record and retains links/audit. |
| CR-FR-012; CR-BR-014 | AC-039 | STORY-007 | STORY-007 | Blocking completion | TC-007-05 | **PASSED** — acceptance suite rerun; rejection ends the active interval and permits a new replacement. |
| CR-FR-030; CR-BR-019 | AC-046 | STORY-007 | STORY-007 | Blocking completion | TC-007-06 | **PASSED** — acceptance suite rerun. Independent headless Chrome 153 retest additionally used different exact tags on the Accepted original (`original-only`) and retained Abandoned Draft (`replacement-only`): each filtered card showed its relationship link although the destination was filtered out; activating either link cleared the filter, rendered the destination, and navigated to the existing target card. Original remained Accepted; replacement remained Draft (Abandoned). |
| CR-FR-030; CR-BR-019 | AC-003, AC-047 | STORY-007 | STORY-007 | Blocking completion | TC-007-07 | **PASSED** — acceptance suite rerun; unauthorized and invalid abandonment targets remain denied. |
| CR-FR-030; CR-NFR-003; CR-BR-019 | AC-047 | STORY-007 | STORY-007 | Blocking completion | TC-007-08 | **PASSED** — acceptance suite rerun; abandoned replacement remains immutable and non-reactivatable. |

## Failed Tests

None. The previously reported filtered-navigation implementation defect is
resolved on the validated commit.

## Regression Result

- Developer-owned unit/API coverage was independently rerun with the targeted
  suite: **93 passed** across the STORY-007 acceptance suite and
  `test_decision_records.py` / `test_audit.py`.
- Full backend regression: **225 passed, 1 skipped**.
- The sole skip is the previously approved STORY-009 archived exact-tag
  discovery case, deferred until STORY-012 provides archival support and
  unrelated to this STORY-007 retest.
- Headless Chrome 153 independently exercised the rendered `/app` page with
  linked Accepted and Abandoned records carrying different exact tags. In both
  filter directions, the visible record retained its link; activating it
  cleared the filter and landed on a rendered target card.
- Full-suite execution emitted 17 existing dependency deprecation warnings;
  no warning caused a failure.

## Deferred Non-blocking Integration Validation

| Test Case | Coverage Story or Stories | Execution-owning Story | Required capability / deferred scope | Result for this run |
| --- | --- | --- | --- | --- |
| TC-004-05 | STORY-004; STORY-007 | STORY-007 | Abandoned replacement Draft edit and submission denial | **PASSED** in the independent STORY-007 acceptance suite. |
| TC-005-03 | STORY-005; STORY-008 | STORY-007 | Superseded-record immutability after replacement acceptance | **PASSED** in the independent STORY-007 acceptance suite. |
| TC-006-02 | STORY-006; STORY-007 | STORY-007 | Ownership-transfer denial for an Abandoned replacement Draft | **PASSED** in the independent STORY-007 acceptance suite. |
| TC-015-02 | STORY-015; STORY-007; STORY-011 | STORY-007 | Abandonment audit attribution/time and comment-deletion audit attribution | Abandonment audit evidence **PASSED** under TC-007-06. Comment-deletion validation remains deferred until STORY-011 supplies that capability; non-blocking. |
| TC-002-02 | STORY-002; STORY-007; STORY-012 | STORY-012 | Full administrator-only archive, restore, replacement-creation, and abandonment matrix | Replacement-action denials remain covered by TC-007-03/07. Full archive/restore integration matrix remains deferred to STORY-012 and does not block STORY-007. |
| TC-015-01, TC-015-03 | STORY-015 and governed-action Stories; STORY-012 | STORY-012 | Full audit-event matrix, archival events, and archived-record retention | Remaining cross-workflow audit and archival-retention checks remain deferred to STORY-012 and do not block STORY-007. |

## Uncovered Acceptance Criteria

None for the STORY-007 blocking completion cases. Deferred cross-Story scope
remains explicitly identified above.

## Recommendation

**READY FOR REVIEW** for production commit
`5a5ae138dac96d0bb3c571f935f50a50fff610ee`. The independent retest confirms
the filtered bidirectional navigation defect is resolved on this exact commit.
Human review remains required.
