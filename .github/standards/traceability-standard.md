# Traceability Standard

## Delivery chain

Preserve this traceability chain throughout planning and delivery:

```text
Requirement
  -> Plan
  -> Story
  -> Task
  -> Implementation
  -> Test Design
  -> Validation Result
```

## Identifier rules

- Use stable artifact identifiers such as `PLAN-001` and `TEST-001`.
- Preserve existing Requirement, Story, Task, and Acceptance Criterion IDs.
- Every Story must reference the Requirement or Requirements that justify it.
- Every Task must reference its parent Story.
- Test scenarios and cases must reference their Stories and source requirements.
- Jira keys represent execution tracking and must not replace the canonical
  source artifacts.

## Source-of-truth boundaries

- Requirement Definitions define product intent and acceptance criteria.
- Development Plans define approved Epics, Stories, Tasks, dependencies, and
  priorities.
- Test Designs define planned validation coverage after approval.
- Jira represents execution state and mappings; it does not redefine approved
  requirements or test expectations.
