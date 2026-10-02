# STORY-013 Linked Replacement Review Retest

**Test Run ID:** TR-028
**Coverage Story or Stories:** STORY-013
**Execution-owning Story:** STORY-012
**Validated commit:** `d928ffad3ab81fd2d2e97e5e173227de2a497da0`
**Report path:** `docs/test-results/story-013/details/TR-028-story-013-linked-replacement-retest.md`

## Overall Status

**PASSED**

## Summary

Independently re-executed the approved STORY-013 coverage after two PR review
findings identified invalid replacement test fixtures in TR-027. The corrected
tests create an Accepted original and a linked replacement through the
supported APIs, then submit, abandon, archive, or restore as applicable.
Both sides of each replacement link are checked before the deletion attempt.
Production behavior was unchanged. The approved Requirement Definition v1.3,
PLAN-001 v1.2, and TEST-001 v2.1 are unchanged.

| Scope | Approved cases | Passed | Failed | Blocked | Manual | Not yet automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-013 AC-045 | 2 | 2 | 0 | 0 | 0 | 0 |

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-029; CR-OOS-007 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-01 | **PASSED** — every Mock identity received 405 for DELETE and 422 for soft-delete updates against real Draft, Proposed, Accepted, Rejected, Superseded, active Draft/Proposed replacements, Abandoned replacements, and archived/archived-Abandoned records. Linked replacements and originals remained available with intact links and unchanged list snapshots. |
| CR-SCP-001; CR-FR-029 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-02 | **PASSED** — archived records, including Abandoned replacements, were restored without deletion or lifecycle change under existing rules; adjacent archive/restore integration regressions passed. |

## Failed Tests

None. No Failure Reports apply. The two PR comments concerned the *test
fixtures*, not a demonstrated product defect; both are addressed in this run.

## Regression Result

- On the exact pushed commit from `backend`:
  `python -m pytest -q -rs tests/acceptance/test_story_013_record_retention.py tests/test_decision_records.py tests/acceptance/test_story_007_replacement_versions.py tests/acceptance/test_story_012_archive_restore.py tests/test_archival.py`
  — **123 passed**.
- Full backend regression with the same executable tree:
  `python -m pytest -q -rs` — **288 passed, 1 skipped**, 17 existing dependency
  deprecation warnings. The skip is the existing Human-deferred STORY-009
  archived exact-tag test; it is not STORY-013 coverage.
- The exact reviewed production and executable-test files were committed and
  pushed before the final focused retest. No production code changed.

## Deferred Non-blocking Integration Validation

None remaining for STORY-013. STORY-007 replacement and STORY-012
archive/restore capabilities supplied valid fixtures for the approved
non-blocking TC-013-01/02 integration coverage.

## Uncovered Acceptance Criteria

None for AC-045. UI source inspection for absence of a record-delete action
remains as recorded in TR-027; this retest concentrates on valid HTTP fixtures
and archive/restore behavior.

## Recommendation

**READY FOR REVIEW** for tested commit
`d928ffad3ab81fd2d2e97e5e173227de2a497da0`. Any later production or
executable-test changes require independent retest.
