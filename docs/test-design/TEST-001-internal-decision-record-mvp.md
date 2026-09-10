# Test Design: Internal Decision Record MVP

**Test Design ID:** TEST-001
**Version:** 2.0
**Status:** APPROVED
**Mode:** DESIGN MODE
**Source Requirement:** `docs/requirements/requirement-definition.md`, Version 1.3, Approved
**Source Development Plan:** `docs/planning/PLAN-001-internal-decision-record-mvp.md`, Version 1.1, approved by Human Reviewer in merged PR #3
**Scope:** STORY-001 through STORY-016

## Readiness Assessment

- Requirement Version 1.3 is explicitly Approved.
- Development Plan Version 1.1 was explicitly approved by the Human Reviewer
  and merged in PR #3.
- Every planned Story maps to active Requirements and Acceptance Criteria.
- All 38 active Acceptance Criteria are observable and testable.
- No unresolved product question blocks test design.
- Expected behavior comes only from the approved Requirement and Development
  Plan. Production implementation and Jira were not inspected.

## Test Scenarios

| Scenario ID | Title | Related Story | Related Requirements | Related AC | Objective | Test Type | Priority |
|---|---|---|---|---|---|---|---|
| TS-001 | Select a clearly identified Mock identity | STORY-001 | CR-USR-001, CR-USR-011; CR-FR-027–028; CR-NFR-013; CR-BR-018 | AC-037, AC-043–044 | Verify identity selection establishes configured roles and attribution without implying authentication or access protection. | Acceptance / E2E / Negative | High |
| TS-002 | Enforce additive governed roles | STORY-002 | CR-USR-004–006, CR-USR-009–010; CR-FR-009–010; CR-BR-001–002, CR-BR-013, CR-BR-015 | AC-003, AC-006–007, AC-023 | Verify administrator-only actions, approver authority, self-approval, and additive permissions. | Acceptance / Authorization / Business Rule | High |
| TS-003 | Create a complete structured Draft | STORY-003 | CR-FR-003–005, CR-FR-006A, CR-FR-023; CR-BR-010 | AC-002, AC-004, AC-037 | Verify Draft creation captures all required content, separate author and owner, tags, attribution, and the data-use notice. | Acceptance / E2E / Boundary | High |
| TS-004 | Edit and submit an eligible Draft | STORY-004 | CR-FR-006–008, CR-FR-024, CR-FR-030; CR-BR-003, CR-BR-016, CR-BR-019 | AC-004–005, AC-024, AC-047 | Verify author editing and guarded submission while denying changes to abandoned replacement Drafts. | Acceptance / Negative / State Transition | High |
| TS-005 | Decide and restart review of a proposal | STORY-005 | CR-FR-006–010, CR-FR-014; CR-BR-002–004 | AC-006–008, AC-038 | Verify authorized outcomes, self-decision, review invalidation, terminal immutability, and one concurrent outcome. | Acceptance / Integration / Concurrency | High |
| TS-006 | Transfer ownership without changing authorship | STORY-006 | CR-USR-007–008; CR-FR-006A, CR-FR-026, CR-FR-030; CR-BR-011, CR-BR-019 | AC-014, AC-030, AC-047 | Verify the actor and record-condition matrix, authorship preservation, and retained handling after author departure. | Acceptance / Authorization / State Transition | High |
| TS-007 | Govern one active replacement and abandonment | STORY-007 | CR-FR-011–013, CR-FR-030; CR-BR-005–006, CR-BR-013–014, CR-BR-019 | AC-009–011, AC-025, AC-039, AC-046–047 | Verify replacement creation, active-interval endpoints, atomic supersession, and permanent retained abandonment. | Acceptance / Integration / Business Rule | High |
| TS-008 | Preserve immutable history and version navigation | STORY-008 | CR-FR-013–014, CR-FR-030; CR-NFR-003; CR-BR-004–006, CR-BR-009, CR-BR-019 | AC-012–013, AC-038, AC-046–047 | Verify attributed immutable history and valid navigation across accepted, superseded, and abandoned versions. | Acceptance / Integration / Data Integrity | High |
| TS-009 | Discover retained records by one exact tag | STORY-009 | CR-FR-005, CR-FR-015–016; CR-BR-009 | AC-015 | Verify one exact tag filter includes matching current, historical, and archived records without partial matches. | Acceptance / Integration / Negative | High |
| TS-010 | Create and associate basic tags | STORY-010 | CR-FR-005, CR-FR-025 | AC-029 | Verify team-member tag creation and association of one or more tags with records. | Acceptance / Integration | Medium |
| TS-011 | Discuss records with top-level comments | STORY-011 | CR-USR-002; CR-FR-017, CR-FR-019; CR-BR-012 | AC-016, AC-018–019 | Verify attributed top-level comments and author-only auditable soft deletion. | Acceptance / Integration / Negative / Concurrency | High |
| TS-012 | Archive and restore retained records | STORY-012 | CR-FR-020–021, CR-FR-030; CR-NFR-008; CR-BR-007, CR-BR-014, CR-BR-019 | AC-003, AC-020–021, AC-026, AC-034, AC-047 | Verify administrator-only archival, discovery, exact restoration, replacement guards, and preservation of Abandoned. | Acceptance / Integration / State Transition | High |
| TS-013 | Prevent decision-record deletion | STORY-013 | CR-SCP-001; CR-FR-029; CR-OOS-007 | AC-045 | Verify deletion is absent or denied in every lifecycle, archival, and replacement-specific condition. | Acceptance / Negative / Retention | High |
| TS-014 | Enforce demo-data and deployed HTTPS boundaries | STORY-014 | CR-SCP-003; CR-FR-023; CR-NFR-005; CR-BR-010 | AC-032, AC-037 | Verify required data-use notices and HTTPS application traffic in deployed environments. | Acceptance / Configuration / E2E | High |
| TS-015 | Audit and permanently retain governed events | STORY-015 | CR-FR-014, CR-FR-019–021, CR-FR-030; CR-NFR-007–008 | AC-013, AC-018, AC-033–034, AC-046 | Verify complete event coverage, actor/time attribution, immutability, and no expiry or deletion. | Integration / Audit / Retention | High |
| TS-016 | Meet approved capacity and browser compatibility | STORY-016 | CR-SCP-002; CR-NFR-004, CR-NFR-011 | AC-031, AC-036 | Verify all in-scope functions at 25 Mock users and 1,000 records in supported browser versions without a response-time assertion. | Non-functional / Compatibility / E2E | High |

