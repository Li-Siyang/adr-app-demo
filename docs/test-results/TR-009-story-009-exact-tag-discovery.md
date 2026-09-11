# Test Result: STORY-009 Exact Tag Discovery

**Test Run ID:** TR-009  
**Mode:** VALIDATION MODE  
**Execution date:** 2026-09-11  
**Implementation commit:** `270e8c09e547032cdafef997170c3f644bd62884`  
**Source Requirement:** `docs/requirements/requirement-definition.md`, Version 1.3, Approved  
**Source Development Plan:** `docs/planning/PLAN-001-internal-decision-record-mvp.md`, Version 1.1  
**Source Test Design:** `docs/test-design/TEST-001-internal-decision-record-mvp.md`, Version 2.0, Approved

## Overall Status

**BLOCKED**

Exact-tag matching, exclusion of partial tag text, tagged Draft persistence, and
discovery across Draft, Proposed, Accepted, Rejected, and Superseded lifecycle
states passed. The archived-record portion of TC-009-01 cannot be executed
because the current record model has no archival condition and the application
has no archive operation. The Development Plan assigns archival implementation
to dependent STORY-012, which is planned after and depends on STORY-009.

## Summary

| Measure | Count |
|---|---:|
| Approved STORY-009 Test Cases | 2 |
| Passed | 1 |
| Failed | 0 |
| Blocked | 1 |
| Manual | 0 |
| Not automated | 0 |
| Additional automated acceptance checks | 2 passed |

TC-009-01 is blocked as a whole because its approved expected result includes
archived records. Its executable current and historical lifecycle-state
coverage passed.

## Execution

| Scope | Command | Result |
|---|---|---|
| STORY-009 and related STORY-003 acceptance | `python -m pytest -q tests\acceptance\test_story_009_exact_tag_discovery.py tests\acceptance\test_story_003_complete_draft.py` | 35 passed, 1 blocked skip |
| Full regression | `python -m pytest -q` | 82 passed, 1 blocked skip |
| Frontend JavaScript syntax | `node --check backend\app\static\app.js` | Passed |

Four dependency deprecation warnings were reported by FastAPI, Starlette,
AnyIO, and HTTPX integrations. They did not affect test outcomes.

## Approved Test Case Results

| Test Case | Execution Status | Result | Evidence |
|---|---|---|---|
| TC-009-01 | Automated / Blocked | Draft, Proposed, Accepted, Rejected, and Superseded exact-tag matches passed. Archived coverage is blocked. | `test_tc_009_01_returns_matching_current_and_historical_records`; record model has no `archived` field and API has no archive or restore operation. |
| TC-009-02 | Automated | Passed | `test_tc_009_02_returns_only_records_with_the_complete_selected_tag` |

## Related Story Validation

| Story | Coverage | Result |
|---|---|---|
| STORY-003 | Complete Draft creation, one-or-more tag retention, and discovery by each associated tag | Passed |
| STORY-005 | Discovery of Rejected records | Passed using controlled lifecycle-state test setup; lifecycle transition operations are not present on this branch. |
| STORY-007 / STORY-008 | Discovery of Superseded records | Passed using controlled lifecycle-state test setup; replacement and history operations are not present on this branch. |
| STORY-012 | Discovery of archived records | Blocked because the required archival model and operation are not implemented. |

## Requirement Coverage

| Requirement | Acceptance Criterion | Story | Test Case | Result |
|---|---|---|---|---|
| CR-FR-005 | AC-015 | STORY-009 / STORY-003 | TC-009-01, TC-009-02 | Covered for retained tags |
| CR-FR-015 | AC-015 | STORY-009 | TC-009-01, TC-009-02 | Covered |
| CR-FR-016 | AC-015 | STORY-009 | TC-009-01 | Partially covered: Rejected and Superseded passed; archived blocked |
| CR-BR-009 | AC-015 | STORY-009 | TC-009-01 | Covered for Rejected and Superseded |

## Failure Report

**Test Run ID:** TR-009  
**Story:** STORY-009  
**Test Case:** TC-009-01  
**Related Requirement:** CR-FR-016  
**Related Acceptance Criterion:** AC-015  
**Expected Behavior:** Applying one exact tag filter returns every matching
record, including archived records.  
**Actual Behavior:** Current and historical lifecycle-state matches are
returned, but an archived-record precondition cannot be established. The
`DecisionRecord` model has no archival condition and no archive or restore API
exists.  
**Classification:** PLANNING_GAP  
**Severity:** High  
**Evidence:** `DecisionRecord.model_fields` excludes an archival field; no
archive or restore route exists in `backend/app/api.py`. The approved plan
assigns archival behavior to STORY-012 while STORY-012 depends on STORY-009.  
**Recommended Next Owner:** Planning Agent and Human Reviewer

## Regression Result

All 82 executable automated tests passed and the archived-record case was
explicitly skipped as blocked. Existing STORY-001, STORY-002, and STORY-003
behavior remained green. No implementation failure was observed in the
executable STORY-009 scope.

## Uncovered Acceptance Criteria

- AC-015 remains unverified for archived records.

## Recommendation

**BLOCKED**

Do not mark STORY-009 fully validated until archived records can be created and
the archived branch of TC-009-01 is independently executed. The Planning Agent
or Human Reviewer should either make the required archival test fixture or
STORY-012 capability available before STORY-009 validation, or explicitly
approve deferred AC-015 archival validation with STORY-012.
