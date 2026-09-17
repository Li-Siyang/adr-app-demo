# Session Orchestration Skill

Use this skill when coordinating work across parent and child sessions.

## Responsibilities

- The parent coordinating session owns child-session creation, task dispatch,
  status monitoring, result collection, and cross-branch coordination.
- Developer Agent sessions focus on one Jira Story and must not create, fork,
  delete, archive, or coordinate other sessions.
- Developer Agent sessions perform Jira read-only execution preflight, then
  implement, test, commit, and push their assigned Story.
- The parent session retrieves results when a child becomes idle.

## Child-session kickoff contract

Every child kickoff must include:

- Story ID
- approved Story title
- dedicated Jira Story key
- related Jira Task keys, or `None`
- approved artifact paths
- branch name
- scope
- dependencies
- Definition of Done

Do not combine Story and Task keys in an untyped list.

## Handoff contract

Child sessions must not rely on conversational messaging to the parent.
Before becoming idle, they must output a structured handoff and persist
completed work through the feature branch and commits.

After independent validation, the Pull Request must contain the final
completion summary.
