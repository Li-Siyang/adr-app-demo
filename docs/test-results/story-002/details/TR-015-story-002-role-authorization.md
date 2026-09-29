# STORY-002 Role Authorization Validation

**Test Run ID:** TR-015
**Story:** STORY-002 — Administer Additive Roles and Approvers
**Validated commit:** `146aaa5a560afa8d2cbe659c7b08150c1799e402`
**Report path:** `docs/test-results/story-002/details/TR-015-story-002-role-authorization.md`
**Validation date:** 2026-09-28

## Overall Status

BLOCKED

## Summary

The approved scope contains five Test Cases: four passed and one remains
blocked. A session-local Python 3.12.10 runtime and the backend development
dependencies were installed (`pytest 8.4.2`, `FastAPI 0.141.1`,
`Pydantic 2.13.5`, `httpx 0.28.1`). The Developer-owned governance unit tests and
Validation-Agent acceptance tests passed; the full backend regression suite
also passed with the previously approved STORY-009 skip.

TC-002-02 cannot be fully evaluated because its required archive, restore,
replacement creation, and replacement-Draft abandonment actions are not
implemented in the current backend. The PR check rollup contains no reported
checks, and no explicit `READY FOR INDEPENDENT VALIDATION` report was found.
This report therefore does not claim complete Story validation or review
readiness.

The production code tested is from commit
`146aaa5a560afa8d2cbe659c7b08150c1799e402`. The validation-owned acceptance
tests were expanded in the working tree to exercise actual proposal decisions
for TC-002-03 through TC-002-05; those test changes are not part of that commit.

## Requirement Coverage

| Requirement | Acceptance Criterion | Story | Test Case | Result |
| --- | --- | --- | --- | --- |
| CR-USR-004; CR-BR-001 | AC-003 | STORY-002 | TC-002-01 | PASSED |
| CR-USR-006, CR-USR-009; CR-BR-013 | AC-003 | STORY-002 | TC-002-02 | BLOCKED — archive, restore, replacement creation, and replacement abandonment actions are not implemented |
| CR-FR-009 | AC-006 | STORY-002 | TC-002-03 | PASSED |
| CR-USR-005; CR-FR-010; CR-BR-002 | AC-007 | STORY-002 | TC-002-04 | PASSED |
| CR-USR-010; CR-BR-015 | AC-023 | STORY-002 | TC-002-05 | PASSED |

All five cases have automated acceptance coverage in
`backend/tests/acceptance/test_story_002_additive_roles.py`. Seventeen
validation-owned acceptance tests ran and passed. Four Developer-owned
governance unit tests ran and passed. No manual test was completed.

## Failed Tests

No Test Case produced a failing result. No Failure Report is applicable.

## Regression Result

Targeted command: Developer-owned `tests/test_governance.py` plus the
STORY-002 acceptance suite — **21 passed** (4 unit tests and 17 acceptance
tests), run with the backend directory on `sys.path`.

Full backend regression: **141 passed, 1 skipped**. The skipped test is the
previously approved STORY-009 archived-discovery deferral to STORY-012; it is
unrelated to STORY-002. Five deprecation warnings were emitted by the current
FastAPI/Starlette/AnyIO dependencies; they did not cause test failures.

## Uncovered Acceptance Criteria

AC-003 is only partially verified: TC-002-01 passed, but TC-002-02 remains
blocked for its later-Story governed actions. AC-006, AC-007, and AC-023
passed their mapped tests, including actual denied and successful proposal
decision requests and record-state checks.

## Recommendation

BLOCKED

Implement the dependent archive, restore, replacement-creation, and
replacement-abandonment operations under their approved Stories, then rerun
all of TC-002-02 and relevant regression cases. Record the Developer Agent's
readiness report before treating this Story as ready for review.
