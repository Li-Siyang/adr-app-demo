# Documentation Standard

## Stable filenames

Document filenames must remain stable and must not contain semantic or
revision version numbers such as `v1`, `v1.2`, or `2026-09`.

Store a document's version only in its metadata.

Artifact identifiers such as `PLAN-001` and `TEST-001` are stable IDs, not
version numbers, and may remain in filenames.

## Canonical documents

Before creating or updating an artifact, search for its existing canonical
file and update that file instead of creating a versioned copy.

When renaming a document, update every repository reference to its new path.

Canonical examples:

- `docs/requirements/requirement-definition.md`
- `docs/planning/PLAN-001-internal-decision-record-mvp.md`
- `docs/test-design/TEST-001-internal-decision-record-mvp.md`

Metadata examples:

- `**Version:** 1.3`
- `**Plan ID:** PLAN-001`
- `**Test Design ID:** TEST-001`