## Test Cases

### STORY-001 — Select a Mock Identity

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-001-01 | TS-001 | STORY-001 | CR-FR-027–028; CR-BR-018 | AC-043 | Multiple preconfigured Mock users have distinct roles. | Open the entry screen; inspect the identity list; select each representative identity; perform an attributed action. | Every identity is labeled Mock; the application uses the selected identity's additive roles and records that identity as actor. | High | E2E |
| TC-001-02 | TS-001 | STORY-001 | CR-NFR-013; CR-BR-018 | AC-044 | Entry and identity-related screens are available. | Inspect all identity-related content and select an administrator identity. | No SSO is required; no content states or implies identity verification, team-membership verification, authorization of the real person, or protection from unauthorized access. | High | Acceptance |
| TC-001-03 | TS-001 | STORY-001 | CR-FR-023 | AC-037 | Entry screen is available. | Open the entry screen. | A visible notice allows only demo or synthetic data and prohibits real internal confidential, regulated personal, and health information. | High | E2E |

### STORY-002 — Administer Additive Roles and Approvers

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-002-01 | TS-002 | STORY-002 | CR-USR-004; CR-BR-001 | AC-003 | Administrator and ordinary Mock identities exist. | As each identity, attempt to designate and remove an approver. | Administrator actions succeed; ordinary-user actions are denied without changing approver designations. | High | API |
| TC-002-02 | TS-002 | STORY-002 | CR-USR-006, CR-USR-009; CR-BR-013 | AC-003 | Non-administrator identity and eligible records exist. | Attempt archive, restore, replacement creation, and replacement-Draft abandonment. | Every administrator-only action is denied and record state is unchanged. | High | API |
| TC-002-03 | TS-002 | STORY-002 | CR-FR-009 | AC-006 | Proposed records and a non-approver identity exist. | Attempt Accept and Reject. | Both actions are denied and no lifecycle outcome is recorded. | High | API |
| TC-002-04 | TS-002 | STORY-002 | CR-USR-005; CR-FR-010; CR-BR-002 | AC-007 | A proposal's author is a designated approver. | Accept one authored proposal and reject an equivalent authored proposal. | Each selected transition succeeds. | High | Acceptance |
| TC-002-05 | TS-002 | STORY-002 | CR-USR-010; CR-BR-015 | AC-023 | One Mock identity holds multiple roles with distinct permissions. | Attempt one action granted by each role and one action granted by none. | Every action granted by any held role succeeds; roles do not revoke each other's permissions; the ungranted action is denied. | High | API |

