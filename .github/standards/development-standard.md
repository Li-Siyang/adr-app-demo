# Development Standard

## Scope and authority

Development implements one approved Jira Story only. Approved Requirement, Development Plan, and Test Design are authoritative respectively for product intent, scope/tasks/dependencies/order, and validation scenarios. Jira is an execution and traceability source, not a replacement for those artifacts. Escalate ambiguity, planning gaps, architecture changes, new significant dependencies, security-sensitive decisions outside approved artifacts, breaking API changes, or scope expansion to the appropriate agent or Human Reviewer; do not guess.

## Ownership boundaries

The Developer owns production code, implementation decisions, implementation-level Unit Tests, local checks, commits, pushes, and fixes classified `IMPLEMENTATION_DEFECT`. The Validation Agent owns requirement-driven Acceptance, Integration, API, End-to-End, and independent regression tests. Never weaken, skip, delete, or rewrite Validation-Agent-owned tests; report `POSSIBLE TEST DEFECT` with evidence. Requirements, planning, test design, Jira synchronization, review, and merge remain with their named owners.

## Jira read-only preflight

Use only read-only Jira access. With a supplied key, and when searching, first perform an exact stable Story-ID mapping across all issue types: use the configured Source ID field when the project provides its identifier; otherwise use the exact bracketed ID in Summary, otherwise the structured Source section in Description. If the identifier is unavailable, report `JIRA TOOLING BLOCKED` rather than claiming a custom-field-only mapping was absent. Never use unrestricted full-text search or count Tasks that merely mention a Story.

Accept exactly one Jira **Story** whose stable ID and approved title match the source artifacts and whose summary is exactly `[<Story ID>] <approved Story title>`; a supplied key must identify that same issue. Read related implementation Tasks for traceability, verify execution status/dependencies/ownership/references, and resolve configured status names/IDs to canonical states. Zero matches: `JIRA STORY MAPPING BLOCKED`; multiple: `JIRA DUPLICATE MAPPING BLOCKED`; unavailable tools/resource: `JIRA TOOLING BLOCKED`. A readable non-eligible status is also `BLOCKED` and must not be modified. Never create/edit/transition Jira issues, comments, fields, links, assignees, priorities, sprints, or dependencies, and never substitute a GitHub Issue or infer a Jira key.

## Branch and repository safety

Use one Story, one dedicated feature branch, and one PR. Create from the configured integration branch (normally `dev`), never directly on `main`, `master`, or shared `dev` without explicit Human authorization. Before branching, verify repository/base branch, search for an existing Story branch, and reuse an unambiguous match. Never create `-2` duplicates. Report `BRANCH MAPPING CONFLICT` for ambiguous ownership or unexpected changes. Do not force-push shared branches, rewrite protected history, delete unrelated remote branches, commit secrets/credentials/generated sensitive files, or bypass protection.

## Implementation and checkpoints

Confirm approved Requirement, Plan, Test Design, Jira Story, satisfied dependencies, unblocked scope, access, and safe branch before production changes. Inspect architecture, conventions, related code, configuration, and tests. Stay within scope; avoid unrelated refactoring and speculative abstractions. Make implementation-level decisions only within the approved scope and existing architecture.

Write meaningful Unit Tests for relevant internal behavior, normal/invalid/boundary cases, and regressions. Iterate `Implement → Unit Test → analyze → fix`. Commit coherent logical checkpoints with meaningful messages (prefer Story IDs), verify relevant checks and intended files first, and push every meaningful checkpoint to the feature branch. Do not commit known broken intermediate states unless explicitly required, and do not push noise.

## Deterministic handoffs

Before independent validation, require implementation and Developer-owned Unit Tests complete and passing, affected checks run where practical, no implementation blocker or unresolved ambiguity, a committed and pushed state, and record its exact HEAD SHA. Every outcome uses `.github/templates/developer-handoff-template.md` with exactly: Outcome (`READY_FOR_INDEPENDENT_VALIDATION`, `READY_FOR_RETEST`, `COMPLETED`, `BLOCKED`, or `FAILED`), Story ID, Jira Story key, Branch, HEAD commit SHA or `N/A`, Implementation summary, Test and validation summary, Blockers or `None`, and Next recommended action.

Completion requires approved scope, dedicated branch, meaningful pushed commits, appropriate Unit Tests passing, independent validation PASS on the traceable commit, one correctly targeted PR, complete requirement/test traceability, no unapproved scope, and Human Review still required or separately complete.
