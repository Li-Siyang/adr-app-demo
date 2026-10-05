# Test Result Report

**Test Run ID:** TR-036
**Coverage Story or Stories:** STORY-016; integrated STORY-001 through STORY-015
**Execution-owning Story:** STORY-016
**Validated commit:** `8e0229dfa41de26fe99762fd86562ef3ce63b98d`
**Report path:** `docs/test-results/story-016/details/TR-036-story-016-integrated-local-capacity.md`
**Execution date:** 2026-10-05
**Validation branch:** `li-siyang-musical-telegram`
**Production source branch:** `li-siyang-refactored-chainsaw`

## Overall Status

BLOCKED

Capacity and local-operation cases have confirmed implementation failures.
Mandatory compatibility execution is blocked by the TASK-022 prerequisite
and unavailable required browser executables. This is not an independent
PASS, not a completed STORY-016, and not Ready for Review.

## Summary

Approved STORY-016 cases: **3 total, 0 passed, 2 failed, 1 blocked**.
Two cases have automated live execution; one is blocked before formal
execution. Manual case count: 0. No case is Not Applicable, waived,
or non-blocking deferred coverage.

| Case | Classification of execution | Result | Evidence |
| --- | --- | --- | --- |
| TC-016-01 / AC-031 | Automated live integration/API and local UI | FAILED | Actual capacity verified; Draft-to-Proposed audit missing |
| TC-016-03 / AC-032 | Automated real local browser E2E plus API-only administration | FAILED | All listed local actions exercised; submission absent from displayed history |
| TC-016-02 / AC-036 | Blocked before formal TASK-024 execution | BLOCKED | TASK-022 is not PASS; four required combinations are not available |

Readiness was established from the explicit Developer
`READY_FOR_INDEPENDENT_VALIDATION` handoff, approved Requirement v1.4,
PLAN-001 v1.4, and TEST-001 v2.2. Initial clean HEAD exactly matched the
supplied production SHA. The developer's 410-pass/one-skip statement was
independently reproduced, not accepted as acceptance evidence.

The final independent full suite executed **416 tests: 413 passed,
3 failed, 0 skipped, 0 errors**. The three assertion failures are in the new
requirement-driven tests and represent the same confirmed production defect.
All **243 existing developer-owned top-level tests passed**. All 411
preexisting tests passed after executing the formerly deferred archived-tag
test. The new live suite has 5 executable tests: 2 passed and 3 failed.

After the full regression, the harness was tightened to count unique record
IDs explicitly and exclude audit IDs predating this live run. The attempted
full rerun was interrupted and is not counted as execution evidence.
The final targeted rerun of the persisted live suite completed:
**2 passed, 3 failed, pytest exit 1**, in 250.57 seconds. It independently
reproduced the same missing transition using only newly generated audit
events. Its real local URL was `http://127.0.0.1:54486`; the submitted
record `6e9f268e-f385-4c4f-911f-7890076ea886` was Proposed with no audit
entries. The full-suite figures above refer to the prior completed full
run, not this targeted rerun.

### Actual capacity and local setup

The application was started from `backend` after following README setup:
`python -m venv .venv`, activation, and
`python -m pip install -e ".[dev]"`.
The executable server command was the documented
`uvicorn app.main:app --reload`, invoked through the same venv Python module,
with a dynamically allocated loopback port instead of occupied/shared-port
assumptions. Actual final-run URL: `http://127.0.0.1:54695`.

Windows harness isolation uses a separate server console and
`WATCHFILES_FORCE_POLLING=true`. Native watcher notifications initially
reported changes inside `.venv` and interrupted execution; these interrupted
attempts were not counted as passes. Polling removed that environment
interference without modifying production or omitting `--reload`.
The server's HTTP readiness and real browser DevTools readiness were verified.
Harness deadlines are liveness safeguards, not a response-time SLA.
No deployment, HTTPS, remote endpoint, or multi-worker configuration was used.
Only synthetic data was generated. Owned server/browser processes were
stopped after execution; host browser installations were unchanged.

All seed records were created and transitioned through the live public API;
no production store mutation or smaller capacity proxy was used.

| Measured baseline | Actual |
| --- | --- |
| Distinct preconfigured Mock identities returned by the application | 25 |
| Distinct retained record IDs before acceptance exercise | 1,000 |
| Distinct Mock authors represented in the dataset | 25 |
| Draft / Proposed / Accepted / Rejected / Superseded | 225 / 175 / 400 / 175 / 25 |
| Archived records, across the retained dataset | 100 |
| Abandoned replacement Drafts | 25 |
| Linked replacement records | 50 |
| Retained records after additional creation workflows | 1,020 |

The baseline includes every lifecycle status, retained archived records,
accepted version links, and permanent abandonment. New creation and
replacement workflows increase the count above the baseline; fixtures are
never deleted to maintain an artificial count. No response-time assertion
was added.