### STORY-003 — Create a Complete Draft

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-003-01 | TS-003 | STORY-003 | CR-FR-003–005, CR-FR-006A | AC-002 | A team-member Mock identity, owner, and tags exist. | Create a record with title, context, decision, rationale, alternatives, consequences, owner, decision date, and one or more tags. | A Draft is retained with the selected identity as author, the chosen owner as a distinct attribute, all fields, and all selected tags. | High | E2E |
| TC-003-02 | TS-003 | STORY-003 | CR-FR-004 | AC-004 | Draft submission is available. | Omit each required field individually and then omit multiple required fields; attempt submission. | The record remains Draft and every missing required field is identified in each attempt. | High | Acceptance |
| TC-003-03 | TS-003 | STORY-003 | CR-FR-023; CR-BR-010 | AC-037 | Creation and editing screens are available. | Open both screens. | Both display the complete demo-or-synthetic-only data notice and all three prohibited information categories. | High | E2E |

### STORY-004 — Edit and Submit a Draft

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-004-01 | TS-004 | STORY-004 | CR-USR-003; CR-FR-006 | — | Author has an ordinary Draft. | Edit and save its content. | Changes are retained and lifecycle remains Draft. | High | Acceptance |
| TC-004-02 | TS-004 | STORY-004 | CR-USR-003; CR-FR-006 | — | Another user's Draft exists. | Attempt to edit and save its content. | The attempt is denied and content is unchanged. | High | API |
| TC-004-03 | TS-004 | STORY-004 | CR-FR-007–008 | AC-005 | Complete authored Draft has at least one designated approver. | Submit the Draft. | Lifecycle changes from Draft to Proposed. | High | E2E |
| TC-004-04 | TS-004 | STORY-004 | CR-FR-004, CR-FR-024; CR-BR-016 | AC-004, AC-024 | Authored Draft is incomplete and has no designated approver. | Attempt submission. | It remains Draft; every missing field is identified; an actionable message requires at least one designated approver. | High | Acceptance |
| TC-004-05 | TS-004 | STORY-004 | CR-FR-030; CR-BR-016, CR-BR-019 | AC-047 | Active replacement Draft has been marked Abandoned. | Attempt editing and submission as every relevant role. | All attempts are denied; content, lifecycle, and Abandoned condition remain unchanged. | High | API |

### STORY-005 — Review and Decide a Proposal

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-005-01 | TS-005 | STORY-005 | CR-FR-008–010 | AC-006–007 | Equivalent proposals exist for a designated approver and non-approver. | Have each actor attempt Accept and Reject. | The designated approver completes each selected outcome; the non-approver is denied. | High | API |
| TC-005-02 | TS-005 | STORY-005 | CR-FR-006, CR-FR-008; CR-BR-003 | AC-008 | Authored Proposed record has prior or in-progress review. | Save an author edit; attempt a decision before resubmission; then resubmit. | Save atomically returns it to Draft and invalidates review; decision is blocked until it is resubmitted to Proposed. | High | Integration |
| TC-005-03 | TS-005 | STORY-005 | CR-FR-014; CR-BR-004 | AC-038 | Rejected and Superseded records exist. | Attempt content, lifecycle-data, and version-content changes as all roles. | Every change is denied; only separately governed archival condition changes remain possible. | High | API |
| TC-005-04 | TS-005 | STORY-005 | CR-FR-008 | — | One Proposed record is available to two approvers concurrently. | Initiate conflicting Accept and Reject actions. | Exactly one outcome is committed and the record cannot become both Accepted and Rejected. | High | Integration |

