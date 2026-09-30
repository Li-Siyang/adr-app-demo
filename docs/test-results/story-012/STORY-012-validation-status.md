# STORY-012 validation status

**Latest independent run:** [TR-024](details/TR-024-story-012-archive-ui-retest.md)
— **PASSED for the historical production commit only**. PR #33 is Draft;
the subsequent superseded-refresh fix is pending independent retest. NOT
READY FOR REVIEW for the new production code.
**Validated production commit:** `10021f11c9dd82a6da3fbc028344ba20cef695fa`.
**Validated production app.js blob:** `f1ff89ab16d81953471b3528887ae6a4256e88af`.
**Current-code applicability:** TR-024 did not test the superseded-refresh
change now in progress. Its PASS cannot be carried forward to a new production
SHA; a new independent run is required.

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

## Run history

| Run | Validated production commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-021](details/TR-021-story-012-archive-restore.md) | `225f3989e7761dad1e3ad9a535785e438dc173d0` | PASSED | TC-012-01–05 passed; focused suite 33 passed; full backend regression 261 passed with one historical approved skip. |
| [TR-022](details/TR-022-story-012-review-fix-retest.md) | `fedeb6b9eae10cc864f87225abc774f23d040821` | PASSED | Two review findings independently retested in Chrome; blocking and deferred regression 49 passed, 1 historical skip; full backend 261 passed, 1 historical skip. |
| [TR-023](details/TR-023-story-012-edit-archive-retest.md) | `c72d66e7ce88f7ec403c7032ffdcf71904013e97` | PASSED | Edit/archive guard independently retested in Chrome; blocking/deferred regression 49 passed, 1 historical skip; full backend 261 passed, 1 historical skip. |
| [TR-024](details/TR-024-story-012-archive-ui-retest.md) | `10021f11c9dd82a6da3fbc028344ba20cef695fa` | PASSED | Both latest UI review findings independently retested in Chrome; focused regression 50 passed, 1 historical skip; full backend 263 passed, 1 historical skip. |
