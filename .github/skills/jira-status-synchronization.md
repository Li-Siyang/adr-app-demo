# Jira Status Synchronization Skill

Use this skill after Jira execution work items exist to synchronize verified
execution state.

Status sync must not redefine Requirement Definition, Development Plan, Test
Design, Story scope, Acceptance Criteria, priorities, or dependencies.

## Evidence rules

Status transitions that represent external execution facts must be supported by
observable evidence. Do not treat unsupported natural-language claims as
verified execution evidence.

Trusted evidence by canonical state:

- **Ready for Test:** Developer Agent reports
  `READY FOR INDEPENDENT VALIDATION`; required Developer-owned Unit Tests were
  actually executed and passed. Prefer CI results, test command output, or a
  structured Developer Agent report where available.
- **Testing:** Validation Agent actually started validation or an associated
  test execution job actually started.
- **Test Failed / Fixing:** Validation Agent produced a Failure Report,
  classification includes `IMPLEMENTATION_DEFECT`, and affected Test Case IDs
  are available.
- **Ready for Retest:** Developer Agent reports implementation fix complete and
  relevant Unit Tests were actually executed and passed.
- **Ready for Review:** Validation Agent produced a Test Result Report with
  Overall Status `PASSED` and Recommendation `READY FOR REVIEW`.
- **In Review:** a Pull Request actually exists and the PR reference can be
  verified.
- **Done:** Pull Request exists, required review and Human approval exist,
  Pull Request is merged, required validation passed, and no known blocking
  execution item remains. Do not mark Done solely because implementation was
  written.

Actual Jira transition names depend on project configuration. Resolve project
status names or IDs to canonical states before acting.

## Workflow

### 1. Verify the source event

Read the evidence source and verify it is sufficient for the requested
canonical state. Do not fabricate missing automated evidence.

### 2. Verify Jira tooling and mapping

Verify Jira tools are available, the target issue exists, the stable source ID
matches the approved source artifact, the issue type is compatible, and required
links or parent relationships are consistent.

If Jira tools are unavailable, report `JIRA TOOLING BLOCKED`.

### 3. Verify the transition

Verify the target Jira transition exists and required transition fields are
known. Do not claim Jira status support from assumptions.

### 4. Apply the transition

Perform the Jira transition or concise field/comment update only after evidence
and transition validation pass.

### 5. Verify final state

Re-read Jira and verify the new state. Do not claim success until Jira confirms
the updated status.

### 6. Report the result

Use `.github/templates/jira-status-sync-report-template.md`. If blocked, use
`.github/templates/jira-blocked-report-template.md`.

## Test result synchronization

After Validation Agent validation, Jira may contain a concise execution summary:

- Test Status
- Test Run ID
- approved Test Case count
- passed, failed, and blocked counts
- Recommendation

Do not copy large logs into Jira. Detailed evidence belongs in CI, test reports,
Pull Request checks, or repository artifacts.

## Failure synchronization

When validation fails, Jira may record Test Run ID, failed Test Case IDs,
failure classification, severity, short expected vs. actual summary, and next
owner.

Do not reinterpret Validation Agent failure classification.

## Human override

An authorized Human may explicitly request a Jira state change, for example:

`I have manually verified the Story. Move it to Done.`

When using a Human override:

1. make clear that the transition is Human-authorized;
2. do not fabricate missing automated evidence;
3. record the override reason where appropriate; and
4. verify that Jira allows the requested transition.

Human override does not retroactively create test evidence that does not exist.