### STORY-006 — Transfer Record Ownership

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-006-01 | TS-006 | STORY-006 | CR-USR-007–008; CR-FR-006A; CR-BR-011 | AC-014 | Ordinary Draft and Proposed records exist. | In each state, transfer ownership as author, current owner, and administrator. | Every transfer succeeds; owner changes and author remains unchanged. | High | API |
| TC-006-02 | TS-006 | STORY-006 | CR-FR-006A, CR-FR-030; CR-BR-011, CR-BR-019 | AC-014, AC-047 | Editable, terminal, and Abandoned records exist. | Attempt transfer by an unrelated user and in every ineligible record condition. | Every unauthorized combination is denied; owner and author remain unchanged. | High | API |
| TC-006-03 | TS-006 | STORY-006 | CR-FR-026 | AC-030 | A record's Mock author is represented as having left; owner and administrator remain. | Retrieve the record; perform otherwise-granted owner/admin actions; attempt author-only editing without another grant. | Record remains; owner/admin retain only existing permissions; departure grants no additional edit permission. | High | Integration |

### STORY-007 — Govern Replacement Versions

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-007-01 | TS-007 | STORY-007 | CR-FR-011; CR-BR-004–005 | AC-009 | Accepted record exists. | Attempt direct editing as each role. | Editing is prevented and Accepted content is unchanged. | High | API |
| TC-007-02 | TS-007 | STORY-007 | CR-FR-012; CR-BR-005, CR-BR-013–014 | AC-010 | Accepted record has no active replacement. | Administrator starts a replacement. | A linked Draft is created without changing the original and counts as active immediately. | High | Integration |
| TC-007-03 | TS-007 | STORY-007 | CR-FR-012; CR-BR-013–014 | AC-003, AC-025 | Accepted records respectively have no replacement and one active replacement. | A non-administrator attempts creation on the first; an administrator attempts a second on the other. | Both attempts are denied and replacement counts remain unchanged. | High | API |
| TC-007-04 | TS-007 | STORY-007 | CR-FR-013; CR-BR-006 | AC-011, AC-039 | Proposed replacement and Accepted original exist. | Accept the replacement. | Replacement becomes Accepted and original atomically becomes Superseded; links remain and no active replacement remains. | High | Integration |
| TC-007-05 | TS-007 | STORY-007 | CR-FR-012; CR-BR-014 | AC-039 | Active replacement is Proposed. | Reject it; then create a new replacement. | Rejected replacement ceases to be active; original stays Accepted; new linked replacement creation succeeds. | High | Integration |
| TC-007-06 | TS-007 | STORY-007 | CR-FR-030; CR-BR-019 | AC-046 | Active replacement Draft exists. | Administrator marks it Abandoned, inspects original/link/audit, navigates both directions, and starts a new replacement. | It remains Draft with permanent Abandoned condition, ceases to be active, is retained and linked, leaves original Accepted and unchanged, creates actor/time audit evidence, and permits a new replacement. | High | Acceptance / Integration |
| TC-007-07 | TS-007 | STORY-007 | CR-FR-030; CR-BR-019 | AC-003, AC-047 | Active replacement Draft exists. | Non-administrator attempts abandonment; administrator attempts it on ordinary Draft, Proposed replacement, Accepted, Rejected, and Superseded records. | Every attempt is denied and no target gains Abandoned. | High | API |
| TC-007-08 | TS-007 | STORY-007 | CR-FR-030; CR-NFR-003; CR-BR-019 | AC-047 | Abandoned replacement Draft exists. | Attempt changes to content, lifecycle, ownership, approvers, and version data; attempt removal, reactivation, and submission. | Every attempt is denied and the retained record remains permanently unchanged and Abandoned. | High | API |

### STORY-008 — View Immutable Change and Version History

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-008-01 | TS-008 | STORY-008 | CR-FR-013 | AC-012 | Linked Superseded original and Accepted replacement exist. | View each and navigate to the related version. | Navigation resolves correctly in both directions. | High | E2E |
| TC-008-02 | TS-008 | STORY-008 | CR-FR-030 | AC-046 | Accepted original and linked Abandoned replacement exist. | Navigate from each record to the other. | Both retained records remain reachable through the correct links. | High | E2E |
| TC-008-03 | TS-008 | STORY-008 | CR-FR-014; CR-NFR-003 | AC-013 | Record has known changes by known Mock identities at known times. | Compare displayed history with the changes and attempt to modify entries. | History identifies what, who, and when for every change and cannot be modified. | High | Integration |
| TC-008-04 | TS-008 | STORY-008 | CR-FR-014, CR-FR-030; CR-BR-004, CR-BR-009, CR-BR-019 | AC-038, AC-047 | Rejected, Superseded, and Abandoned records and a multi-version chain exist. | Attempt mutation; traverse all links repeatedly. | Mutation is denied; records and history remain retrievable; links resolve without unintended cycles or corruption. | High | Integration |

