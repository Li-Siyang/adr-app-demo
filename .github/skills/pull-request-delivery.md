# Pull Request Delivery

Create the single Story PR only after the Validation Agent reports `Overall Status: PASSED` and `Recommendation: READY FOR REVIEW`. Confirm the tested commit is the final branch commit or an ancestor with no unvalidated production changes; otherwise obtain validation again. Default target is `dev`, never `main` unless the repository workflow explicitly requires it.

Use `.github/templates/pull-request-template.md` for the description and preserve its Jira, Story, requirement, Acceptance Criteria, implementation, technical decision, Unit Test, independent validation, limitation, and source-artifact fields. Title format is `[STORY-ID] Story Title`. Include Test Run ID and tested SHA. A PR is not approval: Reviewer Agent and Human Review remain required, and the Developer must never self-merge.

Record PR creation in the structured handoff template with `Outcome: COMPLETED`, exact branch/HEAD, validation evidence, `Blockers: None`, and next action Human Review. Do not mutate Jira; the Jira Agent may synchronize verified events such as `IN DEVELOPMENT`, `READY FOR INDEPENDENT VALIDATION`, `READY FOR RETEST`, and `PR CREATED`.
