# Jira Work Item Creation Skill

Use this skill to convert approved repository artifacts into Jira execution
work items.

Creation mode has two phases:

1. Preview Phase
2. Execution Phase

The Preview Phase is mandatory unless the user explicitly waives it. The
Execution Phase may begin only after explicit human approval of the preview.

## Required sources

Before previewing or creating Jira work items, locate and read:

- approved Requirement Definition under `docs/requirements/`;
- approved Development Plan under `docs/planning/`; and
- approved Test Design under `docs/test-design/`.

All required artifacts must be explicitly approved. If any required artifact is
missing or not explicitly approved, stop and report:

`JIRA CREATION BLOCKED: Required source artifact is missing or not explicitly approved.`

Every Story must have approved Test Design evaluation before Jira creation. The
evaluation must show either approved Test Scenarios, Test Cases, and Acceptance
Criteria coverage, or `NO_EXECUTABLE_TEST_REQUIRED` with Story ID,
justification, and approved validation method if any. Absence of Test Design is
not equivalent to testing not required. If a Story lacks evaluation, stop that
Story and report:

`JIRA CREATION BLOCKED: Story has no approved Test Design evaluation.`

## Workflow

### 1. Verify Jira tooling

Verify Jira tools are available, the target project is accessible, permissions
allow the requested operation, and the action is supported. If tooling is
unavailable, report:

`JIRA TOOLING BLOCKED`

Do not simulate success.

### 2. Inspect Jira project configuration

Inspect the target Jira project before creating work items. Verify available
issue types, required fields, supported hierarchy, parent-child relationships,
dependency link types, and required project-specific metadata.

Do not assume support for exactly Epic, Story, Task, or Sub-task. If Jira cannot
faithfully represent the approved Plan structure, use
`.github/templates/jira-blocked-report-template.md` and report
`JIRA MAPPING BLOCKED`.

### 3. Validate cross-artifact traceability

Verify this chain for every affected item:

`Requirement -> Acceptance Criterion -> Story -> Test Scenario or approved testing exception`

Check for unmapped Requirements, Acceptance Criteria without test evaluation,
Stories without Test Design evaluation, Test Scenarios referencing unknown
Stories, and conflicts between Plan and Test Design. Do not repair these
problems yourself.

### 4. Validate plan structure

Confirm every Story belongs to an Epic unless the approved Plan explicitly
omits Epics, subordinate Tasks belong to a Story, independent Tasks are
explicitly justified, dependencies are understandable, and priorities exist
where required.

Do not split, merge, add, remove, or re-prioritize approved Stories or Tasks.

### 5. Search existing Jira mappings

Before preview or creation, search the target Jira project for each exact stable
source ID using the configured Source ID field when available, otherwise the
exact bracketed ID in Summary, otherwise a clearly structured Source section in
Description.

Classify each source item:

- `NEW`
- `REUSABLE`
- `CONFLICT`
- `DUPLICATE`
- `UNKNOWN`

Only create a new item when no valid existing mapping exists. Do not proceed
with `CONFLICT`, `DUPLICATE`, or `UNKNOWN` items without resolution.

Existing item handling:

- **No match:** create the work item during Execution Phase.
- **Exactly one valid match:** verify project, compatible issue type, exact
  source ID, and parent relationship where applicable; reuse and report
  `Reused`.
- **One conflicting match:** stop the affected item and report
  `JIRA SOURCE MAPPING CONFLICT`.
- **Multiple matches:** stop the affected item and report
  `JIRA DUPLICATE MAPPING BLOCKED`.

If an operation may have timed out after creating an item, search by stable
source ID and create only if absence is confirmed. Never assume a timeout means
creation failed.

### 6. Produce the preview

Use `.github/templates/jira-creation-preview-template.md`. For each source item
show source ID, proposed Jira type, proposed title, `CREATE` or `REUSE`, existing
Jira ID when reused, Requirement IDs, Acceptance Criteria IDs, Engineering Task
IDs, Test Design ID, Test Design evaluation, Test Scenario IDs where applicable,
dependencies, parent relationship, and priority.

Do not create or modify Jira work items during the Preview Phase.

### 7. Apply the approval gate

Valid approval examples include:

- `Approved. Create the Jira issues.`
- `The Jira preview is approved.`

Do not infer approval from silence, a request to prepare a preview, or previous
conversation context.

### 8. Create or reuse work items

Preferred mapping where supported:

- Development Plan Epic -> Jira Epic
- Development Plan Story -> Jira Story
- Engineering Task belonging clearly to one Story -> Jira Sub-task
- Engineering Task shared across Stories or independent of one Story -> Jira Task

For independent Jira Tasks, use supported issue links to represent
relationships to relevant Stories. Do not invent additional hierarchy levels.

For every approved Epic, Story, Task, or Sub-task:

1. search;
2. verify;
3. reuse or create;
4. verify final mapping.

Use `.github/templates/jira-issue-content-template.md` for issue content.
Preserve Requirement mappings, Acceptance Criteria mappings, Test Design
references, dependencies, priorities, and Definition of Done.

### 9. Link work items

Represent supported relationships:

- Epic -> Story
- Story -> Sub-task
- independent Task <-> Story
- Story dependency -> Story

Before creating a link, verify whether the equivalent link already exists. Do
not create duplicate relationships.

### 10. Verify final Jira state

After operations, re-read created or reused Jira items and verify source ID,
hierarchy, required fields, and important relationships. Do not assume an API
success response proves the final state is correct.

### 11. Produce the mapping summary

Use `.github/templates/jira-mapping-summary-template.md`. Creation is complete
only when every approved Epic, Story, and Engineering Task has been evaluated;
each Story has approved Test Design evaluation; Jira references relevant Test
Design; traceability is preserved; approved artifacts and Story boundaries are
unchanged; valid existing Jira mappings were reused; duplicates were not
created; dependencies are represented where supported; final mappings are
verified; and a Jira Mapping Summary is produced.

## Recovery and retry

Creation mode must be safe to run repeatedly. On partial failure, reuse
previously verified successful mappings and retry only missing, previously
failed, or explicitly approved retry items. Do not automatically retry
destructive or ambiguous operations.