## Requirement Coverage

All rows below are completion-blocking under STORY-016's integrated cases.
Successful subchecks do not imply that their parent case passed.

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-SCP-002; CR-NFR-004 | AC-031 | STORY-016 | STORY-016 | Blocking completion | TC-016-01 | FAILED |
| CR-OBJ-001; CR-SCP-004; CR-NFR-005; CR-OOS-015 | AC-032 | STORY-016 | STORY-016 | Blocking completion | TC-016-03 | FAILED |
| CR-NFR-011 | AC-036 | STORY-016 | STORY-016 | Blocking completion | TC-016-02 | BLOCKED |
| CR-FR-027-028; CR-NFR-013; CR-BR-018 | AC-043-044 | STORY-001 | STORY-016 | Blocking completion | TC-016-01/03, underlying TC-001-01/02 | Identity selection, roles, attribution and limitation checks passed |
| CR-FR-003-006A; CR-FR-024; CR-BR-003/016 | AC-002/004-005/008/024/029 | STORY-003/004/005/010 | STORY-016 | Blocking completion | TC-016-01/03 | Creation, required-content guards, tags, edit and review restart checks passed |
| CR-USR-004-006/009-010; CR-FR-009-010; CR-BR-001-002/013/015 | AC-003/006-007/023 | STORY-002/005/007/012 | STORY-016 | Blocking completion | TC-016-01/03 | Administrator denial, designated/self decision, and additive permissions checks passed |
| CR-FR-006A/026; CR-BR-011 | AC-014/030 | STORY-006 | STORY-016 | Blocking completion | TC-016-01/03 | Author/owner/admin transfer, author preservation and no extra departure editing checks passed |
| CR-FR-011-013/030; CR-BR-004-006/014/019 | AC-009-012/025/038-039/046-047 | STORY-007/008 | STORY-016 | Blocking completion | TC-016-01/03 | Replacement creation/guards/outcomes, supersession, abandonment and navigation checks passed |
| CR-FR-015-017/019/025; CR-BR-009/012 | AC-015-016/018-019/029 | STORY-009/010/011 | STORY-016 | Blocking completion | TC-016-01/03 | Exact discovery across all states, retained archived matches, tags and comment checks passed |
| CR-FR-020-021/029; CR-NFR-008; CR-BR-007/014 | AC-020-021/026/034/045/047 | STORY-012/013 | STORY-016 | Blocking completion | TC-016-01/03 | All-state archive/restore, replacement guard, retention/deletion denial checks passed |
| CR-FR-014; CR-NFR-003/007-008 | AC-013/033-034 | STORY-008/015 and governed actions | STORY-016 | Blocking completion | TC-016-01/03, underlying TC-008-03/TC-015-01 | FAILED: submission audit/history absent; other exercised categories retained |
| CR-SCP-003; CR-FR-023; CR-BR-010 | AC-037 | STORY-001/003/014 | STORY-016 | Blocking completion | TC-016-01/03, underlying TC-014-01 | Entry/create/edit notices visibly passed |

Executable capacity/local coverage:
`backend/tests/acceptance/test_story_016_integrated_local.py`.
Tests cover ordinary and self decisions, all 25 identity attributions,
required creation fields, individually cleared editable submission fields,
missing approvers, unauthorized role actions, terminal/abandoned immutability,
ownership actors and states, all replacement endpoints, all-state
archive/restore, exact discovery, author-only comment soft deletion,
concurrent conflicting decisions and duplicate comment deletion, audit
retrieval/immutability, and real UI workflow navigation.

## Failed Tests

- [TC-016-01 Failure Report](FR-036-story-016-tc-016-01.md):
  `IMPLEMENTATION_DEFECT`, High. Successful submission produces no
  Draft-to-Proposed audit entry.
- [TC-016-03 Failure Report](FR-036-story-016-tc-016-03.md):
  `IMPLEMENTATION_DEFECT`, High. The same missing audit event makes local
  displayed history incomplete.

Final reproducer response: submitted record
`419f1ddc-b12a-4cde-b2a6-0be9765dbfcd` is Proposed and its audit
collection is `{"events":[]}`. The lifecycle-set check independently reports
only `('Draft', 'Proposed')` missing. The browser history assertion also fails.
An earlier diagnostic sorting error involving `None` was a harness defect;
it was corrected and the final run contains explicit requirement assertion
failures, not that diagnostic error.

## Regression Result

Commands run from `backend`:

```powershell
python -m pytest -q -rs
# Initial exact-SHA baseline: 410 passed, 1 deferred skip.

.\.venv\Scripts\python.exe -m pytest tests\acceptance\test_story_016_integrated_local.py tests\acceptance\test_story_009_exact_tag_discovery.py -q -s -x
# Setup and local workflow development; no final PASS was issued.

.\.venv\Scripts\python.exe -m pytest -q -s --tb=short
# Final corrected harness: 413 passed, 3 failed, 0 skipped, pytest exit 1.

.\.venv\Scripts\python.exe -m pytest tests\acceptance\test_story_016_integrated_local.py -q -s --tb=short
# Final persisted current-run-only audit harness: 2 passed, 3 failed, exit 1.
```

