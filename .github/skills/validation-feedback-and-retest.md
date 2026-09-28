# Validation Feedback and Retest

Read the Validation Agent report completely: Test Run ID, Story ID, tested commit SHA, failed Test Case IDs, Requirement IDs, expected/actual behavior, classification, severity, and evidence. Do not ignore independent results or modify the branch while validation of a commit is active.

## `IMPLEMENTATION_DEFECT`

Own the fix. Re-read the failed case and Requirement/Acceptance Criterion, reproduce where practical, identify root cause, change production code, add/update Developer-owned Unit Tests, run them, commit the fix, push the feature branch, and complete `.github/templates/developer-handoff-template.md` with `Outcome: READY_FOR_RETEST`, exact new HEAD SHA, `Blockers: None`, and next action Validation Agent retest. Never mark independent validation passed yourself.

## `TEST_DEFECT` or `POSSIBLE_TEST_DEFECT`

Do not modify Validation-Agent-owned tests. Report the case, requirement, evidence, reason it may be incorrect, and classification. Handoff with `Outcome: BLOCKED`, canonical Story/branch fields, blocker classification, and next action Validation Agent/Human Reviewer.

## `REQUIREMENT_AMBIGUITY` and `PLANNING_GAP`

Stop affected implementation. Route ambiguity to Requirement Agent/Human Reviewer; route an insufficient approved Story to Planning Agent/Human Reviewer and report `IMPLEMENTATION PLANNING GAP`. Handoff with `Outcome: BLOCKED`, canonical fields, `N/A` if no commit is available, evidence in summaries, and next action.

## `ENVIRONMENT_FAILURE`

Do not change product behavior to compensate for unrelated infrastructure/test-environment failure. Handoff with `Outcome: FAILED`, canonical fields, `N/A` if unavailable, failure in Blockers, and next action.

Repeat fix/retest until validation passes or escalation blocks progress. A retest must target the pushed fix commit.
