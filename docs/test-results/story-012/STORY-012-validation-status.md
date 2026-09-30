# STORY-012 validation status

**Latest independent run:** [TR-022](details/TR-022-story-012-review-fix-retest.md)
— **PASSED** for the production commit below.
**Validated production commit:** `fedeb6b9eae10cc864f87225abc774f23d040821`.
**Validated production tree:** `fc1cc73b26a6ac2800afce565e85dd18ac422dde`.
**Current-code applicability:** **PENDING INDEPENDENT RETEST**. A subsequent
PR review fix prevents archiving the record currently being edited; TR-022
applies only to the validated production commit above. This PR remains Draft
until independent validation passes the updated production code.

All five blocking STORY-012 Test Cases passed. The assigned administrator-only,
archived exact-tag, deletion-denial, and archival audit/retention regressions
also passed. TC-015-01's comment-deletion event leg remains explicitly
non-blocking and deferred because STORY-011 is absent from the inherited
production branch; no predecessor Story is represented as fully passed.
TR-022 also independently retested both PR review findings in headless Chrome
against the actual UI script and ran the complete backend regression suite.

## Run history

| Run | Validated production commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-021](details/TR-021-story-012-archive-restore.md) | `225f3989e7761dad1e3ad9a535785e438dc173d0` | PASSED | TC-012-01–05 passed; focused suite 33 passed; full backend regression 261 passed with one historical approved skip. |
| [TR-022](details/TR-022-story-012-review-fix-retest.md) | `fedeb6b9eae10cc864f87225abc774f23d040821` | PASSED | Two review findings independently retested in Chrome; blocking and deferred regression 49 passed, 1 historical skip; full backend 261 passed, 1 historical skip. |