Final execution took 230.27 seconds; this is execution evidence, not an
acceptance response-time target. Sixteen dependency deprecation warnings
were present. Production under `backend/app` compares unchanged against the
validated SHA. Only validation-owned tests and reports change on this branch.

The old TC-009-01 archived-tag skip is now applicable because archival is
available. Its empty skipped placeholder was replaced with an executable
archive-and-exact-discovery assertion, preserving expected behavior.
It passed, including in the final full regression. Earlier historical
deferral is not used to justify a continued omission.

## Deferred Non-blocking Integration Validation

None for STORY-016. All three STORY-016 cases block completion.
Legacy Jira Blocks/predecessor Done states were not treated as gates.
PLAN-001 typed dependencies control the execution order.

### Mandatory compatibility blockers and execution-time version evidence

**TEST_ENVIRONMENT**: no isolated executable or configured browser grid for
the missing required major versions was found. The installation inventory
was read only, and no host browser was downgraded, replaced, or updated.
Chromium was not substituted for Edge.

Google's execution-time Windows Stable metadata includes actively served
Chrome 155.0.8059.26 in a 0.005 rollout fraction, alongside the dominant
154.0.8037.93/95/97/98 releases. Conservatively, the highest currently
served Stable major is **155**, and its immediately prior major is **154**;
the small rollout is not silently exempted. The common installed 154
alone therefore cannot establish complete Chrome compatibility.
Microsoft's Stable Windows x64 metadata identifies **154.0.4258.53** as
the latest release, with immediately prior major **153**.

Read-only vendor sources queried on 2026-10-05:

- <https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/stable/versions/all/releases?filter=endtime=none&pageSize=10>
- <https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Windows&num=4>
- <https://edgeupdates.microsoft.com/api/products?view=enterprise>

| Required combination | Actual available evidence | Formal TC-016-02 result |
| --- | --- | --- |
| Chrome 155 current served Stable major | No available executable found | BLOCKED, not executed |
| Chrome 154 immediately prior | Local TC-016-03 actually ran Chrome/154.0.8037.93 | BLOCKED by TASK-022, not a compatibility PASS |
| Edge 154 current Stable major | Installed file ProductVersion 154.0.4258.48; version folders 154.0.4258.48 and 154.0.4258.53 | BLOCKED by TASK-022, inventory only; not executed |
| Edge 153 immediately prior | No available executable found | BLOCKED, not executed |

Inventory locations: installed Google Chrome and Microsoft Edge Application
directories; user-local Chrome/Edge Application directories; Playwright and
Selenium caches; this worktree; configured browser-related environment
variables; repository workflow definitions and available GitHub Actions
workflow listing. No alternate major executable or configured four-version
grid was discovered. Both installed Edge version folders are major 154,
not two major versions. No other user's files or browser profiles were used.

Formal TASK-024 execution has **not started**: PLAN-001 Section 8.1 requires
passing TASK-022 capacity evidence first. The Chrome execution above belongs
to local-operation validation, not a prematurely started compatibility case.

## Uncovered Acceptance Criteria

AC-036 has no complete four-combination evidence. AC-031 and AC-032 are
not satisfied because their integrated audit/history checks fail. AC-013
and AC-033 fail specifically for submission; other passing subchecks cannot
override that failure.

The actual UI/API exposes fixed preconfigured roles and approver
designation/removal, not a user-role mutation surface. End-to-end
`user_role_changed` event generation was not claimed as proven merely
because the developer event enum/store supports that category. This residual
TC-015-01 category must be explicitly evaluated in fix/retest coverage,
using an approved execution fixture or the appropriate role-change entry
point, rather than counted as silently covered.

## Recommendation

BLOCKED; NOT READY FOR REVIEW.

Return the confirmed missing submission audit/history defect to the Developer
Agent/coordinator. Independently retest the exact pushed fix SHA, including
ordinary/replacement submissions, all lifecycle audit pairs, displayed
history, failure atomicity, and regression. Only after TASK-022 passes may
formal TASK-024 run on all four actual browser/version combinations.
Provide safe isolated Chrome 155 and Edge 153 executables or equivalent
actual-browser infrastructure; do not install over host browsers or declare
omitted combinations PASS. Re-resolve relative browser versions at retest.

Jira AIBAIDD-25 / TASK-022 AIBAIDD-48 / TASK-024 AIBAIDD-41 were supplied
as coordinator-owned synchronized mappings. No Jira writes, merge, new
session, production change, or review-readiness declaration was performed.