### STORY-009 — Discover Records by Exact Tag

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-009-01 | TS-009 | STORY-009 | CR-FR-015–016; CR-BR-009 | AC-015 | Exact target tag is assigned across Draft, Proposed, Accepted, Rejected, Superseded, and archived records. | Apply the target as the one exact tag filter. | Every matching record is returned, including Rejected, Superseded, and archived records. | High | E2E |
| TC-009-02 | TS-009 | STORY-009 | CR-FR-015 | AC-015 | Records use the target tag, a longer tag containing its text, and an unrelated tag. | Apply the target exact tag filter. | Only records associated with the exact selected tag are returned. | High | Integration |

### STORY-010 — Create and Associate Tags

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-010-01 | TS-010 | STORY-010 | CR-FR-025 | AC-029 | Team-member Mock identity is selected. | Create a tag and associate it with a record. | The tag becomes available and is retained on the record. | High | Acceptance |
| TC-010-02 | TS-010 | STORY-010 | CR-FR-005, CR-FR-025 | AC-029 | Multiple tags are available. | Associate multiple selected tags with one record and retrieve it. | Every selected tag is associated with the record without removing the others. | Medium | Integration |

### STORY-011 — Discuss a Decision

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-011-01 | TS-011 | STORY-011 | CR-FR-017 | AC-016 | Team-member Mock identity and record exist. | Add a top-level comment and retrieve the record. | Comment is visible and attributed to the selected Mock identity. | High | Acceptance |
| TC-011-02 | TS-011 | STORY-011 | CR-FR-019; CR-BR-012 | AC-018 | Comment author has an undeleted comment. | Delete the comment and inspect its audit evidence. | `[deleted]` replaces content and retained audit evidence identifies the deleting Mock identity. | High | Integration |
| TC-011-03 | TS-011 | STORY-011 | CR-FR-019; CR-BR-012 | AC-019 | Another identity's comment exists. | Attempt deletion. | Deletion is denied and content is unchanged. | High | API |
| TC-011-04 | TS-011 | STORY-011 | CR-FR-019; CR-BR-012 | AC-018 | One comment is available to concurrent author deletion requests. | Submit simultaneous deletion requests. | One `[deleted]` placeholder remains and required audit attribution is preserved without content reappearing. | Medium | Integration |

### STORY-012 — Archive and Restore Records

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-012-01 | TS-012 | STORY-012 | CR-FR-020; CR-BR-007 | AC-020 | Administrator and eligible records in every lifecycle status exist. | Archive each record and discover it. | Each is marked archived, retained, and remains discoverable. | High | Integration |
| TC-012-02 | TS-012 | STORY-012 | CR-FR-020–021; CR-BR-007 | AC-003 | Non-administrator and archived/unarchived records exist. | Attempt archive and restore. | Both actions are denied and conditions are unchanged. | High | API |
| TC-012-03 | TS-012 | STORY-012 | CR-FR-021 | AC-021 | Records archived from each lifecycle status exist. | Restore each as administrator. | Each returns to the lifecycle status held immediately before archival. | High | Integration |
| TC-012-04 | TS-012 | STORY-012 | CR-FR-020; CR-BR-014 | AC-026 | Accepted original has active Proposed replacement. | Attempt to archive original; resolve replacement as Accepted and, in an equivalent fixture, Rejected; retry when applicable. | Initial archival is denied; after either review outcome the active-Proposed block no longer applies. | High | Integration |
| TC-012-05 | TS-012 | STORY-012 | CR-FR-021, CR-FR-030; CR-BR-019 | AC-047 | Abandoned replacement Draft exists. | Archive and restore it as administrator. | Restoration preserves Draft lifecycle and Abandoned condition, does not reactivate it, and leaves it immutable. | High | Integration |

### STORY-013 — Prevent Decision-Record Deletion

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-013-01 | TS-013 | STORY-013 | CR-FR-029; CR-OOS-007 | AC-045 | Records cover every lifecycle status plus active replacement, Abandoned, and archived conditions. | As every role inspect available actions and attempt permanent and soft record deletion through supported interfaces. | No deletion action is available or every attempt is denied; every record remains retained. | High | API / E2E |
| TC-013-02 | TS-013 | STORY-013 | CR-SCP-001; CR-FR-029 | AC-045 | Records from TC-013-01 remain. | Perform otherwise-permitted archive and restore operations. | Archive and restore remain available under their rules and do not delete records. | High | Acceptance |

