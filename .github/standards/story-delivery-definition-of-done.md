# Story Delivery Definition of Done

A Story is complete only when all applicable conditions are satisfied:

- The implementation satisfies the approved Story and mapped acceptance
  criteria.
- Required implementation-level tests are added and pass.
- Existing relevant tests pass.
- Independent validation is complete when required by the approved Test Design.
- A required dependency blocker is explicitly recorded; a blocked validation
  does not count as completion.
- Documentation is updated when the change requires it.
- Traceability to the source Requirement, Plan, Story, Task, and Test Design is
  preserved.
- The change is committed on the Story feature branch.
- The Pull Request contains the final completion summary and validation result.

PR readiness is separate from Draft PR collaboration:

- A Draft PR may be created before final validation when early collaboration is
  necessary, but it must remain clearly marked as Draft.
- A PR may be marked Ready for Review or treated as complete only when the
  Validation Agent has produced a `PASSED` result for the current tested
  commit.
- A `FAILED`, `BLOCKED`, missing, or stale validation result blocks Ready for
  Review until the affected validation is rerun and passes.

If a condition is not applicable, record the reason explicitly rather than
silently omitting it.
