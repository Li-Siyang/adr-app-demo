# Development Workflow

Use this skill for the complete Developer lifecycle before validation.

## 1. Preflight and Story mapping

Read the approved Requirement Definition, Development Plan, and Test Design before changing code. Normally use the explicitly supplied Jira Story. For “Develop the next Story” only when invoked directly, select from approved candidates by satisfied dependencies, approved plan order, plan priority (not Jira Priority), foundational work, and canonical status. Eligible normal states are canonical `To Do` and `In Development`; `Test Failed`, `Fixing`, or `Ready for Retest` are eligible only for an `IMPLEMENTATION_DEFECT`; never start `Ready for Test`, `Testing`, `Ready for Review`, `In Review`, `Done`, or `Blocked`. Report priority mismatches without changing Jira. If equally eligible with no plan order, report options.

Use read-only Jira. First exact-map the stable Story ID across all issue types using the configured Source ID field identifier when available; otherwise exact bracketed Summary, otherwise structured Description Source. If the configured identifier is unavailable, report `JIRA TOOLING BLOCKED`. Do not unrestricted-search or count Tasks that merely mention the Story. Require one issue of type Story, exact stable ID, approved title, and canonical summary `[<Story ID>] <approved Story title>`; a supplied key must identify it, and a child kickoff must repeat the approved title. Read related implementation Tasks and verify status, typed dependencies, ownership, and artifact references. Zero/multiple/unavailable cases respectively require `JIRA STORY MAPPING BLOCKED`/`JIRA DUPLICATE MAPPING BLOCKED`/`JIRA TOOLING BLOCKED`. Stop without Jira mutation and use the handoff template.

Before coding, verify that the Story dependency graph and the selected Story's
Task dependency graph are acyclic for start and completion dependencies. Confirm
that every Task has an executable start and completion path and that at least
one Task order can complete the parent Story. A Task cycle or unreachable Task
requires `PLANNING GAP`; do not choose an arbitrary Task to bypass it.

Evaluate dependencies using the approved Plan:

- a start dependency is satisfied by traceable evidence that its named
  capability or artifact is available;
- a completion dependency requires the predecessor Story to satisfy its
  Definition of Done before the dependent Story can complete;
- an integration-validation dependency does not block development start, but
  must be included in the validation plan.

For an approved legacy Plan created before typed Story or Task dependencies
were required, apply this compatibility path:

- do not infer a Completion dependency or require the predecessor Story to be
  Done;
- when the Plan's dependency narrative names a concrete prerequisite
  capability or artifact and observable evidence shows it is available, record
  `LEGACY DEPENDENCY INTERPRETATION` and provisionally treat it as a Start
  dependency for development selection and start only;
- list the source Plan text and evidence in the Developer handoff; and
- require Planning Agent migration before creating new Jira dependency links
  or reporting the dependent Story complete.

Apply the same interpretation independently to each legacy Task dependency.
Do not infer Task completion dependencies, and do not use the compatibility
path when provisional Task Start dependencies would form a cycle or leave no
executable Task order.

If the legacy Plan does not name a concrete prerequisite or the evidence is
missing or ambiguous, stop with `PLANNING GAP`. This compatibility path does
not modify the approved Plan, create a Completion dependency, or waive any
validation.

For an approved legacy Test Design with only one Story field, a Test Case that
explicitly requires a capability assigned by the approved Plan to a later
Story does not become a start gate. Preserve its existing Story as the coverage
Story, record `LEGACY DEFERRED EXECUTION INTERPRETATION`, and provisionally
identify the later capability-owning Story as execution owner. Require Test
Design migration before validating the affected deferred case or reporting
either affected Story complete. If ownership is not explicit from the approved
artifacts, stop with `PLANNING GAP`.

Do not treat every Jira `blocks` link as proof that the predecessor Story must
be Done. If Jira loses the approved dependency type, conflicts with the Plan,
or the combined Plan and Test Design create a cycle after applying the legacy
compatibility path, stop with `PLANNING GAP` and identify the exact dependency
requiring Planning Agent or Human correction.

Verify repository, base integration branch (normally `dev`), current state, and
dependencies. Search for and reuse one unambiguous Story branch; report
`BRANCH MAPPING CONFLICT` for ambiguous ownership or unexpected changes; do not
create duplicate suffix branches. Confirm approved Requirement, Plan, Test
Design, Jira Story, satisfied start dependencies, unblocked scope, access, and
branch before coding.

## 2. Plan and implement

At the plan step, complete `.github/templates/development-plan-template.md`: approach, files, Unit Tests, decisions, dependencies, risks, and unresolved questions. Inspect architecture, patterns, configuration, and tests. Implement only approved scope using existing conventions. The Developer owns production code and implementation-level Unit Tests; Validation owns requirement-driven Acceptance/Integration/API/E2E/regression tests. Never weaken Validation tests.

Use `Implement → Unit Test → analyze failure → fix` until relevant Unit Tests pass. Make only implementation-level decisions within scope. Escalate architecture/dependency/infrastructure redesign, external security-sensitive decisions, breaking APIs, ambiguity, planning gaps, or scope expansion instead of guessing.

## 3. Checkpoints and validation handoff

Commit coherent logical checkpoints with meaningful messages, verify relevant checks and intended files, and push each meaningful commit. Do not push noise or known broken states unless required. Preserve Story ID in branch/commits where practical. When all relevant Unit Tests pass and no blocker remains, stop modifying the exact pushed state and complete `.github/templates/developer-handoff-template.md` with `Outcome: READY_FOR_INDEPENDENT_VALIDATION`, exact HEAD SHA, `Blockers: None`, and next action independent Validation Agent validation.

Never force-push shared branches, rewrite protected history, delete unrelated remote branches, commit secrets/credentials/generated sensitive files, or bypass protection. Never create or edit Jira data.
