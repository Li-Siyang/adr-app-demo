# Test Result Report

**Test Run ID:** TR-012
**Story:** STORY-004
**Validated commit:** `68d316139717a6cf00a29f3fb698bf9d65a10427`
**Report path:** `docs/test-result/story-004/details/TR-012-story-004-browser-validation.md`

## Overall Status

FAILED

## Summary

Approved Test Cases: 5; passed: 5 (TC-004-01 through TC-004-05, including
existing API acceptance coverage); failed approved cases: 0; blocked: 0;
manual: 0; not automated: 0. One additional browser edit-mode regression
check **failed** and prevents a validation PASS. It is reported below with
TC-004-01 as its related approved editing case, without changing that case's
approved expected result.

Chrome 153.0.8010.53, driven by Playwright against the running FastAPI
application, exercised the actual creation/edit/submission UI in a clean
single-process environment. The browser test deliberately held the
`/api/mock-identities` response until after clicking Edit on a Draft whose
author (`maya-member`) differs from its owner (`arun-approver`). The Owner
control remained disabled and the saved record retained its actual owner,
but after identities loaded the disabled control displayed `maya-member`.

Browser checks passed for edit/save retaining Draft status and correct backend
ownership (TC-004-01); native required-field validation in creation mode;
blank required-field edit/save and actionable submission errors with the
record remaining Draft (TC-004-04); and valid UI Draft-to-Proposed submission
after designating an approver (TC-004-03). API acceptance tests also passed
for non-author denial (TC-004-02) and Abandoned Draft denial for all configured
roles (TC-004-05).

## Requirement Coverage

| Requirement | Acceptance Criterion | Story | Test Case | Result |
| --- | --- | --- | --- | --- |
| CR-USR-003; CR-FR-006 | — | STORY-004 | TC-004-01 | Approved edit/save outcome passed; related Owner presentation regression failed |
| CR-USR-003; CR-FR-006 | — | STORY-004 | TC-004-02 | Passed via API acceptance test |
| CR-FR-007–008 | AC-005 | STORY-004 | TC-004-03 | Passed in Chrome and API acceptance test |
| CR-FR-004, CR-FR-024; CR-BR-016 | AC-004, AC-024 | STORY-004 | TC-004-04 | Passed in Chrome and API acceptance test |
| CR-FR-030; CR-BR-016, CR-BR-019 | AC-047 | STORY-004 | TC-004-05 | Passed via API acceptance test with controlled Abandoned setup |
| CR-FR-006A | — | STORY-004 edit UI / STORY-003 author-owner model | Additional UI regression | Failed: displayed Owner differs from retained record Owner |

## Failed Tests

### Test Failure Report: edit-mode Owner presentation regression

**Test Run ID:** TR-012

**Story:** STORY-004 (related distinct author/owner behavior from STORY-003)

**Test Case:** Additional browser regression check associated with TC-004-01;
the approved TC-004-01 edit/save expected result itself passed.

**Related Requirement:** CR-FR-006A (author and owner are distinct retained
attributes); CR-FR-006 (author editing an eligible Draft).

**Related Acceptance Criterion:** None assigned to this additional UI check.

**Expected Behavior:** While editing a Draft, the disabled Owner control shows
the record's actual Owner, including after asynchronous identity loading;
author-only edits cannot change that Owner.

**Actual Behavior:** The control shows the author (`maya-member`) instead of
the persisted Owner (`arun-approver`) after delayed identity loading. Saving
the edit keeps the persisted Owner as `arun-approver` and remains Draft.

**Classification:** IMPLEMENTATION_DEFECT

**Severity:** Medium

**Evidence:** In Chrome, create an authored Draft with Owner
`arun-approver`; delay `/api/mock-identities` on `/app`, click Edit while the
request is pending, then release it. The control is disabled but reports
`maya-member`; `GET /api/decision-records/{id}` still reports
`owner.id=arun-approver`. A local screenshot and executable reproduction script
are retained in the validating session's `files/browser-test/` directory.
`beginEdit` assigns the Owner selection before `loadContext` replaces the
select's options; option replacement resets the selection to the first user.

**Recommended Next Owner:** Developer Agent

## Regression Result

At the exact commit above, targeted unit/governance/STORY-004 acceptance
tests: 45 passed. Full `python -m pytest -q -rs`: 116 passed, 1 skipped
(STORY-009 archived-tag case deferred by Human Reviewer to STORY-012),
5 dependency deprecation warnings. The browser scenario completed the three
requested UI paths but exited nonzero due to the additional Owner display
assertion. The other automated tests do not assert this display state.

## Uncovered Acceptance Criteria

No STORY-004 acceptance criterion remains unexecuted in this run. The reported
Owner presentation defect is an additional regression not covered by the
approved TC-004-01 expected result.

## Recommendation

NOT READY FOR REVIEW. Return the confirmed Owner presentation defect to the
Developer Agent, then independently retest the exact fix commit, including the
same delayed identity-loading scenario and related regression suite. This
report is **not** an independent validation PASS.