### STORY-014 — Enforce Demo Data and Deployed HTTPS Boundaries

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-014-01 | TS-014 | STORY-014 | CR-SCP-003; CR-FR-023; CR-BR-010 | AC-037 | Entry, creation, and editing screens are available. | Inspect each screen. | Each visibly permits only demo or synthetic data and prohibits all three named real-data categories. | High | E2E |
| TC-014-02 | TS-014 | STORY-014 | CR-NFR-005 | AC-032 | Representative deployed environment and local development environment exist. | Access the deployed client and exercise subsequent application traffic; inspect the local environment separately. | Deployed client-facing and subsequent application traffic use HTTPS; no equivalent HTTPS assertion is applied to local development. | High | Configuration / Integration |

### STORY-015 — Audit and Permanently Retain Governed Events

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-015-01 | TS-015 | STORY-015 | CR-NFR-007 | AC-033 | Fixtures support every governed event category. | Trigger role change, approver change, each lifecycle transition, archive, restore, abandonment, ownership transfer, and comment deletion. | A corresponding audit record is created for every event category. | High | Integration |
| TC-015-02 | TS-015 | STORY-015 | CR-FR-019, CR-FR-030; CR-NFR-007 | AC-018, AC-033, AC-046 | Comment deletion and abandonment are performed by known Mock identities. | Inspect their audit records. | Comment deletion identifies the deleting Mock identity; abandonment identifies acting administrator and time. | High | Integration |
| TC-015-03 | TS-015 | STORY-015 | CR-FR-014; CR-NFR-003, CR-NFR-008 | AC-013, AC-034 | Audit entries and archived records exist. | Attempt modification, expiry assignment, and permanent deletion; retrieve them repeatedly. | Audit entries are immutable; neither audit entries nor archived records have retention expiry or a permanent deletion path and both remain retrievable. | High | Security / Integration |

### STORY-016 — Meet Capacity and Compatibility Requirements

| Test Case ID | Parent Scenario | Story | Related Requirements | Related AC | Preconditions | Test Steps | Expected Result | Priority | Recommended Automation |
|---|---|---|---|---|---|---|---|---|---|
| TC-016-01 | TS-016 | STORY-016 | CR-SCP-002; CR-NFR-004 | AC-031 | 25 preconfigured Mock users and 1,000 representative decision records exist. | Exercise every in-scope functional Acceptance Criterion against the approved-capacity dataset and identities. | Every applicable functional Acceptance Criterion remains satisfied; no response-time assertion is made. | High | Integration / E2E |
| TC-016-02 | TS-016 | STORY-016 | CR-NFR-011 | AC-036 | Current and immediately prior major Chrome and Edge versions are identified at execution time. | Run all in-scope acceptance workflows on each of the four browser/version combinations. | Every in-scope function is supported in each required browser/version combination. | High | E2E |

## Test Traceability Matrix

