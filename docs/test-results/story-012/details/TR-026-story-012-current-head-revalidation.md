# STORY-012 Current-HEAD Independent Revalidation

**Test Run ID:** TR-026
**Coverage Story or Stories:** STORY-002, STORY-009, STORY-012, STORY-013, STORY-015
**Execution-owning Story:** STORY-012
**Validated commit:** `1391adfc0f9585cae4224aa597ad871e78d6479f`
**Validated production commit:** `f35ea906cedf49abd28fe07cececc615b146f3e9`
**Validated production tree:** `43b5f240439fd9c7ae16db8ab35aabd6c0e0e568`
**Report path:** `docs/test-results/story-012/details/TR-026-story-012-current-head-revalidation.md`

## Overall Status

**PASSED**

## Summary

Independently re-executed validation on the exact clean PR HEAD, rather than
relying on TR-025's prior execution. The approved Requirement Definition v1.3,
PLAN-001 v1.2, and TEST-001 v2.1 are unchanged. The only changes between
the production fix commit and the tested HEAD are the TR-025 report and
validation-status page; no production or executable test files changed.
Developer-owned archival, audit, and Chrome regression tests passed in the
full suite. Chrome was available on the Windows validation host.

| Scope | Approved cases | Passed | Failed | Blocked | Manual | Not yet automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-012 blocking completion | 5 | 5 | 0 | 0 | 0 | 0 |
| Owned deferred integration | 6 | 5 plus one partial | 0 | 0 | 0 | 0 |
| Latest browser review regressions | 2 findings | 2 | 0 | 0 | 0 | 0 |

The partial result is TC-015-01: its archive/restore audit legs passed,
while the STORY-011 comment-deletion event leg remains an approved
non-blocking deferred integration dependency.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-020; CR-BR-007 | AC-020 | STORY-012 | STORY-012 | Blocking completion | TC-012-01 | **PASSED** — archived Draft, Proposed, Accepted, Rejected, and Superseded records remained discoverable; in-flight card actions stayed locked across superseded refreshes. |
| CR-FR-020–021; CR-BR-007 | AC-003 | STORY-012 | STORY-012 | Blocking completion | TC-012-02 | **PASSED** — non-administrators were denied archive and restore without state changes. |
| CR-FR-021 | AC-021 | STORY-012 | STORY-012 | Blocking completion | TC-012-03 | **PASSED** — restoring each archived lifecycle preserved the exact pre-archive state. |
| CR-FR-020; CR-BR-014 | AC-026 | STORY-012 | STORY-012 | Blocking completion | TC-012-04 | **PASSED** — active Proposed replacement blocked original archival until either review outcome. |
| CR-FR-021, CR-FR-030; CR-BR-019 | AC-047 | STORY-012 | STORY-012 | Blocking completion | TC-012-05 | **PASSED** — restored Abandoned replacement stayed linked, Draft, abandoned, and immutable. |
| CR-USR-006, CR-USR-009; CR-BR-013 | AC-003 | STORY-002, STORY-007, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-002-02 | **PASSED** — non-administrator archive/restore/replacement/abandonment matrix denied. |
| CR-FR-015–016; CR-BR-009 | AC-015 | STORY-009 | STORY-012 | Non-blocking integration-validation | TC-009-01 | **PASSED for archived leg** — archived records returned in exact-tag discovery. |
| CR-FR-029; CR-OOS-007 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-01 | **PASSED for archival conditions** — archived and Abandoned records could not be deleted and stayed retrievable. |
| CR-SCP-001; CR-FR-029 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-02 | **PASSED** — permitted archive/restore retained records. |
| CR-NFR-007 | AC-033 | STORY-015 and governed-action Stories | STORY-012 | Non-blocking integration-validation | TC-015-01 | **PARTIAL, NON-BLOCKING** — attributed immutable archive/restore events and concurrency passed; STORY-011 comment deletion unavailable. |
| CR-FR-014; CR-NFR-003, CR-NFR-008 | AC-013, AC-034 | STORY-015, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-015-03 | **PASSED for archival scope** — no expiry/deletion path for archived records or audit entries; repeated retrieval preserved them. |

## Review Finding Retest

The independent headless-Chrome test loaded actual `app.html` and `app.js`
against controlled API responses. It verified that the edit warning appears
in the form without sending an archive POST or losing edits; Save/Cancel
replace/clear it. It also verified target-record mutation controls stay locked
while archive/restore is pending, through a filter-driven refresh and while
the archive/restore refresh is superseded by another pending list request.
Other records remain usable, failed archival restores controls, and successful
archive/restore replaces stale actions. The developer Chrome regression
separately exercised the superseded archive refresh.

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- From `backend`:
  `python -m pytest -q tests\acceptance\test_story_012_review_ui_retest.py tests\acceptance\test_story_012_archive_restore.py tests\test_archival.py tests\test_audit.py tests\acceptance\test_story_007_replacement_versions.py tests\acceptance\test_story_009_exact_tag_discovery.py`
  — **50 passed, 1 skipped**, 2 dependency warnings.
- From `backend`: `python -m pytest -q` — **263 passed, 1 skipped**,
  17 existing dependency-deprecation warnings.
- The sole skip is the unchanged STORY-009 archived-tag placeholder; the
  archived exact-tag leg ran in the STORY-012 acceptance suite.
- No live-server or Linux/macOS browser run was performed: Chrome tests used
  actual UI files with deterministic mocked API responses on Windows. The
  process-local retention checks do not establish restart durability.
- The working tree was clean before execution. PR #33 remote head equaled
  the validated commit; the production change was published in its parent.

## Deferred Non-blocking Integration Validation

| Test Case | Coverage Story or Stories | Execution-owning Story | Required capability and regression scope | Reason non-blocking |
| --- | --- | --- | --- | --- |
| TC-015-01 | STORY-015 and governed-action Stories | STORY-012 | Trigger and verify the comment-deletion audit category when STORY-011 becomes available. | TEST-001 v2.1 designates integration-validation; archive and restore event legs passed. |

## Uncovered Acceptance Criteria

None for STORY-012 blocking completion. The remaining TC-015-01 category
does not mean STORY-011 or STORY-015 is fully passed.

## Recommendation

**READY FOR REVIEW** for tested HEAD
`1391adfc0f9585cae4224aa597ad871e78d6479f` and its production commit
`f35ea906cedf49abd28fe07cececc615b146f3e9`. Human governance and audit
review remains required; a later production change needs another retest.
