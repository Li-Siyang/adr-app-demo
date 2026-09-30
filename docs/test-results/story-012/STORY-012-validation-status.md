# STORY-012 validation status

**Latest independent run:** [TR-021](details/TR-021-story-012-archive-restore.md)
— **PASSED** for the production commit below.
**Validated production commit:** `225f3989e7761dad1e3ad9a535785e438dc173d0`.
**Validated production tree:** `df121381634f27ea11d612be5382c03672645afb`.
**Current-code applicability:** **PENDING INDEPENDENT RETEST**. The PR review
fixes changed `backend/app/static/app.js` after TR-021; its PASSED result
applies only to the production commit above. This PR remains Draft until an
independent validation run passes the current production code.

All five blocking STORY-012 Test Cases passed. The assigned administrator-only,
archived exact-tag, deletion-denial, and archival audit/retention regressions
also passed. TC-015-01's comment-deletion event leg remains explicitly
non-blocking and deferred because STORY-011 is absent from the inherited
production branch; no predecessor Story is represented as fully passed.

## Run history

| Run | Validated production commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-021](details/TR-021-story-012-archive-restore.md) | `225f3989e7761dad1e3ad9a535785e438dc173d0` | PASSED | TC-012-01–05 passed; focused suite 33 passed; full backend regression 261 passed with one historical approved skip. |
