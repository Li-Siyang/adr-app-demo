# STORY-013 Linked Record Retention Validation

**Test Run ID:** TR-031
**Coverage Story or Stories:** STORY-013
**Execution-owning Story:** STORY-012
**Validated commit:** `9d2127b3d285662ed87bba5cd47d0108f2622eb8`
**Report path:** `docs/test-results/story-013/details/TR-031-story-013-linked-retention-validation.md`

## Overall Status

**PASSED**

## Summary

In the currently selected Validation Agent role, re-evaluated AC-045 against
Requirement Definition v1.3, PLAN-001 v1.2 APPROVED, and TEST-001 v2.1
APPROVED rather than accepting TR-028's assertion. The worktree was clean at
the tested PR commit. Commit `d928ffa` changed only developer and acceptance
tests; later commits through the tested SHA changed only validation documents.
The Developer-owned tests previously passed and were rerun here. No production
code or approved artifacts were changed for this run.

| Scope | Approved cases | Passed | Failed | Blocked | Manual | Not yet automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-013 AC-045 | 2 | 2 | 0 | 0 | 0 | 0 |

This is a new requirement-driven evaluation performed after switching to the
Validation Agent role **in the same session**. It is not a claim that another
person or a separate session performed the review. The earlier assertion that
the approved workflow requires a separate session was incorrect; the workflow
requires independent comparison against approved expectations, not a specific
session boundary.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-029; CR-OOS-007 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-01 | **PASSED (Automated API + UI-source inspection):** all configured Mock identities received 405 for permanent DELETE and 422 for attempted soft deletion via record update; records and list snapshots remained unchanged. The eleven API-generated fixtures cover Draft, Proposed, Accepted, Rejected, Superseded, valid active Draft/Proposed replacements, Abandoned replacements, archived records, and archived-Abandoned replacements. Valid replacements point to the Accepted original, and the original lists the replacement ID before the attempt. The shipped record UI has archive/restore but no delete-record action. |
| CR-SCP-001; CR-FR-029 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-02 | **PASSED (Automated API):** archived fixtures, including Abandoned replacements, restored without losing lifecycle or replacement condition; STORY-012 lifecycle, guard, discovery, and administrator-only regressions passed. |

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- At the exact tested commit, from `backend`:
  `python -m pytest -q -rs tests/acceptance/test_story_013_record_retention.py tests/acceptance/test_story_012_archive_restore.py tests/acceptance/test_story_007_replacement_versions.py tests/test_decision_records.py tests/test_archival.py`
  — **123 passed**.
- `python -m pytest -q -rs` — **288 passed, 1 skipped**, 17 pre-existing
  dependency warnings. The skip is the Human-deferred STORY-009 archived-tag
  placeholder; STORY-012's actual archived discovery test ran successfully.
- Inspected record routes and update schema: no decision-record DELETE route,
  and unknown soft-delete fields are forbidden. Inspected `app.js` and
  `app.html`: the only DELETE call in the UI clears the Mock session, not a
  record. Comment-content deletion remains separate and was not modified.
- No live browser interaction was performed; UI-action absence was inspected
  in the shipped source, while API behavior was exercised via TestClient.

## Deferred Non-blocking Integration Validation

None for TC-013-01/02. The STORY-003 retained-record Start capability and
STORY-007/012 replacement/archival integration-validation fixtures are
available and were executed. No Completion dependency is approved.

## Uncovered Acceptance Criteria

None for STORY-013 AC-045.

## Recommendation

**READY FOR REVIEW** for the tested executable tree at
`9d2127b3d285662ed87bba5cd47d0108f2622eb8`. Human review remains required;
any later production or executable-test change requires an impact assessment
and, if affected, new validation.
