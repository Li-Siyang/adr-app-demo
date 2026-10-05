# STORY-014 Independent Validation Rerun

**Test Run ID:** TR-029
**Coverage Story or Stories:** STORY-014
**Execution-owning Story:** STORY-014
**Validated commit:** `796074f9788662a0488f7e6b62fed6bae1289033`
**Report path:** `docs/test-results/story-014/details/TR-029-story-014-independent-rerun.md`

## Overall Status

**PASSED**

## Summary

This independent rerun used Requirement Definition v1.4 Approved, PLAN-001
v1.4 Approved, and TEST-001 v2.2 Approved (2026-10-02). STORY-014's approved
blocking scope is AC-037 and TC-014-01 only. The target production commit is
`796074f9788662a0488f7e6b62fed6bae1289033`; current HEAD is a later
documentation-only validation-evidence commit, with no production changes
since the tested commit.

| Scope | Approved Test Cases | Passed | Failed | Blocked | Manual | Not Yet Automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-014 blocking completion | 1 | 1 | 0 | 0 | 0 | 0 |

TC-014-01 was executed against `/` and `/app`. The test asserts that each
served page exposes a non-hidden notice with the approved demo/synthetic-only
language and all three prohibited real-data categories. The `/app` response
also exposes the record form. The notice uses the shared visible `.notice`
style. The identity-entry surface, creation surface, and shared edit surface
are represented by these two routes.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-SCP-003; CR-FR-023; CR-BR-010 | AC-037 | STORY-014 | STORY-014 | Blocking completion | TC-014-01 | **PASSED** — both served routes show the required notice; `/app` contains the shared create/edit form. |

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- Focused acceptance command, run from `backend`:
  `python -m pytest tests\acceptance\test_story_014_demo_data_and_https.py -q`
  — **2 passed** in 2.52 seconds; two existing dependency deprecation
  warnings.
- Full backend suite, run from `backend`:
  `python -m pytest -q` — **271 passed, 1 skipped** in 29.98 seconds.
  The skip is the existing STORY-009 archived-tag placeholder. Seventeen
  deprecation warnings were emitted; no tests failed.
- Developer-owned tests were included in the full backend suite.
- No production files changed after the tested commit. The later HEAD commit
  contains validation documentation only.

## Deferred Non-blocking Integration Validation

None is assigned to STORY-014 in TEST-001 v2.2.

## Uncovered Acceptance Criteria

None within STORY-014's approved scope. AC-032 and TC-016-03 are blocking
local-operation coverage for STORY-016. Deployed environments and HTTPS are
not acceptance requirements under the approved v1.4 baseline and were not
tested or treated as defects here.

## Recommendation

**READY FOR REVIEW** — TC-014-01 and the full backend regression suite passed.
The result applies to production commit
`796074f9788662a0488f7e6b62fed6bae1289033`. The inherited Jira mapping issue
is a tracking discrepancy and does not alter the approved acceptance
baseline; Jira was not modified.
