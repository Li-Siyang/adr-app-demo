# STORY-012 validation status

**Latest independent run:** [TR-025](details/TR-025-story-012-superseded-refresh-retest.md)
— **PASSED**; READY FOR REVIEW for the validated production commit.
**Validated production commit:** `f35ea906cedf49abd28fe07cececc615b146f3e9`.
**Validated production tree:** `43b5f240439fd9c7ae16db8ab35aabd6c0e0e568`.
**Current-code applicability:** TR-025 independently retested the superseded
refresh fix. Evidence-only commits after this SHA do not change production;
any subsequent production change requires another independent retest.

All five blocking STORY-012 Test Cases passed. The assigned administrator-only,
archived exact-tag, deletion-denial, and archival audit/retention regressions
also passed. TC-015-01's comment-deletion event leg remains explicitly
non-blocking and deferred because STORY-011 is absent from the inherited
production branch; no predecessor Story is represented as fully passed.
TR-022 also independently retested both PR review findings in headless Chrome
against the actual UI script and ran the complete backend regression suite.
TR-023 independently retested the editing/archival review fix, including
preservation of unsaved edits and normal archiving after save or cancel.
TR-024 independently retested the visible edit warning and in-flight
record-action lock in Chrome, including failure recovery and refresh timing.
TR-025 independently retested the superseded-refresh race and cross-platform
browser discovery change.

## Run history

| Run | Validated production commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-021](details/TR-021-story-012-archive-restore.md) | `225f3989e7761dad1e3ad9a535785e438dc173d0` | PASSED | TC-012-01–05 passed; focused suite 33 passed; full backend regression 261 passed with one historical approved skip. |
| [TR-022](details/TR-022-story-012-review-fix-retest.md) | `fedeb6b9eae10cc864f87225abc774f23d040821` | PASSED | Two review findings independently retested in Chrome; blocking and deferred regression 49 passed, 1 historical skip; full backend 261 passed, 1 historical skip. |
| [TR-023](details/TR-023-story-012-edit-archive-retest.md) | `c72d66e7ce88f7ec403c7032ffdcf71904013e97` | PASSED | Edit/archive guard independently retested in Chrome; blocking/deferred regression 49 passed, 1 historical skip; full backend 261 passed, 1 historical skip. |
| [TR-024](details/TR-024-story-012-archive-ui-retest.md) | `10021f11c9dd82a6da3fbc028344ba20cef695fa` | PASSED | Both latest UI review findings independently retested in Chrome; focused regression 50 passed, 1 historical skip; full backend 263 passed, 1 historical skip. |
| [TR-025](details/TR-025-story-012-superseded-refresh-retest.md) | `f35ea906cedf49abd28fe07cececc615b146f3e9` | PASSED | Superseded refresh and browser discovery follow-up retested; focused regression 50 passed, 1 historical skip; full backend 263 passed, 1 historical skip. |
