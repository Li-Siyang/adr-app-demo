# STORY-014 Rendered Notice Visibility Retest

**Test Run ID:** TR-030
**Coverage Story or Stories:** STORY-014
**Execution-owning Story:** STORY-014
**Validated commit:** `801448e50df85e78abd64a885329a783cf89c86c`
**Report path:** `docs/test-results/story-014/details/TR-030-story-014-rendered-notice-visibility.md`

## Overall Status

**PASSED**

## Summary

Retested STORY-014 against Requirement Definition v1.4 Approved, PLAN-001
v1.4 Approved, and TEST-001 v2.2 Approved (2026-10-02). The approved
blocking scope remains AC-037 / TC-014-01. The test now checks both approved
notice language in the served response and actual browser-rendered visibility
of the notice using headless Chrome on identity entry and the shared record
creation/editing surface.

| Scope | Approved Test Cases | Passed | Failed | Blocked | Manual | Not Yet Automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-014 blocking completion | 1 | 1 | 0 | 0 | 0 | 0 |

The browser assertion loads each actual static surface with its shared
stylesheet and inspects the notice and every ancestor's computed display,
visibility, opacity, and rendered bounds. The `/app` served response also
confirms the shared record form is present.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-SCP-003; CR-FR-023; CR-BR-010 | AC-037 | STORY-014 | STORY-014 | Blocking completion | TC-014-01 | **PASSED** — required content is served on `/` and `/app`; headless Chrome confirms the notice is rendered and visible on both surfaces. |

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- Focused acceptance command, run from `backend`:
  `python -m pytest tests\acceptance\test_story_014_demo_data_notice.py -q`
  — **2 passed** in 4.88 seconds; two existing dependency deprecation
  warnings. Chrome was available and both rendered-visibility checks executed.
- Full backend suite, run from `backend`:
  `python -m pytest -q` — **271 passed, 1 skipped** in 37.95 seconds.
  The skip is the existing STORY-009 archived-tag placeholder. Seventeen
  deprecation warnings were emitted; no test failed.
- The test module was renamed from its former HTTPS-related name to
  `test_story_014_demo_data_notice.py`. TR-028 and TR-029 retain the exact
  command names that were run for those historical reports; this report uses
  the current module path.
- No production source behavior changed in this retest commit. The test gained
  the real-browser visibility assertion and the approved Plan's stale
  pre-approval readiness text was reconciled with the approved v1.4/v2.2
  baseline.

## Deferred Non-blocking Integration Validation

None is assigned to STORY-014 in TEST-001 v2.2.

## Uncovered Acceptance Criteria

None within STORY-014's approved scope. AC-032 and TC-016-03 are blocking
local-operation coverage for STORY-016. Deployed environments and HTTPS are
not acceptance requirements under the approved v1.4 baseline and were not
tested or treated as defects.

## Recommendation

**READY FOR REVIEW** — TC-014-01 passes its served-content and browser
visibility assertions on both required surfaces, and the full backend
regression suite passes. This result applies to commit
`801448e50df85e78abd64a885329a783cf89c86c`.
