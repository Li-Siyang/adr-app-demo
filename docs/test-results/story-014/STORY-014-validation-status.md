# STORY-014 validation status

**Latest independent run:** [TR-033](details/TR-033-story-014-create-edit-browser-validation.md)
— **PASSED**; recommendation: **READY FOR REVIEW**.
**Tested commit:** `5fe70443d40606e300053d7c665814b224586446`.
**Current-code applicability:** The latest run validates the actual served UI
through Mock identity selection, record creation, and record editing. No
production source behavior changed.

TC-014-01 passed for identity entry, record creation, and record editing,
including the initialized create and edit states in headless Chrome. The
full backend regression suite passed (272 passed, 1 skipped). HTTPS,
deployment, AC-032, and TC-016-03 are not STORY-014 acceptance conditions
under the approved v1.4 baseline; AC-032 and TC-016-03 belong to STORY-016.
The inherited legacy Jira mapping discrepancy is a tracking issue and does
not alter the approved requirement, plan, test design, or this product result.
Jira was not modified.

## Run history

| Run | Validated production commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-027](details/TR-027-story-014-data-and-https-boundaries.md) | `b05c4bfd1e1c4f2e7cf8cbd4e8324319ea4af361` | BLOCKED against superseded Requirement v1.3 | TC-014-01 passed; its deployed-HTTPS check was blocked under the then-approved v1.3 baseline. Historical evidence is unchanged and does not establish a result against v1.4. |
| [TR-028](details/TR-028-story-014-demo-data-notice.md) | `796074f9788662a0488f7e6b62fed6bae1289033` | PASSED | TC-014-01 passed on identity entry and the shared create/edit surface; full backend suite passed. |
| [TR-029](details/TR-029-story-014-independent-rerun.md) | `796074f9788662a0488f7e6b62fed6bae1289033` | PASSED | Independent rerun: TC-014-01 passed (2 route checks); full backend suite passed (271 passed, 1 skipped). |
| [TR-030](details/TR-030-story-014-rendered-notice-visibility.md) | `801448e50df85e78abd64a885329a783cf89c86c` | PASSED | TC-014-01 passed with computed-style/rendered-bounds checks in headless Chrome on both surfaces; full backend suite passed (271 passed, 1 skipped). |
| [TR-031](details/TR-031-story-014-pushed-head-revalidation.md) | `c604368075dbf860424b37efc02a6a36b91da209` | PASSED | Exact pushed PR HEAD revalidated: both browser visibility assertions passed; full backend suite passed (271 passed, 1 skipped). |
| [TR-032](details/TR-032-story-014-initialized-browser-surfaces.md) | `e9df3afaa12912978812d352de28da89ef452749` | PASSED | Actual app browser E2E passed after identity selection and page initialization; full backend suite passed (272 passed, 1 skipped). |
| [TR-033](details/TR-033-story-014-create-edit-browser-validation.md) | `5fe70443d40606e300053d7c665814b224586446` | PASSED | TC-014-01 passed through actual browser identity selection, record creation, and edit-mode visibility checks; full backend suite passed (272 passed, 1 skipped). |
