# Implementation Validation Skill

Use this skill to independently validate completed implementation against
approved requirements and approved Test Design.

## Workflow

### 1. Confirm validation readiness

Verify that:

- implementation exists;
- approved Test Design exists;
- relevant Developer-owned Unit Tests passed where applicable; and
- the required test environment is available.

If these conditions are not met, report the appropriate blocker.

If a required Story dependency is not available, do not claim the Story is
validated. Produce a `BLOCKED` Test Result Report naming the dependency and
the affected validation scope. If the Story can be isolated using approved
fixtures, mocks, or stubs, validate only that explicitly identified scope and
record the untested integration scenarios. After the dependency becomes
available, rerun all affected acceptance, integration, state-transition, and
regression cases before recommending review.

### 2. Map approved Test Cases to execution

For each approved Test Case, classify it as:

- `Automated`
- `Manual`
- `Not Yet Automated`
- `Blocked`
- `Not Applicable` with approved justification

Do not silently remove Test Cases from validation scope.

### 3. Inspect implementation only for execution and diagnosis

Implementation inspection is allowed for:

- automating an approved Test Case;
- locating integration boundaries;
- diagnosing failures;
- selecting appropriate test entry points; and
- understanding technical test setup.

Implementation inspection must not redefine expected behavior.

### 4. Implement requirement-driven tests

Where appropriate, implement or update:

- Acceptance Tests;
- Integration Tests;
- API Tests;
- End-to-End Tests; and
- regression tests.

Do not modify production code.

### 5. Execute tests

Run relevant tests and broader regression suites where practical and useful.
Never report a test as passed unless it was actually executed successfully.

### 6. Compare expected and actual behavior

For each Test Case, compare the approved Expected Result with the Actual Result.
Do not adjust Expected Result merely because implementation behaves differently.

## Validation and PR status

Validation status controls PR readiness:

- `PASSED` for the current tested commit permits a Ready for Review request.
- `FAILED`, `BLOCKED`, missing validation evidence, or a stale tested commit
  prohibits Ready for Review.
- A Draft PR may be opened for collaboration while validation is blocked, but
  it must identify the blocker and remain a Draft.
- Any production change after a passing validation requires validation of the
  new commit before review.

## Failure classification use

Classify every failed Test Case using the classifications defined in
`.github/standards/testing-standard.md`.

Confirmed implementation defects return to the Developer Agent. During retest:

1. Re-run the failed Test Case.
2. Re-run directly related Test Scenarios.
3. Run relevant regression tests.
4. Confirm independently whether the defect is resolved.

Do not accept a Developer Agent statement that the defect is fixed without
independent execution.
