# STORY-013 Independent Validation: Record Retention

**Test Run ID:** TR-027
**Coverage Story or Stories:** STORY-013
**Execution-owning Story:** STORY-012
**Validated commit:** `2423591b223b8676af4ef27edb16608504d17d24`
**Report path:** `docs/test-results/story-013/details/TR-027-story-013-record-retention.md`

## Overall Status

**PASSED**

## Summary

Validated the approved Requirement Definition v1.3, PLAN-001 v1.2 APPROVED,
and TEST-001 v2.1 APPROVED on the exact pushed commit. Developer-owned tests
passed on the implementation commit before independent validation. Added
Validation-Agent-owned API acceptance coverage and executed it along with the
replacement and archive/restore integration regressions.

| Scope | Approved cases | Passed | Failed | Blocked | Manual | Not yet automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-013 AC-045 | 2 | 2 | 0 | 0 | 0 | 0 |

The extra manual inspection confirmed the decision-record UI exposes archive
and restore controls but no record-delete action. Comment-content deletion
remains outside this Story's scope and was not changed.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-029; CR-OOS-007 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-01 | **PASSED** — API permanent deletion returned 405 and soft-delete update attempts returned 422; record state, detail retrieval, and listing remained unchanged across all Mock identities and Draft, Proposed, Accepted, Rejected, Superseded, active replacement Draft/Proposed, Abandoned, archived, and archived-Abandoned conditions. |
| CR-SCP-001; CR-FR-029 | AC-045 | STORY-013 | STORY-012 | Non-blocking integration-validation | TC-013-02 | **PASSED** — archive/restore continued to work under approved rules, preserved lifecycle state, and retained records; replacement and Abandoned archive/restore regressions passed. |

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- Independent acceptance plus related integration selection:
  `python -m pytest -q tests/acceptance/test_story_013_record_retention.py tests/acceptance/test_story_007_replacement_versions.py tests/acceptance/test_story_012_archive_restore.py tests/test_archival.py`
  — **45 passed**.
- Complete backend suite from `backend`:
  `python -m pytest -q -rs` — **288 passed, 1 skipped**, 17 existing dependency
  deprecation warnings. The skip is the pre-existing, Human-deferred archived
  exact-tag test in STORY-009; it does not cover STORY-013.
- Inspection of `backend/app/static/app.js` and `app.html` found no
  decision-record delete action. Existing session-cookie deletion is unrelated.
- Worktree was clean at the exact tested commit before report creation.

## Deferred Non-blocking Integration Validation

None outstanding for STORY-013. TEST-001 v2.1 assigns TC-013-01/02 to
STORY-012 as non-blocking integration validation. The STORY-007 replacement
and STORY-012 archival capabilities and fixtures were available, and their
deletion-denial, archive, restore, and Abandoned regressions were executed in
this run. The approved dependency typing remains unchanged: STORY-003 is a
Start dependency; STORY-007 and STORY-012 are integration-validation
dependencies, not completion gates.

## Uncovered Acceptance Criteria

None for STORY-013 AC-045. No independent live-server/browser interaction was
needed to test the supported HTTP mutation boundary; UI affordance presence was
checked against the shipped UI source.

## Recommendation

**READY FOR REVIEW** for validated commit
`2423591b223b8676af4ef27edb16608504d17d24`. No production changes were made
during independent validation. The validation test commit adds only
Validation-Agent-owned test coverage.
