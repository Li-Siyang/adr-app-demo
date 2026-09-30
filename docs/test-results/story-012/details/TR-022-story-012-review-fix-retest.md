# STORY-012 Review Fix Independent Retest

**Test Run ID:** TR-022
**Coverage Story or Stories:** STORY-002, STORY-009, STORY-012, STORY-013,
STORY-015
**Execution-owning Story:** STORY-012
**Validated commit:** `fedeb6b9eae10cc864f87225abc774f23d040821`
**Validated production tree:** `fc1cc73b26a6ac2800afce565e85dd18ac422dde`
**Report path:** `docs/test-results/story-012/details/TR-022-story-012-review-fix-retest.md`

## Overall Status

**PASSED**

## Summary

TR-022 independently retested the two PR review findings against the exact
review-fix production SHA above, reran all five blocking STORY-012 cases,
exercised the executable deferred integration cases and directly related
replacement/discovery scenarios, and ran the complete backend regression.
The approved Requirement Definition v1.3, PLAN-001 v1.2, and TEST-001 v2.1
remain unchanged. Developer-owned tests had passed at handoff and passed again
in this run. The worktree was clean before this run; no production code was
changed during independent validation.

| Scope | Approved cases | Passed | Failed | Blocked | Manual browser | Not automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-012 blocking completion | 5 | 5 | 0 | 0 | 0 | 0 |
| Owned deferred integration validation | 6 | 5 plus one partial | 0 | 0 | 0 | 0 |
| PR review findings | 2 | 2 | 0 | 0 | 2 | 0 |

The partial deferred case is TC-015-01: its archive/restore audit leg passed;
the absent STORY-011 comment-deletion category is a non-blocking limitation,
not a claimed pass for all STORY-015 event categories.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-020; CR-BR-007 | AC-020 | STORY-012 | STORY-012 | Blocking completion | TC-012-01 | **PASSED** — all five lifecycle statuses archived, retained, directly retrieved, and discovered by exact tag; a duplicate-title browser fixture exposed a distinct archive/restore accessible name containing title and ID for each record. |
| CR-FR-020–021; CR-BR-007 | AC-003 | STORY-012 | STORY-012 | Blocking completion | TC-012-02 | **PASSED** — non-administrators could not archive or restore; browser rendering exposed no archive/restore controls for a non-administrator. |
| CR-FR-021 | AC-021 | STORY-012 | STORY-012 | Blocking completion | TC-012-03 | **PASSED** — restore returned each lifecycle to its pre-archive state. |
| CR-FR-020; CR-BR-014 | AC-026 | STORY-012 | STORY-012 | Blocking completion | TC-012-04 | **PASSED** — an active Proposed replacement blocked original archival; resolving review to Accepted or Rejected ended the block. Browser rendering of a Draft replacement with an archived original hid only Submit Draft, retaining Edit Draft; restore exposed submission again. |
| CR-FR-021, CR-FR-030; CR-BR-019 | AC-047 | STORY-012 | STORY-012 | Blocking completion | TC-012-05 | **PASSED** — Abandoned replacement remained linked, Draft, Abandoned, and immutable after archive/restore. |
| CR-USR-006, CR-USR-009; CR-BR-013 | AC-003 | STORY-002, STORY-007, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-002-02 | **PASSED** — non-administrator archive, restore, replacement creation and abandonment denied with unchanged state. |
| CR-FR-015–016; CR-BR-009 | AC-015 | STORY-009 | STORY-012 | Non-blocking integration-validation | TC-009-01 | **PASSED** — archived exact-tag matches across lifecycle statuses returned; the unchanged historical placeholder remains skipped, but its archival leg ran here. |
| CR-FR-029; CR-OOS-007 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-01 | **PASSED** — deletion attempts on archived and Abandoned records denied for every configured role and records remained retrievable. |
| CR-SCP-001; CR-FR-029 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-02 | **PASSED** — otherwise-permitted restore retained the same record. |
| CR-NFR-007 | AC-033 | STORY-015 and governed-action Stories | STORY-012 | Non-blocking integration-validation | TC-015-01 | **PARTIAL, NON-BLOCKING** — archive and restore audit attribution and concurrency regressions passed; the unavailable STORY-011 comment-deletion event leg remains deferred. |
| CR-FR-014; CR-NFR-003, CR-NFR-008 | AC-013, AC-034 | STORY-015, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-015-03 | **PASSED for assigned archival scope** — archived records and audit entries remained retrievable and exposed no expiry or deletion path. |

Neither earlier STORY-002, STORY-009, STORY-013, nor STORY-015 is represented
as fully PASSED by this run; the table records only their assigned integration
scope.

## Review Finding Retest

| Finding | Expected behavior | Independent execution and actual result |
| --- | --- | --- |
| `backend/app/static/app.js` archive/restore accessible names | The visible label remains, while the accessible name identifies the affected record even if titles repeat. | **PASSED** — headless Chrome rendered two same-title records and observed `Archive record: Duplicate title (other)` and `Restore record: Duplicate title (source)`, with unchanged visible labels. |
| `backend/app/static/app.js` replacement submission after original archival | Hide the unavailable submit action only while the linked original is archived; keep editing available and restore submission availability when the original is restored. | **PASSED** — independent headless Chrome fixtures rendered archived and restored originals: Submit Draft absent/present respectively; Edit Draft present in both. Backend tests also confirmed archived-original submission is rejected until restored. |

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- From `backend`, `python -m pytest -q tests\acceptance\test_story_012_archive_restore.py tests\test_archival.py tests\test_audit.py tests\acceptance\test_story_007_replacement_versions.py tests\acceptance\test_story_009_exact_tag_discovery.py` — **49 passed, 1 skipped**.
- From `backend`, `python -m pytest -q` — **261 passed, 1 skipped**.
- Independent Python-driven headless Chrome rendering of the actual
  `backend/app/static/app.js` and `backend/app/static/app.html` with isolated,
  deterministic mocked API responses — **3 fixture combinations passed**:
  archived original/admin, restored original/admin, archived original/non-admin.
  The fixtures checked duplicate-title action names, submit/edit gating, and
  non-administrator control visibility. This was a browser-rendered UI check,
  not a live-server end-to-end exercise or a screen-reader assessment.
- The historical skip is the unchanged STORY-009 archived-tag placeholder
  deferred to STORY-012; this run separately executed its archived-record leg.
- `git diff --check` passed. The full suite reported 17 existing dependency
  deprecation warnings without failures.

## Deferred Non-blocking Integration Validation

| Test Case | Coverage Story or Stories | Execution-owning Story | Required capability and remaining regression scope | Reason non-blocking |
| --- | --- | --- | --- | --- |
| TC-015-01 | STORY-015 and governed-action Stories | STORY-012 | STORY-011 comment-deletion workflow is absent on the validated branch; trigger the comment-deletion event and verify its attribution when that capability is available. | TEST-001 v2.1 designates this as non-blocking integration validation. Archive/restore audit leg passed; the absent event category is not claimed complete. |

## Uncovered Acceptance Criteria

None for STORY-012 blocking scope. The deferred TC-015-01 event category is
recorded above and does not redefine the approved expected behavior.

## Recommendation

**READY FOR REVIEW** for the exact production commit
`fedeb6b9eae10cc864f87225abc774f23d040821`. TR-021 remains historical
evidence for its earlier SHA only. Human review is still required; any
subsequent production change requires a new independent retest.
