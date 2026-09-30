# Test Result Report

**Test Run ID:** TR-017
**Coverage Story or Stories:** STORY-007
**Execution-owning Story:** STORY-007
**Validated commit:** `ec708a301aee4ace443b8ba86a5bd6711c1fccea`
**Branch:** `li-siyang-supreme-memory`
**Report path:** `docs/test-results/story-007/details/TR-017-story-007-replacement-governance.md`

## Overall Status

**PASSED**

## Summary

- Approved blocking STORY-007 Test Cases: 8
- Passed: 8
- Failed: 0
- Blocked: 0
- Manual-only: 0
- Not yet automated: 0
- Independent acceptance suite: 12 passed (the eight STORY-007 cases, three
  deferred cross-Story integration cases, and one replacement-decision
  concurrency regression)
- Full backend regression: 225 passed, 1 skipped
- Developer-owned unit tests were independently rerun as part of the full
  backend suite and passed.

The validated production commit exactly matches the developer handoff SHA.
The worktree was clean before Validation-Agent-owned acceptance tests and
reports were added. No production source was changed during validation.

## Requirement Coverage

| Requirement | Acceptance Criterion | Coverage Story or Stories | Execution-owning Story | Execution designation | Test Case | Result |
| --- | --- | --- | --- | --- | --- | --- |
| CR-FR-011; CR-BR-004–005 | AC-009 | STORY-007 | STORY-007 | Blocking completion | TC-007-01 | **PASSED** — direct edits to Accepted records were denied for every configured Mock identity; retained content and state were unchanged. |
| CR-FR-012; CR-BR-005, CR-BR-013–014 | AC-010 | STORY-007 | STORY-007 | Blocking completion | TC-007-02 | **PASSED** — administrator created a linked Draft replacement; original remained Accepted and unchanged apart from its retained replacement link. |
| CR-FR-012; CR-BR-013–014 | AC-003, AC-025 | STORY-007 | STORY-007 | Blocking completion | TC-007-03 | **PASSED** — non-administrator creation was denied; a second active replacement was denied without changing retained records. |
| CR-FR-013; CR-BR-006 | AC-011, AC-039 | STORY-007 | STORY-007 | Blocking completion | TC-007-04 | **PASSED** — replacement acceptance changed it to Accepted and the original to Superseded; one attributed audit event recorded both changes and both links remained. |
| CR-FR-012; CR-BR-014 | AC-039 | STORY-007 | STORY-007 | Blocking completion | TC-007-05 | **PASSED** — rejection ended the active interval; the original stayed Accepted and a new linked replacement could be created. |
| CR-FR-030; CR-BR-019 | AC-046 | STORY-007 | STORY-007 | Blocking completion | TC-007-06 | **PASSED** — abandonment kept the linked replacement as Draft, retained the original as Accepted, recorded administrator/time evidence, allowed another replacement, and exposed bidirectional UI links. Headless Chrome 153 rendered and followed the links to both records. |
| CR-FR-030; CR-BR-019 | AC-003, AC-047 | STORY-007 | STORY-007 | Blocking completion | TC-007-07 | **PASSED** — a non-administrator could not abandon; an administrator could not abandon an ordinary Draft, Proposed replacement, Accepted, Rejected, or Superseded record. |
| CR-FR-030; CR-NFR-003; CR-BR-019 | AC-047 | STORY-007 | STORY-007 | Blocking completion | TC-007-08 | **PASSED** — content, lifecycle, ownership, approver/version fields, reactivation, submission, repeated abandonment, decision, and deletion attempts were denied; retained record remained unchanged. |

## Failed Tests

None.

## Regression Result

- Independent STORY-007 acceptance and integration suite:
  `python -m pytest tests/acceptance/test_story_007_replacement_versions.py -q`
  — **12 passed**.
- Full backend regression:
  `python -m pytest tests -q` — **225 passed, 1 skipped**.
- The one skip is the previously approved STORY-009 archived exact-tag
  discovery case, deferred until STORY-012 provides archival support; it is
  unrelated to STORY-007.
- Replacement Accept/Reject race regression returned exactly one success and
  one conflict. The final original status was Superseded only when replacement
  acceptance won; otherwise the original remained Accepted.
- A headless Chrome 153 session exercised the rendered decision-record page
  with an Accepted original, Abandoned replacement, and subsequent replacement.
  Both version directions rendered as anchors; following the abandoned-version
  link navigated to the corresponding record card.
- The test run emitted 17 existing dependency deprecation warnings; no
  warning caused a test failure.

## Deferred Non-blocking Integration Validation

| Test Case | Coverage Story or Stories | Execution-owning Story | Required capability / deferred scope | Result for this run |
| --- | --- | --- | --- | --- |
| TC-004-05 | STORY-004; STORY-007 | STORY-007 | Abandoned replacement Draft edit and submission denial | **PASSED** in the independent suite. |
| TC-005-03 | STORY-005; STORY-008 | STORY-007 | Superseded-record immutability after replacement acceptance | **PASSED** in the independent suite. |
| TC-006-02 | STORY-006; STORY-007 | STORY-007 | Ownership-transfer denial for an Abandoned replacement Draft | **PASSED** in the independent suite. |
| TC-015-02 | STORY-015; STORY-007; STORY-011 | STORY-007 | Abandonment audit attribution/time and comment-deletion audit attribution | Abandonment actor/time **PASSED** under TC-007-06. The comment-deletion leg remains deferred until STORY-011 provides comment deletion; it is non-blocking integration coverage, not a STORY-007 completion dependency. |
| TC-002-02 | STORY-002; STORY-007; STORY-012 | STORY-012 | Full administrator-only archive, restore, replacement-creation, and abandonment matrix | Replacement action denials are covered by TC-007-03/07. Full matrix remains deferred to STORY-012, which owns archive/restore integration validation; it does not block STORY-007. |
| TC-015-01, TC-015-03 | STORY-015 and governed-action Stories; STORY-012 | STORY-012 | Full audit-event matrix, archival events, and archived-record retention | Abandonment audit evidence is covered by TC-007-06. Remaining cross-workflow event and archival-retention checks are deferred to STORY-012 and do not block STORY-007. |

## Uncovered Acceptance Criteria

None for the STORY-007 blocking completion cases. Cross-Story deferred scope
is explicitly identified above and does not change the STORY-007 result.

## Recommendation

**READY FOR REVIEW** for production commit
`ec708a301aee4ace443b8ba86a5bd6711c1fccea`. This independent PASS applies to
that exact production SHA; no production code was changed during validation.
Human review remains required.
