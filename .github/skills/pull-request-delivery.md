# Pull Request Delivery

Create the single Story PR as a Draft PR only when early collaboration is
needed. A Draft PR may lack final validation, but its description must clearly
state the validation blocker and it must not be marked Ready for Review.

Create or mark the single Story PR Ready for Review only after the Validation
Agent reports `Overall Status: PASSED` and `Recommendation: READY FOR REVIEW`.
Confirm the tested commit is the final branch commit or an ancestor with no
unvalidated production changes; otherwise obtain validation again. A missing
report, `FAILED` or `BLOCKED` report, unmet dependency, or report for a
different commit is a hard blocker for Ready for Review. If a dependency was
unavailable, obtain the blocked dependency and rerun the affected validation
before requesting review. Default target is `dev`, never `main` unless the
repository workflow explicitly requires it.

Use `.github/templates/pull-request-template.md` for the description and
preserve its Jira, Story, requirement, Acceptance Criteria, implementation,
technical decision, Unit Test, independent validation, limitation, and
source-artifact fields. Title format is `[STORY-ID] Story Title`. Include Test
Run ID and tested SHA. A PR is not approval: Reviewer Agent and Human Review
remain required, and the Developer must never self-merge.

Record PR creation in the structured handoff template with `Outcome: COMPLETED`, exact branch/HEAD, validation evidence, `Blockers: None`, and next action Human Review. Do not mutate Jira; the Jira Agent may synchronize verified events such as `IN DEVELOPMENT`, `READY FOR INDEPENDENT VALIDATION`, `READY FOR RETEST`, and `PR CREATED`.
