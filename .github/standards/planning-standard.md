# Planning Standard

## Planning inputs

- Planning must use an explicitly approved Requirement Definition.
- The Requirement Definition is the source of product intent.
- Planning must not modify the Requirement Definition.
- Unapproved assumptions must not be used as product requirements.

## Plan quality

A Development Plan must:

- cover all in-scope requirements or explicitly record their coverage gap;
- identify blocking and non-blocking planning gaps;
- preserve Requirement -> Plan -> Epic -> Story -> Task traceability;
- keep source Acceptance Criteria unchanged;
- record dependencies, risks, and recommended implementation order;
- avoid undocumented product behavior and implementation-specific decisions;
- include a Requirement Traceability Matrix; and
- contain no implementation code.

## Epic quality

Each Epic must include:

- Epic ID;
- title;
- objective;
- related Requirement IDs; and
- included Stories.

An Epic must represent a meaningful product capability or development
workstream, not merely one individual requirement.

## Story quality

Each Story must include:

- Story ID;
- title;
- User Story;
- description;
- related Requirement IDs;
- source Acceptance Criteria mapping;
- Acceptance Criteria Gap, when applicable;
- dependencies;
- priority; and
- Story Delivery Definition of Done reference.

Stories must be independently understandable and should be independently
implementable and reviewable where practical. They must not introduce product
behavior or create replacement Acceptance Criteria.

## Task quality

Each Task must include:

- Task ID;
- title;
- parent Story;
- purpose; and
- dependencies.

Tasks must not force a specific library, framework, database, or architecture
unless the approved Requirement Definition makes it an explicit constraint.

## Planning completion criteria

A Development Plan is ready for Human Review only when:

- every in-scope Requirement has been evaluated for Story coverage;
- every Story references its source Requirements;
- every source Acceptance Criterion has been evaluated for Story mapping;
- blocking gaps are explicitly identified;
- dependencies and planning risks have been recorded;
- no undocumented product requirements have been introduced;
- a Requirement Traceability Matrix exists;
- a recommended implementation order is included; and
- no implementation code has been written.

If a blocking requirement gap exists, the plan must be reported as blocked and
must include the gap, impact, and required clarification.