| Requirement | Acceptance Criterion | Story | Scenario | Test Case | Coverage |
|---|---|---|---|---|---|
| CR-FR-003, CR-FR-028 | AC-002 | STORY-003 | TS-003 | TC-003-01 | Covered |
| CR-USR-004, CR-USR-006, CR-USR-009; CR-BR-001, CR-BR-013, CR-BR-019 | AC-003 | STORY-002, STORY-007, STORY-012 | TS-002, TS-007, TS-012 | TC-002-01–02, TC-007-03, TC-007-07, TC-012-02 | Covered |
| CR-FR-004 | AC-004 | STORY-003, STORY-004 | TS-003, TS-004 | TC-003-02, TC-004-04 | Covered |
| CR-FR-007–008; CR-BR-016 | AC-005 | STORY-004 | TS-004 | TC-004-03 | Covered |
| CR-FR-009 | AC-006 | STORY-002, STORY-005 | TS-002, TS-005 | TC-002-03, TC-005-01 | Covered |
| CR-FR-010; CR-BR-002 | AC-007 | STORY-002, STORY-005 | TS-002, TS-005 | TC-002-04, TC-005-01 | Covered |
| CR-FR-006, CR-FR-008; CR-BR-003 | AC-008 | STORY-005 | TS-005 | TC-005-02 | Covered |
| CR-FR-011; CR-BR-004–005 | AC-009 | STORY-007 | TS-007 | TC-007-01 | Covered |
| CR-FR-012; CR-BR-005, CR-BR-013–014 | AC-010 | STORY-007 | TS-007 | TC-007-02 | Covered |
| CR-FR-013; CR-BR-006 | AC-011 | STORY-007 | TS-007 | TC-007-04 | Covered |
| CR-FR-013 | AC-012 | STORY-008 | TS-008 | TC-008-01 | Covered |
| CR-FR-014; CR-NFR-003 | AC-013 | STORY-008, STORY-015 | TS-008, TS-015 | TC-008-03, TC-015-03 | Covered |
| CR-FR-006A; CR-BR-011 | AC-014 | STORY-006 | TS-006 | TC-006-01–02 | Covered |
| CR-FR-015–016; CR-BR-009 | AC-015 | STORY-009 | TS-009 | TC-009-01–02 | Covered |
| CR-FR-017 | AC-016 | STORY-011 | TS-011 | TC-011-01 | Covered |
| CR-FR-019; CR-BR-012 | AC-018 | STORY-011, STORY-015 | TS-011, TS-015 | TC-011-02, TC-011-04, TC-015-02 | Covered |
| CR-FR-019; CR-BR-012 | AC-019 | STORY-011 | TS-011 | TC-011-03 | Covered |
| CR-FR-020; CR-BR-007 | AC-020 | STORY-012 | TS-012 | TC-012-01 | Covered |
| CR-FR-021; CR-BR-007 | AC-021 | STORY-012 | TS-012 | TC-012-03 | Covered |
| CR-USR-010; CR-BR-015 | AC-023 | STORY-002 | TS-002 | TC-002-05 | Covered |
| CR-FR-024; CR-BR-016 | AC-024 | STORY-004 | TS-004 | TC-004-04 | Covered |
| CR-FR-012; CR-BR-014 | AC-025 | STORY-007 | TS-007 | TC-007-03 | Covered |
| CR-FR-020; CR-BR-014 | AC-026 | STORY-012 | TS-012 | TC-012-04 | Covered |
| CR-FR-005, CR-FR-025 | AC-029 | STORY-010 | TS-010 | TC-010-01–02 | Covered |
| CR-FR-026 | AC-030 | STORY-006 | TS-006 | TC-006-03 | Covered |
| CR-SCP-002; CR-NFR-004 | AC-031 | STORY-016 | TS-016 | TC-016-01 | Covered |
| CR-NFR-005 | AC-032 | STORY-014 | TS-014 | TC-014-02 | Covered |
| CR-NFR-007 | AC-033 | STORY-015 | TS-015 | TC-015-01–02 | Covered |
| CR-NFR-008 | AC-034 | STORY-012, STORY-015 | TS-012, TS-015 | TC-012-01, TC-015-03 | Covered |
| CR-NFR-011 | AC-036 | STORY-016 | TS-016 | TC-016-02 | Covered |
| CR-FR-023; CR-BR-010 | AC-037 | STORY-001, STORY-003, STORY-014 | TS-001, TS-003, TS-014 | TC-001-03, TC-003-03, TC-014-01 | Covered |
| CR-FR-014; CR-BR-004 | AC-038 | STORY-005, STORY-008 | TS-005, TS-008 | TC-005-03, TC-008-04 | Covered |
| CR-FR-012; CR-BR-014 | AC-039 | STORY-007 | TS-007 | TC-007-04–06 | Covered |
| CR-FR-027–028; CR-BR-018 | AC-043 | STORY-001 | TS-001 | TC-001-01 | Covered |
| CR-NFR-013; CR-BR-018 | AC-044 | STORY-001 | TS-001 | TC-001-02 | Covered |
| CR-FR-029 | AC-045 | STORY-013 | TS-013 | TC-013-01–02 | Covered |
| CR-FR-030; CR-BR-019 | AC-046 | STORY-007, STORY-008, STORY-015 | TS-007, TS-008, TS-015 | TC-007-06, TC-008-02, TC-015-02 | Covered |
| CR-FR-030; CR-NFR-003; CR-BR-019 | AC-047 | STORY-004, STORY-006–008, STORY-012 | TS-004, TS-006–008, TS-012 | TC-004-05, TC-006-02, TC-007-07–08, TC-008-04, TC-012-05 | Covered |

