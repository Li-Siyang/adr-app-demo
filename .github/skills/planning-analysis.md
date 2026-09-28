# Planning Analysis Skill

Use this skill to convert an approved Requirement Definition into a
Development Plan.

## Workflow

Follow these steps in order.

### 1. Understand the Requirement Definition

Read the complete approved document and identify:

- product objective;
- scope and out-of-scope items;
- users;
- functional and non-functional requirements;
- business rules;
- acceptance criteria;
- constraints; and
- unresolved open questions.

Use only requirements explicitly documented in the approved source. Do not
modify the Requirement Definition.

### 2. Validate planning readiness

Check for:

- unresolved questions that block implementation;
- contradictory requirements;
- ambiguous acceptance criteria;
- missing business rules;
- requirements that cannot be tested; and
- unclear scope boundaries.

Classify findings as:

- `Blocking Gap`: planning cannot safely continue;
- `Non-blocking Gap`: planning can continue, but the issue must be recorded.

Never resolve a gap by silently choosing product behavior. A missing
Acceptance Criterion is non-blocking only when the intended behavior and scope
are explicit; it blocks implementation readiness when the outcome cannot be
objectively verified.

### 3. Identify Epics

Group related capabilities into a small number of coherent Epics. An Epic
should represent a meaningful product capability or development workstream.
Avoid creating an Epic for every individual requirement.

For each Epic, record its ID, title, objective, related Requirement IDs, and
included Stories. If an Epic is not meaningful for a small change, explicitly
document the approved omission.

### 4. Create User Stories

Break each Epic into independently understandable Stories. Use this format
where appropriate:

`As a [user], I want [capability], so that [business value].`

For each Story:

- preserve its source Requirement mapping;
- map source Acceptance Criteria without weakening or rewriting them;
- record an Acceptance Criteria Gap when no source criterion exists;
- record dependencies and priority; and
- keep the Story small enough to implement and review independently where
  practical.

Do not create artificial Stories solely to increase task count. If a related
requirement has no source Acceptance Criterion, state:

`No source Acceptance Criterion specified.`

Record the Requirement Gap and do not mark the Story implementation-ready until
clarification is provided.

### 5. Create Engineering Tasks

Create Tasks only when doing so adds planning value. Tasks may cover
implementation, validation, persistence, automated tests, integration, or
documentation.

Keep Tasks implementation-oriented without prescribing detailed technical
solutions unless the Requirement Definition explicitly requires them. Every
Task must identify its parent Story, purpose, and dependencies.

### 6. Check requirement and acceptance coverage

Verify that:

- every in-scope Requirement is covered by at least one Story;
- every source Acceptance Criterion is mapped to one or more Stories; and
- uncovered or partially covered items are explicitly reported.

Use the statuses `Covered`, `Partially Covered`, `Not Covered`, and `Blocked`.
Do not mark a requirement as Covered unless the planned work genuinely
addresses it.

### 7. Identify dependencies and implementation order

Identify necessary dependencies between Stories and highlight anything that
could block parallel development. Recommend an implementation order using
dependencies, business value, technical foundations, risk, and incremental
testability. The recommended order is not a new product requirement.

## Blocking output

If a blocking gap is discovered, stop and produce:

```markdown
## PLANNING BLOCKED

### Requirement Gap

Describe the missing or ambiguous information.

### Impact

Explain why planning cannot safely proceed.

### Required Clarification

State the question for the Requirement Agent or human Product Owner.
```
