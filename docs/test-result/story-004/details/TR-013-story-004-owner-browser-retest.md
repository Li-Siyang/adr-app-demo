# Test Result Report

**Test Run ID:** TR-013
**Story:** STORY-004
**Validated commit:** `660d896898b359492e74d73140accfb208233f82`
**Report path:** `docs/test-result/story-004/details/TR-013-story-004-owner-browser-retest.md`

## Overall Status

PASSED

## Summary

Approved Test Cases: 5; passed: 5; failed: 0; blocked: 0; manual: 0;
not automated: 0. The additional Owner-presentation regression reported in
TR-012 also passed its independent retest. No production source was modified
for this validation run.

Against a clean detached checkout of the exact commit above, Chrome
153.0.8010.53 was driven through the real application with Playwright. The
validator delayed `/api/mock-identities` until after clicking Edit on an
authored Draft whose Owner is a different identity. Once the identity list
arrived, the disabled Owner select still displayed `arun-approver`, matching
the record's retained Owner, rather than defaulting to `maya-member`.
Saving the edit preserved Owner and Draft status.

The same browser run verified creation-mode native required constraints,
saving an incomplete Draft in edit mode, the complete missing-field and
designated-approver submission message while retaining Draft status, and
submitting a complete Draft through the UI to Proposed after designating an
approver. Non-author edit denial and Abandoned Draft edit/submission denial
were executed through the approved API acceptance tests.

## Requirement Coverage

| Requirement | Acceptance Criterion | Story | Test Case | Result |
| --- | --- | --- | --- | --- |
| CR-USR-003; CR-FR-006 | — | STORY-004 | TC-004-01 | Passed: browser edit/save retains Draft; delayed Owner display and persisted Owner match |
| CR-USR-003; CR-FR-006 | — | STORY-004 | TC-004-02 | Passed: other identity denied via API with record unchanged |
| CR-FR-007–008 | AC-005 | STORY-004 | TC-004-03 | Passed: complete Draft submitted in Chrome becomes Proposed |
| CR-FR-004, CR-FR-024; CR-BR-016 | AC-004, AC-024 | STORY-004 | TC-004-04 | Passed: incomplete Draft remains Draft; Chrome displays all missing fields and actionable approver message |
| CR-FR-030; CR-BR-016, CR-BR-019 | AC-047 | STORY-004 | TC-004-05 | Passed: all configured roles denied edit and submission via API with controlled Abandoned precondition |
| CR-FR-006A | — | STORY-004 edit UI / STORY-003 author-owner model | TR-012 additional regression | Passed: selected Owner matches stored Owner after delayed identity loading |

## Failed Tests

None. TR-012's `IMPLEMENTATION_DEFECT` was not reproduced on the fix commit.

## Regression Result

- `python -m pytest -q tests\test_decision_records.py
  tests\test_governance.py tests\acceptance\test_story_004_edit_submit_draft.py`:
  45 passed.
- `python -m pytest -q -rs`: 116 passed, 1 skipped. The skipped
  STORY-009 archived-tag case is deferred by Human Reviewer approval to
  STORY-012; it is unrelated to STORY-004.
- `node --check backend\app\static\app.js`: passed.
- Real Chrome browser scenario including delayed identity response, edit
  save, incomplete-submission feedback, and complete submission: passed.

Five deprecation warnings from installed FastAPI/Starlette/AnyIO dependencies
did not affect the test outcomes. Browser automation was executed with an
isolated local single-process backend; the approved Abandoned precondition
remains controlled in the existing acceptance test because replacement
abandonment is planned for STORY-007.

## Uncovered Acceptance Criteria

None for STORY-004 within the approved Test Design. The approved
STORY-009 archived-tag deferred test remains outside this Story's scope.

## Recommendation

READY FOR REVIEW for the exact validated production commit
`660d896898b359492e74d73140accfb208233f82`. Any later production change
requires independent retesting. Human review and PR approval are separate.
