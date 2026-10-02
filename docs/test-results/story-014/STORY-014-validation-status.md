# STORY-014 validation status

**Latest independent run:** [TR-029](details/TR-029-story-014-independent-rerun.md)
— **PASSED**; recommendation: **READY FOR REVIEW**.
**Tested production commit:** `796074f9788662a0488f7e6b62fed6bae1289033`.
**Current-code applicability:** This run validates the current production
commit. Current HEAD is a later documentation-only validation-evidence commit;
no production files have changed since the tested commit.

The independent rerun of TC-014-01 passed for identity entry and the shared
record creation/editing surface. The full backend regression suite passed
(271 passed, 1 skipped). HTTPS, deployment, AC-032, and TC-016-03 are not
STORY-014 acceptance conditions under the approved v1.4 baseline; AC-032 and
TC-016-03 belong to STORY-016. The inherited legacy Jira mapping discrepancy
is a tracking issue and does not alter the approved requirement, plan, test
design, or this product result. Jira was not modified.

## Run history

| Run | Validated production commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-027](details/TR-027-story-014-data-and-https-boundaries.md) | `b05c4bfd1e1c4f2e7cf8cbd4e8324319ea4af361` | BLOCKED against superseded Requirement v1.3 | TC-014-01 passed; its deployed-HTTPS check was blocked under the then-approved v1.3 baseline. Historical evidence is unchanged and does not establish a result against v1.4. |
| [TR-028](details/TR-028-story-014-demo-data-notice.md) | `796074f9788662a0488f7e6b62fed6bae1289033` | PASSED | TC-014-01 passed on identity entry and the shared create/edit surface; full backend suite passed. |
| [TR-029](details/TR-029-story-014-independent-rerun.md) | `796074f9788662a0488f7e6b62fed6bae1289033` | PASSED | Independent rerun: TC-014-01 passed (2 route checks); full backend suite passed (271 passed, 1 skipped). |
