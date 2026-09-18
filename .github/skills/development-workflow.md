# Development Workflow

Use this skill for the complete Developer lifecycle before validation.

## 1. Preflight and Story mapping

Read the approved Requirement Definition, Development Plan, and Test Design before changing code. Normally use the explicitly supplied Jira Story. For “Develop the next Story” only when invoked directly, select from approved candidates by satisfied dependencies, approved plan order, plan priority (not Jira Priority), foundational work, and canonical status. Eligible normal states are canonical `To Do` and `In Development`; `Test Failed`, `Fixing`, or `Ready for Retest` are eligible only for an `IMPLEMENTATION_DEFECT`; never start `Ready for Test`, `Testing`, `Ready for Review`, `In Review`, `Done`, or `Blocked`. Report priority mismatches without changing Jira. If equally eligible with no plan order, report options.

Use read-only Jira. First exact-map the stable Story ID across all issue types using the configured Source ID field identifier when available; otherwise exact bracketed Summary, otherwise structured Description Source. If the configured identifier is unavailable, report `JIRA TOOLING BLOCKED`. Do not unrestricted-search or count Tasks that merely mention the Story. Require one issue of type Story, exact stable ID, approved title, and canonical summary `[<Story ID>] <approved Story title>`; a supplied key must identify it, and a child kickoff must repeat the approved title. Read related implementation Tasks and verify status, dependencies, ownership, and artifact references. Zero/multiple/unavailable cases respectively require `JIRA STORY MAPPING BLOCKED`/`JIRA DUPLICATE MAPPING BLOCKED`/`JIRA TOOLING BLOCKED`. Stop without Jira mutation and use the handoff template.

Verify repository, base integration branch (normally `dev`), current state, and dependencies. Search for and reuse one unambiguous Story branch; report `BRANCH MAPPING CONFLICT` for ambiguous ownership or unexpected changes; do not create duplicate suffix branches. Confirm approved Requirement, Plan, Test Design, Jira Story, dependencies, unblocked scope, access, and branch before coding.

## 2. Plan and implement

At the plan step, complete `.github/templates/development-plan-template.md`: approach, files, Unit Tests, decisions, dependencies, risks, and unresolved questions. Inspect architecture, patterns, configuration, and tests. Implement only approved scope using existing conventions. The Developer owns production code and implementation-level Unit Tests; Validation owns requirement-driven Acceptance/Integration/API/E2E/regression tests. Never weaken Validation tests.

Use `Implement → Unit Test → analyze failure → fix` until relevant Unit Tests pass. Make only implementation-level decisions within scope. Escalate architecture/dependency/infrastructure redesign, external security-sensitive decisions, breaking APIs, ambiguity, planning gaps, or scope expansion instead of guessing.

## 3. Checkpoints and validation handoff

Commit coherent logical checkpoints with meaningful messages, verify relevant checks and intended files, and push each meaningful commit. Do not push noise or known broken states unless required. Preserve Story ID in branch/commits where practical. When all relevant Unit Tests pass and no blocker remains, stop modifying the exact pushed state and complete `.github/templates/developer-handoff-template.md` with `Outcome: READY_FOR_INDEPENDENT_VALIDATION`, exact HEAD SHA, `Blockers: None`, and next action independent Validation Agent validation.

Never force-push shared branches, rewrite protected history, delete unrelated remote branches, commit secrets/credentials/generated sensitive files, or bypass protection. Never create or edit Jira data.
