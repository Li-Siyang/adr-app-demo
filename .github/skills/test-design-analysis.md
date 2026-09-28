# Test Design Analysis Skill

Use this skill to create implementation-independent Test Design from approved
requirements and approved planning artifacts.

## Workflow

### 1. Confirm design readiness

Verify that:

- the Requirement Definition is explicitly approved;
- the Development Plan is explicitly approved;
- Stories can be traced back to Requirements;
- Acceptance Criteria are sufficiently testable; and
- unresolved questions do not prevent test design.

Jira is not required as an input. Do not inspect production implementation to
determine expected behavior.

### 2. Identify test inputs

Extract:

- Functional Requirement IDs;
- Non-functional Requirement IDs;
- Business Rule IDs;
- Acceptance Criteria IDs;
- Story IDs;
- Story scope;
- Story dependencies; and
- approved constraints.

### 3. Select relevant test categories

For each Story, consider these categories where applicable:

- Happy Path tests for expected successful behavior.
- Negative tests for invalid, prohibited, or rejected behavior.
- Boundary tests for minimum, maximum, empty, null, and transition boundaries.
- Business Rule tests for explicit business rules.
- State Transition tests for approved lifecycle behavior.
- Acceptance tests for approved Acceptance Criteria.
- Integration tests for meaningful component or boundary interactions.
- End-to-End tests for important complete user workflows.
- Regression risk coverage for existing capabilities that may be affected.
- Non-functional tests only when supported by approved non-functional
  requirements.

Do not invent performance, security, availability, accessibility, or scalability
expectations that are not approved requirements.

### 4. Design Test Scenarios and Test Cases

Create Test Scenarios from Stories, Requirements, and Acceptance Criteria.
Create Test Cases from Test Scenarios with observable expected results.

Recommended automation levels may include:

- Integration
- API
- Acceptance
- E2E
- Manual

Do not prescribe implementation-level Unit Test structure during test design.
Unit Tests belong primarily to the Developer Agent.

### 5. Produce test traceability

Create a Test Traceability Matrix using this chain:

```text
Requirement
  -> Acceptance Criterion
  -> Story
  -> Test Scenario
  -> Test Case
```

Use these coverage statuses:

- `Covered`
- `Partially Covered`
- `Not Covered`
- `Blocked`

Every approved Acceptance Criterion must be evaluated for test coverage.

## Blocking output

If a blocking ambiguity exists, stop and produce:

```markdown
## TEST DESIGN BLOCKED: REQUIREMENT CLARIFICATION REQUIRED

### Ambiguity

Describe the missing or unclear requirement information.

### Impact

Explain why Test Design cannot safely proceed.

### Required Clarification

State the question for the Requirement Agent or human Product Owner.
```
