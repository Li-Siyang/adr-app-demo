# STORY-014 Demo-Data Notice Validation

**Test Run ID:** TR-028
**Coverage Story or Stories:** STORY-014
**Execution-owning Story:** STORY-014
**Validated commit:** `796074f9788662a0488f7e6b62fed6bae1289033`
**Report path:** `docs/test-results/story-014/details/TR-028-story-014-demo-data-notice.md`

## Overall Status

**PASSED**

## Summary

Independent validation was performed against the approved Requirement
Definition v1.4, PLAN-001 v1.4, and TEST-001 v2.2, all approved on
2026-10-02. STORY-014/TASK-020 owns AC-037 only: the visible demo/synthetic
data notice and prohibition on real internal confidential, regulated personal,
and health information on the identity-entry, creation, and editing surfaces.

| Scope | Approved Test Cases | Passed | Failed | Blocked | Manual | Not Yet Automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-014 blocking completion | 1 | 1 | 0 | 0 | 0 | 0 |

TC-014-01 was executed as an automated acceptance test against both served
surfaces (`/` and `/app`). The notice content and surface availability were
also inspected in the served markup and shared stylesheet: the notice is not
hidden and is styled as a visible notice on each surface. `/app` is the
shared record creation/editing surface.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-SCP-003; CR-FR-023; CR-BR-010 | AC-037 | STORY-014 | STORY-014 | Blocking completion | TC-014-01 | **PASSED** — identity entry, record creation, and record editing visibly state that only demo or synthetic data may be used and prohibit all three specified real-data categories. |

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- Focused acceptance command, run from `backend`:
  `python -m pytest tests\acceptance\test_story_014_demo_data_and_https.py -q`
  — **2 passed** (the parameterized checks cover identity entry and the
  shared create/edit surface); two existing dependency deprecation warnings.
- Full backend regression command, run from `backend`:
  `python -m pytest -q` — **271 passed, 1 skipped** in 46.32 seconds.
  The skip is the existing STORY-009 archived-tag placeholder. The run emitted
  17 deprecation warnings; no test failed.
- Developer-owned tests were included in the full backend suite and passed.
- The exact production commit under test was
  `796074f9788662a0488f7e6b62fed6bae1289033`. No production files were
  changed during validation.

## Deferred Non-blocking Integration Validation

None. No later-Story integration-validation dependency is assigned to
STORY-014.

## Uncovered Acceptance Criteria

None within STORY-014's approved scope. AC-032 is allocated to STORY-016 as
blocking integrated local-operation validation. TC-016-03 is outside this
Story's validation scope. HTTPS and deployed operation are not acceptance
requirements under the approved v1.4 baseline and were not treated as defects.

## Legacy Tracking Note

The inherited Jira mapping discrepancy previously noted in TR-027 is a
tracking/mapping issue, not a product acceptance failure. Jira was not
modified. TR-027 remains unchanged historical evidence for the superseded
Requirement Definition v1.3 baseline and is not the result for v1.4.

## Recommendation

**READY FOR REVIEW** — TC-014-01 passed, all STORY-014 acceptance coverage in
the approved TEST-001 v2.2 is satisfied, and the full backend regression suite
passed. This result applies to the exact tested production commit above.
