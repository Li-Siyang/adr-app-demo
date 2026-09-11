# Branch Naming Standards

- Feature branches for user stories MUST follow the exact format:
  `feature/<STORY-ID>-<kebab-case-short-description>`
- Examples:
  - `feature/STORY-001-select-mock-identity`
  - `feature/STORY-002-administer-roles-approvers`
  - `feature/STORY-003-create-complete-draft`
- Do not use random session slugs or uninformative branch names.


# Session Orchestration

- The parent coordinating session owns child-session creation, task dispatch,
  status monitoring, result collection, and cross-branch coordination.
- Developer Agent sessions focus on one Jira Story and must not create, fork,
  delete, archive, or coordinate other sessions.
- Developer Agent sessions perform Jira read-only execution preflight, then
  implement, test, commit, and push their assigned Story.
- The parent session must retrieve results when a child becomes idle; child
  sessions are not required to have cross-session messaging capability.
- Every child kickoff must include the Story ID, approved Story title,
  dedicated Jira Story key, related Jira Task keys, approved artifact paths,
  branch name, scope, dependencies, and Definition of Done. Use `None` when no
  related Jira Task keys exist; do not combine Story and Task keys in an
  untyped list.
- Child sessions must not rely on conversational messaging to the parent. They
  must output a structured handoff before becoming idle and persist completed
  work through the feature branch and commits. After independent validation,
  the Pull Request must contain the final completion summary.


# Engineering Principles

All implementation work must follow these principles:

- Prefer simple solutions over unnecessary abstraction.
- Follow SOLID principles where they improve maintainability.
- Follow DRY, but do not introduce abstraction solely to eliminate small duplication.
- Prefer clear and explicit code over clever code.
- Follow existing repository architecture and conventions.
- Keep modules focused on a single responsibility.
- Minimize coupling between components.
- Avoid speculative generalization.
- Write code that is testable and maintainable.
- Do not perform unrelated refactoring within a Story.


# Engineering Standards

Before implementation, read and follow the repository-wide engineering
principles defined in the following files:

- `.github/copilot-instructions.md`

Do not duplicate or redefine those principles in this agent profile.


# Documentation Naming and Versioning

- Document filenames must remain stable and must not contain semantic or
  revision version numbers such as `v1`, `v1.2`, or `2026-09`.
- Store a document's version only in its document metadata.
- Artifact identifiers such as `PLAN-001` and `TEST-001` are stable IDs, not
  version numbers, and may remain in filenames.
- Before creating or updating an artifact, search for its existing canonical
  file and update that file instead of creating a versioned copy.
- When renaming a document, update every repository reference to its new path.

Canonical examples:

- `docs/requirements/requirement-definition.md`
- `docs/planning/PLAN-001-internal-decision-record-mvp.md`
- `docs/test-design/TEST-001-internal-decision-record-mvp.md`

Metadata examples:

- `**Version:** 1.3`
- `**Plan ID:** PLAN-001`
- `**Test Design ID:** TEST-001`