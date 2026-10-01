# STORY-014 Data and HTTPS Boundary Validation

**Test Run ID:** TR-027
**Coverage Story or Stories:** STORY-014
**Execution-owning Story:** STORY-014
**Validated commit:** `b05c4bfd1e1c4f2e7cf8cbd4e8324319ea4af361`
**Report path:** `docs/test-results/story-014/details/TR-027-story-014-data-and-https-boundaries.md`

## Overall Status

**BLOCKED**

## Summary

Validated the exact production commit reported by the Developer Agent. The
approved Requirement Definition v1.3, PLAN-001 v1.2, and TEST-001 v2.1 are
approved and in scope. The Developer handoff reports the implementation and
Developer-owned Unit Tests ready for independent validation. The current
environment has no representative deployed HTTPS ingress or deployment
endpoint, so deployed client-facing TLS cannot be observed. The locally
executable portion passed, but TC-014-02 is a blocking completion case and
cannot be marked passed without its deployed-environment precondition.

| Scope | Approved cases | Passed | Failed | Blocked | Manual | Not yet automated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| STORY-014 blocking completion | 2 | 1 | 0 | 1 | 0 | 0 |

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-SCP-003; CR-FR-023; CR-BR-010 | AC-037 | STORY-014 | STORY-014 | Blocking completion | TC-014-01 | **PASSED** — entry (`/`) and shared record create/edit (`/app`) responses each contain an unhidden notice explicitly limiting use to demo/synthetic data and naming all three prohibited real-data categories. |
| CR-NFR-005 | AC-032 | STORY-014 | STORY-014 | Blocking completion | TC-014-02 | **BLOCKED** — app-level production HTTP redirects, HTTPS page/API responses, and local HTTP page/API responses passed. No representative deployed TLS ingress/client endpoint was available to verify the public client connection and its subsequent traffic end to end. |

## Failed Tests

None. No Failure Reports apply.

## Regression Result

- Independent acceptance and developer HTTPS unit tests:
  `python -m pytest tests\acceptance\test_story_014_demo_data_and_https.py tests\test_https_enforcement.py -q`
  — **11 passed**.
- Complete backend suite from `backend`: `python -m pytest -q` —
  **280 passed, 1 skipped**. The skip is an existing STORY-009 archived-tag
  placeholder, unrelated to STORY-014. The suite emitted existing
  Starlette/httpx deprecation warnings.
- The focused acceptance tests were added as Validation-Agent-owned tests and
  are present in the current working tree; they do not alter production code.
  Production source at `b05c4bfd1e1c4f2e7cf8cbd4e8324319ea4af361` was
  unchanged during this run.
- No real deployed host, TLS ingress, or proxy configuration was available.
  TestClient HTTPS requests verify application behavior, not a deployed TLS
  handshake or the public edge's HTTP handling.

## Deferred Non-blocking Integration Validation

None. TC-014-02 is approved blocking completion coverage, not a deferred
integration dependency.

## Uncovered Acceptance Criteria

AC-032 is partially evaluated but not fully covered: deployed client-facing
TLS and subsequent public traffic remain unverified until a representative
deployment endpoint is available. Local development HTTP exemption and
application-level production redirect behavior were exercised.

## Recommendation

**BLOCKED** — do not mark STORY-014 ready for review. Re-run TC-014-02 against
a representative deployed TLS ingress, verify subsequent application traffic
at the public client boundary, and inspect local development separately. Jira
was not modified. The previously recorded Jira `Blocks` link/type conflicts
remain a Planning/Jira mapping issue and were not used to redefine approved
dependency semantics.
