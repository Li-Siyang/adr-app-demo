# STORY-012 validation status

**Latest independent run:** [TR-023](details/TR-023-story-012-edit-archive-retest.md)
— **PASSED for the historical production commit only**. Current production
changes for PR review comments are pending independent retest; NOT READY FOR
REVIEW. PR #33 is Draft.
**Validated production commit:** `c72d66e7ce88f7ec403c7032ffdcf71904013e97`.
**Validated production tree:** `511705b7e30ff5941b0d3da5c267161e34fa3997`.
**Current-code applicability:** TR-023 does not cover the pending changes to
archive warning placement and in-flight record controls. Do not carry its PASS
forward to the new production SHA; a new independent run is required.

All five blocking STORY-012 Test Cases passed. The assigned administrator-only,
archived exact-tag, deletion-denial, and archival audit/retention regressions
also passed. TC-015-01's comment-deletion event leg remains explicitly
non-blocking and deferred because STORY-011 is absent from the inherited
production branch; no predecessor Story is represented as fully passed.
TR-022 also independently retested both PR review findings in headless Chrome
against the actual UI script and ran the complete backend regression suite.
TR-023 independently retested the editing/archival review fix, including
preservation of unsaved edits and normal archiving after save or cancel.

## Run history

| Run | Validated production commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-021](details/TR-021-story-012-archive-restore.md) | `225f3989e7761dad1e3ad9a535785e438dc173d0` | PASSED | TC-012-01–05 passed; focused suite 33 passed; full backend regression 261 passed with one historical approved skip. |
| [TR-022](details/TR-022-story-012-review-fix-retest.md) | `fedeb6b9eae10cc864f87225abc774f23d040821` | PASSED | Two review findings independently retested in Chrome; blocking and deferred regression 49 passed, 1 historical skip; full backend 261 passed, 1 historical skip. |
| [TR-023](details/TR-023-story-012-edit-archive-retest.md) | `c72d66e7ce88f7ec403c7032ffdcf71904013e97` | PASSED | Edit/archive guard independently retested in Chrome; blocking/deferred regression 49 passed, 1 historical skip; full backend 261 passed, 1 historical skip. |