## Business Rule Coverage

| Business Rule | Direct Test Cases | Coverage |
|---|---|---|
| CR-BR-001–002 | TC-002-01, TC-002-04 | Covered |
| CR-BR-003–004 | TC-004-01–02, TC-005-02–03, TC-007-01, TC-008-04 | Covered |
| CR-BR-005–006 | TC-007-01–02, TC-007-04 | Covered |
| CR-BR-007 | TC-012-01–03 | Covered |
| CR-BR-009–010 | TC-003-03, TC-008-04, TC-009-01, TC-014-01 | Covered |
| CR-BR-011–012 | TC-006-01–02, TC-011-02–04 | Covered |
| CR-BR-013–014 | TC-002-02, TC-007-02–05, TC-012-04 | Covered |
| CR-BR-015–016 | TC-002-05, TC-004-03–05 | Covered |
| CR-BR-018–019 | TC-001-01–02, TC-004-05, TC-006-02, TC-007-06–08, TC-012-05 | Covered |

## Cross-Story Regression Risks

| Risk | Stories Most Exposed | Required Regression Focus |
|---|---|---|
| Mock identity context or attribution leaks between selections. | STORY-001–STORY-003, STORY-011, STORY-015 | Role changes, identity switching, authorship, comments, and audit actor attribution. |
| Concurrent lifecycle actions produce conflicting outcomes. | STORY-004–STORY-005, STORY-007, STORY-012 | Submission, review invalidation, one proposal outcome, replacement acceptance, abandonment, and archive guards. |
| Replacement operations corrupt immutable history or links. | STORY-007–STORY-008 | Atomic supersession, one active replacement, abandonment, bidirectional links, and no cycles. |
| Archival changes lifecycle or replacement conditions. | STORY-007, STORY-012–STORY-013 | Prior-status restoration, Proposed-replacement guard, Abandoned preservation, and record retention. |
| Comment deletion removes evidence or affects decision records. | STORY-011, STORY-013, STORY-015 | Placeholder, author authorization, audit attribution, concurrency, and distinction from record deletion. |
| Capacity or browser changes expose workflow-specific defects. | STORY-016 | Full functional acceptance suite against capacity data and each browser/version combination. |

## Test Design Gaps and Execution Constraints

- No requirement ambiguity blocks this design.
- Permanent retention cannot be proven by waiting forever. Validation must
  combine the absence of expiry and permanent-delete behavior with applicable
  retention-control evidence and repeated retrieval.
- The exact Chrome and Edge major versions are resolved at execution time
  because the approved requirement defines them relatively.
- AC-031 requires the complete functional acceptance set at approved capacity;
  it intentionally has no response-time measurement.
- CR-NFR-006, CR-NFR-010, and CR-NFR-012 are approved best-effort scope
  constraints. They do not create mandatory performance, availability, or
  accessibility tests.

## Approved Scope Constraints

- Mock identity selection demonstrates roles and attribution but is not
  authentication, team-membership verification, or a security boundary.
- Only demo or synthetic data may be used.
- Backup/recovery, encryption at rest, tag administration, comment replies,
  record deletion, and formal response-time targets are outside MVP scope.
- Out-of-scope items are guardrails and do not introduce positive behavior
  beyond the active Requirements and Acceptance Criteria.

## Open Testing Questions

None. Test entry points, fixture implementation, concurrency tooling, deployed
HTTPS evidence, capacity data generation, and browser execution infrastructure
are deferred to VALIDATION MODE without changing expected behavior.

## Quality Gate

- All 38 active Acceptance Criteria are evaluated and Covered.
- All 17 explicit Business Rules have direct coverage.
- Every STORY-001 through STORY-016 has a scenario and executable test cases.
- Important happy, negative, boundary, business-rule, state-transition,
  concurrency, integration, E2E, regression, and approved non-functional risks
  are covered where applicable.
- Retired SSO, Draft deletion, comment reply, tag administration, encryption at
  rest, backup/recovery, and response-time expectations are not treated as
  active behavior.
- Expected results are observable and independent of production implementation.
- Requirement to Acceptance Criterion to Story to Scenario to Test Case
  traceability is preserved.

**Recommendation:** READY FOR HUMAN REVIEW
