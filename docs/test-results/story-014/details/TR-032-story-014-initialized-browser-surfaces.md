# STORY-014 Initialized Browser Surfaces Validation

**Test Run ID:** TR-032
**Coverage Story or Stories:** STORY-014
**Execution-owning Story:** STORY-014
**Validated commit:** `e9df3afaa12912978812d352de28da89ef452749`
**Report path:** `docs/test-results/story-014/details/TR-032-story-014-initialized-browser-surfaces.md`

## Overall Status

**PASSED**

## Summary

Independently validated the exact commit against Requirement Definition v1.4
Approved, PLAN-001 v1.4 Approved, and TEST-001 v2.2 Approved. STORY-014's
blocking acceptance scope is AC-037 / TC-014-01. The test runs the actual
local FastAPI application, launches headless Chrome, opens the served
identity-entry page with its production JavaScript and stylesheet, waits for
Mock identities to load, and evaluates rendered notice visibility. It then
selects the first Mock identity through the actual UI, waits for navigation to
`/app` and owner options to load, and evaluates the same visibility conditions
on the initialized record create/edit surface.

| Scope | Approved Test Cases | Passed | Failed | Blocked | Manual | Not Yet Automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-014 blocking completion | 1 | 1 | 0 | 0 | 0 | 0 |

The browser lookup supports `chrome`, `chromium`, `google-chrome`, and
`msedge`, plus standard Windows install locations.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-SCP-003; CR-FR-023; CR-BR-010 | AC-037 | STORY-014 | STORY-014 | Blocking completion | TC-014-01 | **PASSED** — required notice content was served and visible in the initialized identity-entry UI and in the initialized record create/edit UI after Mock identity selection. |

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- Focused acceptance command, run from `backend`:
  `python -m pytest tests\acceptance\test_story_014_demo_data_notice.py -q`
  — **3 passed** in 9.17 seconds; the two browser-dependent checks both ran
  in headless Chrome. Two existing dependency deprecation warnings were
  emitted.
- Full backend suite, run from `backend`:
  `python -m pytest -q` — **272 passed, 1 skipped** in 57.40 seconds.
  The skip is the existing STORY-009 archived-tag placeholder. Seventeen
  deprecation warnings were emitted; no test failed.
- The test starts the application using a temporary audit database and
  terminates both browser and application processes after the run.

## Deferred Non-blocking Integration Validation

None is assigned to STORY-014 in TEST-001 v2.2.

## Uncovered Acceptance Criteria

None within STORY-014's approved scope. AC-032 and TC-016-03 are blocking
local-operation coverage for STORY-016. Deployment and HTTPS are not
acceptance requirements under Requirement Definition v1.4 and were not
asserted.

## Recommendation

**READY FOR REVIEW** — TC-014-01 passed against both fully initialized browser
surfaces, and the full backend regression suite passed. This result applies
to commit `e9df3afaa12912978812d352de28da89ef452749`.
