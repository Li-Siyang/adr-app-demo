# STORY-012 Archive UI Review Fix Independent Retest

**Test Run ID:** TR-024
**Coverage Story or Stories:** STORY-002, STORY-009, STORY-012, STORY-013, STORY-015
**Execution-owning Story:** STORY-012
**Validated commit:** `10021f11c9dd82a6da3fbc028344ba20cef695fa`
**Validated production app.js blob:** `f1ff89ab16d81953471b3528887ae6a4256e88af`
**Report path:** `docs/test-results/story-012/details/TR-024-story-012-archive-ui-retest.md`

## Overall Status

**PASSED**

## Summary

Independently retested the exact pushed production HEAD after review comments
4143927565 and 4143927634. The working tree had no uncommitted production
changes; the only newly added test was Validation-Agent-owned browser coverage.
Requirement Definition v1.3, PLAN-001 v1.2, and TEST-001 v2.1 are approved
and unchanged. Developer-owned archival, audit, and browser tests passed.
Earlier TR-021 through TR-023 remain historical evidence for their own SHAs.

| Scope | Approved cases | Passed | Failed | Blocked | Manual | Not yet automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-012 blocking completion | 5 | 5 | 0 | 0 | 0 | 0 |
| Owned deferred integration | 6 | 5 plus one partial | 0 | 0 | 0 | 0 |
| New review UI regressions | 2 findings | 2 | 0 | 0 | 0 | 0 |

TC-015-01 is partial only because the STORY-011 comment-deletion event
capability is absent from this branch; its archive and restore audit legs
passed. This is an approved non-blocking integration-validation dependency,
not a claim that STORY-011 or STORY-015 passed in full.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-020; CR-BR-007 | AC-020 | STORY-012 | STORY-012 | Blocking completion | TC-012-01 | **PASSED** — archived Draft, Proposed, Accepted, Rejected, and Superseded records remained discoverable; UI guarded unsaved edits and retained disabled mutation controls during archival. |
| CR-FR-020–021; CR-BR-007 | AC-003 | STORY-012 | STORY-012 | Blocking completion | TC-012-02 | **PASSED** — non-administrators could neither archive nor restore. |
| CR-FR-021 | AC-021 | STORY-012 | STORY-012 | Blocking completion | TC-012-03 | **PASSED** — restore returned each record to its exact pre-archive lifecycle. |
| CR-FR-020; CR-BR-014 | AC-026 | STORY-012 | STORY-012 | Blocking completion | TC-012-04 | **PASSED** — active Proposed replacement blocked original archival; either review result removed the active-Proposed guard. |
| CR-FR-021, CR-FR-030; CR-BR-019 | AC-047 | STORY-012 | STORY-012 | Blocking completion | TC-012-05 | **PASSED** — restored Abandoned replacement remained Draft, linked, abandoned, and immutable. |
| CR-USR-006, CR-USR-009; CR-BR-013 | AC-003 | STORY-002, STORY-007, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-002-02 | **PASSED** — non-administrator archive, restore, replacement creation, and abandonment denied without state change. |
| CR-FR-015–016; CR-BR-009 | AC-015 | STORY-009 | STORY-012 | Non-blocking integration-validation | TC-009-01 | **PASSED for archived leg** — archived records remained in exact-tag discovery; unchanged historical placeholder skipped. |
| CR-FR-029; CR-OOS-007 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-01 | **PASSED for archival conditions** — archived and Abandoned records resisted deletion and remained retrievable. |
| CR-SCP-001; CR-FR-029 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-02 | **PASSED** — permitted archive and restore did not delete a record. |
| CR-NFR-007 | AC-033 | STORY-015 and governed-action Stories | STORY-012 | Non-blocking integration-validation | TC-015-01 | **PARTIAL, NON-BLOCKING** — immutable attributed archive/restore audit events and concurrent transitions passed; STORY-011 comment-deletion leg deferred. |
| CR-FR-014; CR-NFR-003, CR-NFR-008 | AC-013, AC-034 | STORY-015, STORY-012 | STORY-012 | Non-blocking integration-validation | TC-015-03 | **PASSED for assigned archival scope** — no expiry or deletion route for archived records or audit entries; repeated retrieval stable. |

## Review Finding Retest

The independent `tests\acceptance\test_story_012_review_ui_retest.py` runs
the actual `app.html` and `app.js` in headless Chrome against controlled API
responses; it does not reuse the developer browser test.

| Finding | Expected | Observed |
| --- | --- | --- |
| 4143927565, invisible warning | No archive request while editing; show the instruction in the edit form's live message without discarding changes; clear on Cancel or replace on Save. | **PASSED** — warning appeared in `#record-form-message`, unsaved title survived, no POST was sent; Cancel cleared it and Save replaced it. |
| 4143927634, in-flight mutation race | Target record actions locked through a list refresh and pending response, while other records remain usable; failed requests restore controls, successful archive updates actions. | **PASSED** — target buttons/select disabled before response, still disabled after filter-driven refresh and during deliberately delayed post-success refresh; other record Edit stayed enabled; failed POST unlocked controls; successful archive removed Edit and enabled Restore, and successful Restore re-enabled Archive. |

This browser fixture models network ordering but is not a live-server E2E or
screen-reader test. API permissions, audit, and lifecycle were separately
exercised through the acceptance suite.

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- Developer-owned checks were confirmed from the development handoff: archival/audit
  subset 33 passed; full backend suite 262 passed, 1 historical skip.
- Independently, from `backend`:
  `python -m pytest -q tests\acceptance\test_story_012_review_ui_retest.py tests\acceptance\test_story_012_archive_restore.py tests\test_archival.py tests\test_audit.py tests\acceptance\test_story_007_replacement_versions.py tests\acceptance\test_story_009_exact_tag_discovery.py`
  — **50 passed, 1 skipped**.
- `python -m pytest -q` — **263 passed, 1 skipped**, including the new
  independent browser test and the developer browser test; 17 existing
  dependency-deprecation warnings.
- The single skip is the unchanged STORY-009 archived-tag placeholder. Its
  archived-record leg was separately executed in the STORY-012 acceptance test.
- `git diff --check` passed; local production `app.js` hash equaled the
  validated HEAD blob above. Remote PR head also matched the validated SHA.

## Deferred Non-blocking Integration Validation

| Test Case | Coverage Story or Stories | Execution-owning Story | Required capability and regression scope | Reason non-blocking |
| --- | --- | --- | --- | --- |
| TC-015-01 | STORY-015 and governed-action Stories | STORY-012 | When STORY-011 is available, trigger and verify its comment-deletion audit category. | TEST-001 v2.1 assigns this as integration-validation; archival event legs passed. |

## Uncovered Acceptance Criteria

None for STORY-012 blocking completion. TC-015-01's remaining category is
reported above, not silently counted as fully passed.

## Recommendation

**READY FOR REVIEW** for production commit
`10021f11c9dd82a6da3fbc028344ba20cef695fa`. Human review of governance
and audit behavior remains necessary. Any later production change requires
another independent retest.
