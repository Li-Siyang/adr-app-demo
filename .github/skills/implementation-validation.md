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

## Test Result Report output

For every completed or blocked validation run, create and save the
Test Result Report in `docs/test-result/story-NNN/details/` using
`.github/templates/test-result-report-template.md`. Do not leave the report
only in the chat response.

Name each report
`TR-NNN-story-NNN-<short-scope>.md`, where the first `NNN` is the next
unused, zero-padded Test Run ID across both `docs/test-result/` and legacy
`docs/test-results/`, the second `NNN` is the Story ID, and `<short-scope>`
is a concise kebab-case description. For example:
`docs/test-result/story-012/details/TR-014-story-012-archive-restore.md`.

Include the Test Run ID, Story ID, overall status, recommendation, and exact
validated commit SHA in the report. If validation is blocked before a commit
can be identified, record the available branch/commit information and state
why no exact SHA could be validated. Link or report the saved file path in the
validation handoff so PR delivery can verify the evidence.

Maintain a stable per-Story entry point at
`docs/test-result/story-NNN/STORY-NNN-validation-status.md` alongside the
individual run reports in `details/`. When saving a new report, update this
page with the latest run's status, recommendation, exact validated commit,
report link, and a chronological history of report links and outcomes. Keep
all prior reports unchanged. Distinguish the result of the last run from
whether it still applies to the current production code: if production code
changes after a passing run, mark review readiness as pending independent
retest until a new run passes. Do not infer validity merely from a report's
filename or a later documentation-only commit; compare the production
changes against the validated commit. Link the stable entry point in the
validation handoff.

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
