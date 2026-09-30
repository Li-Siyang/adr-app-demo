# STORY-012 Edit/Archive Review Fix Independent Retest

**Test Run ID:** TR-023
**Coverage Story or Stories:** STORY-002, STORY-009, STORY-012, STORY-013,
STORY-015
**Execution-owning Story:** STORY-012
**Validated commit:** `c72d66e7ce88f7ec403c7032ffdcf71904013e97`
**Validated production tree:** `511705b7e30ff5941b0d3da5c267161e34fa3997`
**Report path:** `docs/test-results/story-012/details/TR-023-story-012-edit-archive-retest.md`

## Overall Status

**PASSED**

## Summary

Validated the clean PR production HEAD after the editing/archival review fix,
without modifying production code. The approved Requirement Definition v1.3,
PLAN-001 v1.2, and TEST-001 v2.1 are unchanged. Developer-owned archival and
audit tests passed again. The prior TR-021 and TR-022 results apply only to
their respective earlier production SHAs.

| Scope | Test Cases | Passed | Failed | Blocked | Manual | Not Yet Automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-012 blocking completion | 5 | 5 | 0 | 0 | 0 | 0 |
| Owned deferred integration | 6 | 5 plus one partial | 0 | 0 | 0 | 0 |
| Editing/archival review finding | 1 | 1 | 0 | 0 | 0 | 0 |

The partial deferred TC-015-01 covers its archive/restore audit legs; the
STORY-011 comment-deletion event category remains unavailable on this branch
and is not claimed passed.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-020; CR-BR-007 | AC-020 | STORY-012 | STORY-012 | Blocking completion | TC-012-01 | **PASSED** — archived Draft, Proposed, Accepted, Rejected and Superseded records stayed retained and discoverable; the browser withheld an archive request for the record being edited, preserving the unarchived state until save or cancel. |
| CR-FR-020–021; CR-BR-007 | AC-003 | STORY-012 | STORY-012 | Blocking completion | TC-012-02 | **PASSED** — non-administrator archive/restore denied without state changes. |
| CR-FR-021 | AC-021 | STORY-012 | STORY-012 | Blocking completion | TC-012-03 | **PASSED** — each status restored to the state held immediately before archival. |
| CR-FR-020; CR-BR-014 | AC-026 | STORY-012 | STORY-012 | Blocking completion | TC-012-04 | **PASSED** — active Proposed replacement blocked Accepted original archival; resolving review to Accepted or Rejected removed that block. |
| CR-FR-021, CR-FR-030; CR-BR-019 | AC-047 | STORY-012 | STORY-012 | Blocking completion | TC-012-05 | **PASSED** — restored Abandoned replacement remained Draft, Abandoned, linked and immutable. |
| CR-USR-006, CR-USR-009; CR-BR-013 | AC-003 | STORY-002, STORY-007, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-002-02 | **PASSED** — archive, restore, replacement creation and abandonment denied for non-administrators. |
| CR-FR-015–016; CR-BR-009 | AC-015 | STORY-009 | STORY-012 | Non-blocking integration-validation | TC-009-01 | **PASSED** — the archived exact-tag discovery leg executed; its unchanged historical placeholder was skipped. |
| CR-FR-029; CR-OOS-007 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-01 | **PASSED** — archived and Abandoned records could not be deleted and remained retrievable. |
| CR-SCP-001; CR-FR-029 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-02 | **PASSED** — permitted archive/restore retained records. |
| CR-NFR-007 | AC-033 | STORY-015 and governed-action Stories | STORY-012 | Non-blocking integration-validation | TC-015-01 | **PARTIAL, NON-BLOCKING** — archive/restore audit attribution and concurrency passed; absent STORY-011 comment-deletion event leg remains deferred. |
| CR-FR-014; CR-NFR-003, CR-NFR-008 | AC-013, AC-034 | STORY-015, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-015-03 | **PASSED for assigned archival scope** — no expiry/deletion path on archived records or audit entries; repeated retrieval unchanged. |

Deferred integration results do not mark earlier coverage Stories fully PASSED.

## Review Finding Retest

| Scenario | Expected | Independent observed behavior |
| --- | --- | --- |
| Archive the Draft currently being edited, with unsaved changes | Prompt to save or cancel first; send no archive request and preserve the form contents and available save action. | **PASSED** — actual `app.html` and `app.js` rendered in headless Chrome; after editing the title and clicking Archive, requests remained empty, record remained unarchived, title stayed `Unsaved title`, Save changes remained visible and the instruction was shown. Cancel edit then allowed exactly one archive request. |
| Archive the Proposed record currently being edited | Same guard; after saving, archiving is permitted. | **PASSED** — the guard preserved unsaved title and prevented the initial request; Save changes sent the PUT, then Archive sent one POST and retained the saved title. |
| Edit one record and archive a different record | The guard must not block unrelated archiving or discard current edits. | **PASSED** — only the unrelated record received the archive POST and changed condition; the target edit form still offered Save changes. |

The browser test used isolated deterministic mocked API responses to exercise
the actual application UI script. It is not a live-server end-to-end or
screen-reader test. Earlier accessible-name and replacement-submission review
fixes remained covered by unchanged UI code and the previous TR-022 browser
retest; no production change touched those controls in this run.

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- From `backend`, `python -m pytest -q tests\acceptance\test_story_012_archive_restore.py tests\test_archival.py tests\test_audit.py tests\acceptance\test_story_007_replacement_versions.py tests\acceptance\test_story_009_exact_tag_discovery.py` — **49 passed, 1 skipped**.
- From `backend`, `python -m pytest -q` — **261 passed, 1 skipped**.
- Independent headless Chrome checks — **three scenarios passed** as detailed
  above.
- The one historical skip is the unchanged STORY-009 archived-tag placeholder;
  this run separately executed the archived-record discovery leg.
- Full suite emitted 17 existing dependency deprecation warnings without test
  failures. `git diff --check` passed.

## Deferred Non-blocking Integration Validation

| Test Case | Coverage Story or Stories | Execution-owning Story | Deferred scope | Reason non-blocking |
| --- | --- | --- | --- | --- |
| TC-015-01 | STORY-015 and governed-action Stories | STORY-012 | STORY-011 comment deletion is absent; trigger and verify that event category when available. | TEST-001 v2.1 designates this as integration-validation; the archive/restore audit scope passed. |

## Uncovered Acceptance Criteria

None for STORY-012 blocking completion. Deferred TC-015-01 is recorded above.

## Recommendation

**READY FOR REVIEW** for the exact production commit
`c72d66e7ce88f7ec403c7032ffdcf71904013e97`. Human review remains
required; any subsequent production change requires independent retest.
