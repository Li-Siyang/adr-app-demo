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
