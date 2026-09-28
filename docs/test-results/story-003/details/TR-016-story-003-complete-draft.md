# STORY-003 Complete Draft Validation

**Test Run ID:** TR-016
**Story:** STORY-003 — Create a Complete Draft
**Validated commit:** `146aaa5a560afa8d2cbe659c7b08150c1799e402`
**Report path:** `docs/test-results/story-003/details/TR-016-story-003-complete-draft.md`
**Validation date:** 2026-09-28

## Overall Status

BLOCKED

## Summary

All three approved STORY-003 Test Cases passed their executed acceptance
checks. The targeted Developer-owned unit and Validation-Agent acceptance
suite passed **88 tests**. The full backend regression passed **151 tests**
with **1 previously approved STORY-009 test skipped**.

TC-003-02 received additional Validation-Agent-owned acceptance coverage to
exercise the approved incomplete-Draft submission precondition directly. The
approved scenario was established with a controlled test fixture because the
normal create endpoint enforces all fields before it can retain a Draft.
Actual submission attempts correctly identified each missing field and left
the record in Draft.

TC-003-03 was additionally checked in headless Chrome on both the entry screen
and the shared create/edit screen; the complete data-boundary notice rendered
on both pages.

The run is formally **BLOCKED** because the required Developer Agent report
`READY FOR INDEPENDENT VALIDATION` was not found in PR #8 or the available
repository evidence. This does not negate the passing test observations, but
the required readiness input is unconfirmed. The PR is merged; the tested
production source is current commit
`146aaa5a560afa8d2cbe659c7b08150c1799e402`.

## Requirement Coverage

| Requirement | Acceptance Criterion | Story | Test Case | Result |
| --- | --- | --- | --- | --- |
| CR-FR-003–005, CR-FR-006A | AC-002 | STORY-003 | TC-003-01 | PASSED — complete Draft retained with fields, tags, selected Mock author, and distinct owner |
| CR-FR-004 | AC-004 | STORY-003 | TC-003-02 | PASSED — each missing field and a multi-field omission prevented submission, identified all gaps, and kept the record in Draft |
| CR-FR-023; CR-BR-010 | AC-037 | STORY-003 | TC-003-03 | PASSED — complete notice rendered on entry and create/edit screens and retained on a Draft |

## Failed Tests

No Test Case failed. No Failure Report is applicable.

## Regression Result

Targeted command: `tests/test_decision_records.py` and
`tests/acceptance/test_story_003_complete_draft.py` — **88 passed**.

Full backend regression — **151 passed, 1 skipped**. The skipped test is the
previously Human-approved STORY-009 archived-discovery deferral to STORY-012.
It is unrelated to STORY-003. Fifteen deprecation warnings were emitted by
FastAPI/Starlette/AnyIO dependencies; they did not cause test failures.

## Uncovered Acceptance Criteria

No mapped STORY-003 Acceptance Criterion remains untested in this run.
TC-003-01 exercised record creation through the API; a browser-driven form
submission was not performed. TC-003-03 separately verified browser-rendered
visibility of the entry and shared create/edit notices in headless Chrome.

## Recommendation

BLOCKED

Record the Developer Agent's explicit readiness report before treating this
run as satisfying the required independent-validation handoff. The observed
test results support the STORY-003 behaviors at the validated production
commit; any production-code change requires retesting.
