# STORY-004 validation status

**Latest independent run:** [TR-013](details/TR-013-story-004-owner-browser-retest.md)
— PASSED; READY FOR REVIEW.
**Validated production commit:** `660d896898b359492e74d73140accfb208233f82`.
**PR:** [#10](https://github.com/Li-Siyang/adr-app-demo/pull/10).

TR-013 passed all five approved STORY-004 cases and the delayed Owner-display
browser regression. The subsequent PR changes add validation documentation
only; no later production change was present when this page was published.
This is a snapshot, not an automatic status check: compare the PR's production
changes with the validated commit before relying on READY FOR REVIEW. If
production code changes, review readiness is **pending independent retest**
until a new run passes. Human review and PR approval are separate.

## Run history

| Run | Validated commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-010](details/TR-010-story-004-review-fix-retest.md) | `74d79c06f1580edf1cabcb5adf4a57ab94827022` | BLOCKED | Python and Node.js unavailable; tests could not run. |
| [TR-011](details/TR-011-story-004-review-fix-retest.md) | `37737fe520551d332f9625bd54e99bb3da6300ac` | BLOCKED | Executable tests passed; browser interaction remained unverified. |
| [TR-012](details/TR-012-story-004-browser-validation.md) | `68d316139717a6cf00a29f3fb698bf9d65a10427` | FAILED | Delayed identity loading displayed the wrong Owner in edit mode. |
| [TR-013](details/TR-013-story-004-owner-browser-retest.md) | `660d896898b359492e74d73140accfb208233f82` | PASSED | Browser retest and relevant regression checks passed. |

For each subsequent validation run, preserve its separate TR report and update
this page's latest result, validated commit, review readiness, and history.
When production code changes before a retest, mark review readiness pending
instead of presenting the earlier PASS as current.
