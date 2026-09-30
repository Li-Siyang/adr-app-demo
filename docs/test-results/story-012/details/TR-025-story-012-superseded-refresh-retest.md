# STORY-012 Superseded Refresh Independent Retest

**Test Run ID:** TR-025
**Coverage Story or Stories:** STORY-002, STORY-009, STORY-012, STORY-013, STORY-015
**Execution-owning Story:** STORY-012
**Validated commit:** `f35ea906cedf49abd28fe07cececc615b146f3e9`
**Validated production tree:** `43b5f240439fd9c7ae16db8ab35aabd6c0e0e568`
**Report path:** `docs/test-results/story-012/details/TR-025-story-012-superseded-refresh-retest.md`

## Overall Status

**PASSED**

## Summary

Retested the exact published production tree after review findings 4144182098
(superseded refresh unlocking stale record actions) and 4144182167 (browser
discovery restricted to Windows). The working tree contained no uncommitted
production changes. Requirement v1.3, PLAN-001 v1.2, and TEST-001 v2.1 remain
approved and unchanged. TR-024 and prior reports apply only to their recorded
production SHAs.

| Scope | Approved cases | Passed | Failed | Blocked | Manual | Not yet automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-012 blocking completion | 5 | 5 | 0 | 0 | 0 | 0 |
| Owned deferred integration | 6 | 5 plus one partial | 0 | 0 | 0 | 0 |
| Latest review findings | 2 | 2 | 0 | 0 | 0 | 0 |

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-020; CR-BR-007 | AC-020 | STORY-012 | STORY-012 | Blocking completion | TC-012-01 | **PASSED** — every lifecycle remained archived, retained, and discoverable; stale-card controls remained locked through superseding list requests. |
| CR-FR-020–021; CR-BR-007 | AC-003 | STORY-012 | STORY-012 | Blocking completion | TC-012-02 | **PASSED** — non-administrator archive and restore denied. |
| CR-FR-021 | AC-021 | STORY-012 | STORY-012 | Blocking completion | TC-012-03 | **PASSED** — each restored lifecycle matched its pre-archive state. |
| CR-FR-020; CR-BR-014 | AC-026 | STORY-012 | STORY-012 | Blocking completion | TC-012-04 | **PASSED** — original archival denied while replacement Proposed; both review outcomes removed that guard. |
| CR-FR-021, CR-FR-030; CR-BR-019 | AC-047 | STORY-012 | STORY-012 | Blocking completion | TC-012-05 | **PASSED** — restored Abandoned replacement retained Draft, Abandoned, link, and immutability. |
| CR-USR-006, CR-USR-009; CR-BR-013 | AC-003 | STORY-002, STORY-007, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-002-02 | **PASSED** — administrator-only matrix denied non-admin actions without state changes. |
| CR-FR-015–016; CR-BR-009 | AC-015 | STORY-009 | STORY-012 | Non-blocking integration-validation | TC-009-01 | **PASSED for archived leg** — exact-tag discovery includes archived records; unchanged historical placeholder skipped. |
| CR-FR-029; CR-OOS-007 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-01 | **PASSED for archival conditions** — archived and Abandoned records resisted deletion and remained retrievable. |
| CR-SCP-001; CR-FR-029 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-02 | **PASSED** — permitted archive/restore did not delete records. |
| CR-NFR-007 | AC-033 | STORY-015 and governed-action Stories | STORY-012 | Non-blocking integration-validation | TC-015-01 | **PARTIAL, NON-BLOCKING** — attributed immutable archival events and concurrent transitions passed; STORY-011 comment deletion unavailable. |
| CR-FR-014; CR-NFR-003, CR-NFR-008 | AC-013, AC-034 | STORY-015, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-015-03 | **PASSED for archival scope** — archived records and audit entries have no expiry/deletion path and remain retrievable. |

## Review Finding Retest

The independent `tests\acceptance\test_story_012_review_ui_retest.py` uses
actual `app.html` and `app.js` in headless Chrome against controlled API
responses. During a delayed restore refresh, a newer filter request superseded
the first; resolving the first request left the old Restore button disabled
until the second request rendered the new Archive button. The developer-owned
browser regression independently exercised the equivalent archive race.
Other records stayed operable, failed archive restored controls, and the edit
warning remained in the form. Browser lookup now checks Chrome/Chromium/Edge
on PATH before the Windows fallback; this execution used installed Windows
Chrome, **not** a Linux or macOS environment.

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- From `backend`:
  `python -m pytest -q tests\acceptance\test_story_012_review_ui_retest.py tests\acceptance\test_story_012_archive_restore.py tests\test_archival.py tests\test_audit.py tests\acceptance\test_story_007_replacement_versions.py tests\acceptance\test_story_009_exact_tag_discovery.py`
  — **50 passed, 1 skipped**.
- `python -m pytest -q` — **263 passed, 1 skipped**, including both Chrome
  regressions; 17 existing dependency-deprecation warnings.
- One unchanged STORY-009 historical placeholder is skipped; the archived-tag
  leg ran separately. `git diff --check` passed.
- Git HTTPS was unreachable; the production fix was published using GitHub
  Git objects after verifying the remote tree equals the local commit tree.
  Remote branch and local branch were aligned to the exact SHA above.

## Deferred Non-blocking Integration Validation

| Test Case | Coverage Story or Stories | Execution-owning Story | Required capability and regression scope | Reason non-blocking |
| --- | --- | --- | --- | --- |
| TC-015-01 | STORY-015 and governed-action Stories | STORY-012 | Verify the STORY-011 comment-deletion event when that capability is available. | TEST-001 v2.1 designates integration-validation; archive/restore audit legs passed. |

## Uncovered Acceptance Criteria

None for STORY-012 blocking completion. The deferred comment-deletion category
is not claimed passed, nor are predecessor Stories represented as fully passed.

## Recommendation

**READY FOR REVIEW** for production commit
`f35ea906cedf49abd28fe07cececc615b146f3e9`. Human governance and audit
review remains required; any later production change needs a fresh retest.
