# STORY-006 validation status

**Latest independent run:** [TR-015](details/TR-015-story-006-transfer-ownership.md) — **PASSED; READY FOR REVIEW** for the validated commit.
**Validated production commit:** `bc80af936aded0cc3b586e9c3ce8adfa89354a45`.
**Applicability:** This result covers production code at the stated SHA. Revalidate any subsequent production changes; human review is still required.

All three approved STORY-006 cases passed in independent API/integration
tests: transfer by the author, current owner, or administrator in Draft and
Proposed; denial for unrelated actors, terminal states, and Abandoned Drafts;
and record retention without additional owner/admin edit permission after a
modeled author's departure. The full backend regression suite passed with one
unrelated STORY-009 test deferred until STORY-012.

## Run history

| Run | Validated commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-015](details/TR-015-story-006-transfer-ownership.md) | `bc80af936aded0cc3b586e9c3ce8adfa89354a45` | PASSED | All three STORY-006 cases passed; full backend regression passed with one previously deferred, unrelated skip. |

Preserve the prior reports and update this page with each later run's status,
validated SHA, applicability, and chronological history.
