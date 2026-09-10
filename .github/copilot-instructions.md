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