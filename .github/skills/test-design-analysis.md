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
- Story dependencies, their types, and their stated satisfaction evidence; and
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

For each Test Case, record both:

- the coverage Story or Stories whose Requirements or Acceptance Criteria the
  case verifies; and
- the execution-owning Story that supplies the last capability required to run
  the case.

These may be the same Story. When a case verifies an earlier capability across
a later workflow, preserve the earlier coverage Story and assign execution to
the later capability-owning Story as non-blocking integration or regression
coverage. Do not make the earlier Story wait for future implementation.

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

### 6. Check lifecycle feasibility

Compare Test Cases with the approved dependency types and recommended
implementation order. Verify that:

- every Story can execute all tests required for its Definition of Done using
  its own scope and satisfied start or completion dependencies;
- no blocking Test Case requires a capability assigned only to a later Story;
- deferred integration or regression coverage is explicitly identified as
  non-blocking for the earlier Story; and
- the combined Plan and Test Design contain no start or completion cycle.

If a test is required by an Acceptance Criterion but cannot run until a later
Story, report `TEST DESIGN BLOCKED: PLANNING CORRECTION REQUIRED` with the
affected Stories, Test Cases, dependency cycle, and required Planning Agent or
Human action. Do not silently mark the earlier Story's validation as deferred.

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
