# Testing Standard

## Correctness principle

- Requirement Definition defines expected product behavior.
- Approved Test Design defines planned validation behavior.
- Implementation does not define correctness.
- Jira does not define correctness.

## Source-of-truth rules

- Requirement Definitions are authoritative for expected behavior, functional
  requirements, non-functional requirements, business rules, scope, and
  acceptance criteria.
- Development Plans are authoritative for Epics, Stories, Engineering Tasks,
  dependencies, priorities, and approved work decomposition.
- Approved Test Designs are authoritative for Test Scenarios, Test Cases,
  expected test behavior, test traceability, and validation scope.
- The repository is authoritative for current implementation, existing
  automated tests, architecture, and test infrastructure.

The repository may explain how validation is executed, but it must not redefine
approved expected behavior.

## Approval rules

- Requirement Definition and Development Plan must be explicitly approved
  before Test Design creation.
- New Test Design documents must initially use `Status: DRAFT`.
- The Test Design Agent must never approve its own Test Design.
- Only explicit Human approval can change a Test Design to `Status: APPROVED`.
- Approved Test Design remains stable unless the Requirement Definition,
  Acceptance Criteria, Development Plan scope, or explicit Human-approved Test
  Design correction changes.
- Implementation differences alone are not a valid reason to change approved
  expected behavior.

## Ownership boundaries

- Requirement Agent owns product intent and Acceptance Criteria.
- Planning Agent owns Epics, Stories, Tasks, dependencies, and priorities.
- Test Design Agent owns Test Scenarios, Test Cases, and Test Design.
- Developer Agent owns production implementation and implementation-level Unit
  Tests.
- Validation Agent owns requirement-driven automated tests, independent
  validation execution, failure classification, and Test Result reporting.
- Jira Agent owns representing approved test information and verified execution
  state in Jira.

## Test quality

Requirement-driven tests must:

- have clear and observable expected results;
- trace to Requirements, Acceptance Criteria, and Stories;
- avoid unnecessary dependency on implementation details;
- evaluate relevant happy paths, negative paths, boundary cases, business
  rules, state transitions, and regression risks;
- clearly state execution status; and
- be reported as passed only after successful execution.

## Failure classifications

Use exactly one classification for each failed Test Case:

- `IMPLEMENTATION_DEFECT`: the implementation violates an approved Requirement,
  Business Rule, Acceptance Criterion, or approved Test Case.
- `TEST_DEFECT`: the executable test incorrectly represents the approved Test
  Design or approved Requirement.
- `REQUIREMENT_AMBIGUITY`: expected behavior cannot be determined from approved
  artifacts.
- `PLANNING_GAP`: the approved implementation scope does not appear sufficient
  to satisfy an approved Requirement or Test Case.
- `ENVIRONMENT_FAILURE`: the failure is caused by unavailable dependencies,
  CI infrastructure, browser environment, test data environment, external
  service outage, or tooling failure.

Do not classify a test as defective merely because production code fails it.
Do not classify an environment failure as an implementation defect without
evidence.

## Test Design completion criteria

Test Design is ready for Human Review only when:

- Requirement and Plan are explicitly approved;
- relevant Stories have Test Scenarios;
- relevant Acceptance Criteria have been evaluated for coverage;
- important Business Rules are covered;
- important negative and boundary behavior has been considered;
- a Test Traceability Matrix exists;
- Test Design is stored as `Status: DRAFT`;
- no Jira dependency was required; and
- no implementation behavior was used to define correctness.

## Validation completion criteria

Validation is complete only when:

- all approved Test Cases have been evaluated;
- required automated tests have been executed where practical;
- failures have been classified;
- requirement coverage has been evaluated;
- regression impact has been evaluated;
- a Test Result Report has been produced; and
- the implementation is classified as `READY FOR REVIEW`, `NOT READY FOR
  REVIEW`, or `BLOCKED`.
