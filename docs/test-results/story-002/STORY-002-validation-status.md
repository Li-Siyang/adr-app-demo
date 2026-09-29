# STORY-002 validation status

**Latest independent run:** [TR-015](details/TR-015-story-002-role-authorization.md) — **BLOCKED**.
**Validated production commit:** `146aaa5a560afa8d2cbe659c7b08150c1799e402`.
**Current-code applicability:** The Developer-owned governance tests and
Validation-Agent acceptance tests pass at this commit, but full Story
validation remains blocked by TC-002-02's dependent governed actions.

TR-015 ran the Developer-owned governance unit tests and all available
STORY-002 acceptance tests: **21 passed**. The full backend regression passed
with **141 passed and 1 approved unrelated skip**. TC-002-01, TC-002-03,
TC-002-04, and TC-002-05 passed. TC-002-02 remains blocked because archive,
restore, replacement creation, and replacement abandonment are assigned to
later Stories and are not exposed by the current backend API. Review readiness
is not established.

## Run history

| Run | Validated commit | Result | Key finding |
| --- | --- | --- | --- |
| [TR-015](details/TR-015-story-002-role-authorization.md) | `146aaa5a560afa8d2cbe659c7b08150c1799e402` | BLOCKED | 21 targeted tests and full regression passed; TC-002-02 dependent actions unavailable. |
