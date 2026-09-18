# Jira Standard

## Role of Jira

Jira is the execution tracking representation of approved artifacts. Jira keys
and fields do not replace canonical repository artifacts.

Source-of-truth ownership:

- Requirement Definition defines product behavior, functional requirements,
  non-functional requirements, business rules, product scope, and Acceptance
  Criteria.
- Development Plan defines Epics, Stories, Engineering Tasks, dependencies,
  priorities, approved work decomposition, and recommended implementation order.
- Test Design defines Test Scenarios, Test Cases, expected validation behavior,
  test traceability, planned validation scope, and approved justification when
  executable testing is not required.
- Jira is authoritative only for execution state and mappings.

## Approval

Approval must be explicit, such as `Status: APPROVED` or `status: approved`.
Do not infer approval from document completeness, file location, previous
conversation context, comments, reviewer names, or implied intent.

## Modification boundaries

Jira coordination may:

- create Jira work items from approved artifacts;
- reuse valid existing Jira work items;
- create approved parent-child relationships;
- create approved dependency links;
- synchronize verified execution state;
- synchronize concise Test Design references; and
- synchronize concise Test Result summaries.

Jira coordination must not:

- modify Requirement Definition, Development Plan, Test Design, or Acceptance
  Criteria;
- introduce new features, business rules, user roles, permissions, workflows,
  acceptance criteria, product behavior, or scope;
- split, merge, add, remove, or re-bound approved Stories;
- create, remove, or re-prioritize approved Engineering Tasks;
- create, remove, weaken, or modify Test Scenarios, Test Cases, expected
  results, coverage decisions, or testing-required decisions;
- change production code or automated tests;
- delete duplicate Jira issues automatically; or
- fabricate execution evidence.

Route artifact issues to the owning agent or Human Reviewer:

- Requirement issue -> Requirement Agent / Human Reviewer
- Planning issue -> Planning Agent / Human Reviewer
- Test Design issue -> Test Design Agent / Human Reviewer

## Traceability

Preserve this Jira traceability chain:

`Requirement -> Acceptance Criterion -> Story -> Task -> Test Scenario -> Test Case -> Jira Work Item`

Every Jira Story must preserve:

- source Story ID;
- related Requirement IDs;
- related Acceptance Criteria IDs;
- related Test Scenario IDs where applicable;
- Test Design evaluation status;
- parent Epic;
- dependencies;
- priority;
- Definition of Done;
- source Requirement document;
- source Development Plan; and
- source Test Design.

Every Jira Sub-task must preserve source Task ID, parent Story, purpose, and
dependencies where relevant.

Every independent Jira Task must preserve source Task ID, related Story IDs
where applicable, purpose, and dependencies where relevant.

Keep Jira execution-focused. Prefer IDs, summaries, execution status, and source
references in Jira; keep complete Requirement, Plan, and Test Design content in
the repository.

## Stable source identifiers and idempotency

Every Jira work item created by the Jira Agent must preserve its stable source
ID, such as `EPIC-001`, `STORY-003`, or `TASK-003-01`.

The stable source ID must be stored in a reliably searchable location:

1. dedicated Jira custom field for Source ID, when configured;
2. otherwise the Jira Summary, such as `[STORY-003] Create Decision`;
3. otherwise a clearly structured Source section in the Description.

Creation must be idempotent. Before creating any Jira Epic, Story, Task, or
Sub-task, search the target Jira project for the exact stable source ID,
evaluate the result, and create only when no valid existing mapping exists.

## Jira tooling

Jira communication must use Jira or Atlassian tools available in the GitHub
Copilot environment.

Before Jira operations, verify tools are available, target project access
exists, required read/write permissions exist, and the requested action is
supported. If tooling is unavailable, report:

`JIRA TOOLING BLOCKED`

Do not claim that a Jira issue was created, modified, linked, or transitioned
unless the corresponding tool operation actually succeeded and was verified.

## Mapping rules

Preferred mapping where Jira supports it:

- Development Plan Epic -> Jira Epic
- Development Plan Story -> Jira Story
- Engineering Task belonging clearly to one Story -> Jira Sub-task
- Engineering Task shared across multiple Stories or independent of one Story
  -> Jira Task

For independent Jira Tasks, use supported issue links to represent
relationships to relevant Stories. Do not invent additional hierarchy levels.

If Jira cannot represent the approved structure, report `JIRA MAPPING BLOCKED`
and do not apply alternatives without explicit Human approval.

## Canonical execution states

Jira project status names vary by configuration. Resolve project statuses to
canonical states before applying gates or transitions:

- To Do
- In Development
- Ready for Test
- Testing
- Test Failed
- Fixing
- Ready for Retest
- Ready for Review
- In Review
- Done
- Blocked

Transitions must be supported by trusted evidence or explicit Human override.
Human override must be recorded without fabricating missing automated evidence.

## Conflict handling

If approved source artifacts conflict, report `JIRA CREATION BLOCKED` with the
conflict, sources, impact, and required owner action.

If existing Jira state conflicts with source mappings, report
`JIRA SOURCE MAPPING CONFLICT` with stable source ID, existing Jira ID, expected
mapping, actual mapping, impact, and required Human action.

If multiple Jira items map to one stable source ID, report
`JIRA DUPLICATE MAPPING BLOCKED` with stable source ID, duplicate Jira IDs,
issue types, parent relationships, and recommended Human review. Do not guess
which issue is canonical and do not delete Jira issues automatically.
