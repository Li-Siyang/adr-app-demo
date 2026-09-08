# Development Plan

## 1. Source Requirement

Requirement document: `docs/requirements/requirement-definition-v1.md`

Requirement version: 1.1

Requirement status: Approved

Planning date: 2026-09-01

---

## 2. Planning Summary

This plan delivers the Internal Decision Record Application MVP for one internal
team. The work is organized around access control, decision lifecycle,
versioning, discovery, comments, archival, and operational quality.

Authentication and authorization are foundational dependencies. Core record
creation and lifecycle behavior precede versioning, archival, comments, and
discovery. Audit, confidentiality, retention, recovery, performance, and browser
compatibility apply across the product.

No product-level planning blocker remains. Engineering risks center on
concurrent lifecycle actions, immutable history, immediate access revocation,
atomic version and tag operations, permanent Draft deletion, and recovery
verification.

---

## 3. Planning Readiness

### Blocking Gaps

No blocking requirement gaps identified.

### Non-blocking Gaps

No non-blocking requirement gaps identified. The approved availability and
accessibility statements are scope constraints rather than measurable delivery
targets.

---

## 4. Epics

### EPIC-001: Secure Team Access and Role Administration

Objective: Restrict the application to authenticated team members and enforce
additive role permissions, including approver administration.

Related Requirements: CR-USR-001–006, CR-USR-009–010, CR-FR-001–002,
CR-FR-009–010, CR-NFR-001–002, CR-BR-001–002, CR-BR-013, CR-BR-015.

Stories: STORY-001, STORY-002

### EPIC-002: Decision Record Authoring and Lifecycle

Objective: Create complete decision records and move them safely through the
approved review lifecycle.

Related Requirements: CR-USR-003, CR-FR-003–010, CR-FR-023–024,
CR-BR-003–004, CR-BR-010, CR-BR-016.

Stories: STORY-003, STORY-004, STORY-005

### EPIC-003: Ownership, Versioning, and History

Objective: Preserve authorship and immutable history while supporting ownership
transfer and controlled evolution of Accepted decisions.

Related Requirements: CR-USR-007–009, CR-FR-006A, CR-FR-011–014, CR-FR-026,
CR-NFR-003, CR-BR-005–006, CR-BR-011, CR-BR-013–014.

Stories: STORY-006, STORY-007, STORY-008

### EPIC-004: Discovery and Tag Governance

Objective: Discover all authorized decisions by one exact tag and maintain tag
references without losing records.

Related Requirements: CR-FR-005, CR-FR-015–016, CR-FR-025, CR-BR-009,
CR-BR-017.

Stories: STORY-009, STORY-010

### EPIC-005: Decision Discussion

Objective: Support simple discussion through comments, single-level replies,
and auditable soft deletion.

Related Requirements: CR-USR-002, CR-FR-017–019, CR-BR-012.

Stories: STORY-011

### EPIC-006: Archival, Restoration, and Draft Deletion

Objective: Retain published records, restore archived records to their prior
state, and permanently delete eligible Drafts under approved rules.

Related Requirements: CR-USR-006, CR-FR-020–022, CR-BR-007–008, CR-BR-014.

Stories: STORY-012, STORY-013

### EPIC-007: Security, Audit, and Operational Quality

Objective: Meet the approved confidentiality, capacity, performance, audit,
retention, recovery, and compatibility requirements.

Related Requirements: CR-SCP-002–003, CR-NFR-001–012.

Stories: STORY-014, STORY-015, STORY-016

---

## 5. User Stories

### STORY-001: Authenticate and Restrict Team Access

**User Story**

As an internal team member, I want to authenticate through organizational SSO
so that I can securely access decision records.

**Description**

Permit access only to authenticated members of the designated team and remove
access when membership is lost.

**Related Requirements**

CR-USR-001–002; CR-FR-001–002; CR-NFR-001–002.

**Source Acceptance Criteria Mapping**

AC-001: Access is denied to anyone who is not an authenticated member of the
designated team.

**Dependencies**

None.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-002: Administer Additive Roles and Approvers

**User Story**

As an administrator, I want to designate approvers and apply additive user roles
so that only authorized users can make governed decisions.

**Description**

Enforce administrator-only approver administration and replacement creation,
while allowing a user to hold additive roles and a designated approver to
self-approve.

**Related Requirements**

CR-USR-004–006, CR-USR-009–010; CR-FR-009–010; CR-BR-001–002,
CR-BR-013, CR-BR-015.

**Source Acceptance Criteria Mapping**

AC-003: Non-administrators cannot designate approvers, archive, restore, or
create replacements. AC-006: Non-approvers cannot decide a Proposed record.
AC-007: A designated approver may decide their own Proposed record. AC-023:
permissions from multiple held roles are additive.

**Dependencies**

STORY-001.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-003: Create a Complete Draft

**User Story**

As a team member, I want to create a structured Draft so that the decision and
its rationale can be reviewed and understood later.

**Description**

Create a Draft with the required content, distinct author and owner, one or more
tags, and the mandatory information-handling notice.

**Related Requirements**

CR-BG-001–002; CR-OBJ-001–002; CR-USR-003, CR-USR-007; CR-FR-003–005,
CR-FR-006A, CR-FR-023; CR-BR-010.

**Source Acceptance Criteria Mapping**

AC-002: A new record is Draft and records its creator as author. AC-004: Missing
required fields are identified when submission is attempted. AC-037: Creation
and editing screens display the prohibited-information notice.

**Dependencies**

STORY-001.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-004: Edit and Submit a Draft

**User Story**

As an author, I want to edit and submit a complete Draft so that an approver can
review it.

**Description**

Allow the author to edit Draft content and transition it to Proposed only when
all required fields and at least one designated approver are present.

**Related Requirements**

CR-USR-003; CR-FR-006, CR-FR-007–008, CR-FR-024; CR-BR-003, CR-BR-016.

**Source Acceptance Criteria Mapping**

AC-004: Incomplete Draft submission is prevented. AC-005: A complete Draft with
an approver becomes Proposed. AC-024: Submission without an approver is
prevented with an actionable message.

**Dependencies**

STORY-002, STORY-003.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-005: Review and Decide a Proposal

**User Story**

As a designated approver, I want to accept or reject a Proposed decision so that
the team has a clear outcome.

**Description**

Permit only designated approvers to decide a proposal. If the author edits a
Proposed record, return it to Draft, invalidate review, and require
resubmission. Rejected records are immutable.

**Related Requirements**

CR-FR-006–010; CR-FR-014; CR-BR-002–004.

**Source Acceptance Criteria Mapping**

AC-006–007 map approval authorization and self-approval. AC-008 maps automatic
return to Draft and review invalidation after editing. AC-038 maps immutability
of Rejected and Superseded records.

**Dependencies**

STORY-004.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-006: Transfer Record Ownership

**User Story**

As an author, owner, or administrator, I want to transfer a Draft or Proposed
record without changing authorship so that responsibility can change safely.

**Description**

Allow only approved roles and lifecycle states to transfer ownership. Retain
records when an author leaves, without granting additional permissions.

**Related Requirements**

CR-USR-007–008; CR-FR-006A, CR-FR-026; CR-BR-011.

**Source Acceptance Criteria Mapping**

AC-014: Approved roles may transfer Draft or Proposed records and authorship is
unchanged; all other combinations are denied. AC-030: A departed author's
record remains and the owner or administrator retains only otherwise-granted
actions.

**Dependencies**

STORY-002, STORY-003.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-007: Create and Decide a Replacement Version

**User Story**

As an administrator, I want to create one replacement version of an Accepted
record so that the decision can evolve without altering its history.

**Description**

Create a linked Draft replacement only when no active replacement exists. Keep
it active until Accepted, Rejected, or deleted, and atomically supersede the
previous Accepted version when its replacement is Accepted.

**Related Requirements**

CR-USR-009; CR-FR-011–013; CR-BR-005–006, CR-BR-013–014.

**Source Acceptance Criteria Mapping**

AC-009: Accepted content cannot be edited directly. AC-010: An administrator
creates a linked active Draft. AC-011: Acceptance supersedes the prior version.
AC-025: A second active replacement is denied. AC-039: Accepted, Rejected, or
deleted replacements cease to be active.

**Dependencies**

STORY-002, STORY-005.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-008: View Immutable Change and Version History

**User Story**

As a reader, I want to inspect change history and navigate linked versions so
that I can understand how a decision evolved.

**Description**

Expose immutable change history and bidirectional navigation between
Superseded and replacement versions.

**Related Requirements**

CR-OBJ-002; CR-FR-013–014; CR-NFR-003; CR-BR-004–006, CR-BR-009.

**Source Acceptance Criteria Mapping**

AC-012: Readers can navigate between related versions. AC-013: History shows
what changed, who changed it, and when, and cannot be modified. AC-038:
Rejected and Superseded content is immutable.

**Dependencies**

STORY-003, STORY-007.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-009: Discover Records by Exact Tag

**User Story**

As a team member, I want to filter by one exact tag so that I can find relevant
current and historical records.

**Description**

Return authorized matching records, including Rejected, Superseded, and
archived records.

**Related Requirements**

CR-FR-005, CR-FR-015–016; CR-BR-009.

**Source Acceptance Criteria Mapping**

AC-015: Exact single-tag filtering returns matching authorized records,
including matching Rejected, Superseded, and archived records.

**Dependencies**

STORY-003.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-010: Create and Govern Tags

**User Story**

As a team member, I want to create tags, while administrators maintain them, so
that decision classification remains usable.

**Description**

Allow team tag creation and administrator-only rename, merge, and deletion,
while updating references and never deleting associated records.

**Related Requirements**

CR-FR-025; CR-BR-017.

**Source Acceptance Criteria Mapping**

AC-029 maps tag creation and administrator-only maintenance. AC-040 maps rename
reference updates. AC-041 maps merge replacement. AC-042 maps association-only
deletion with record preservation.

**Dependencies**

STORY-002, STORY-003.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-011: Discuss a Decision

**User Story**

As a team member, I want to comment and add a single-level reply so that I can
contribute to decision discussion.

**Description**

Support top-level comments, one reply level, and author-only soft deletion that
preserves replies and audit evidence.

**Related Requirements**

CR-USR-002; CR-FR-017–019; CR-BR-012.

**Source Acceptance Criteria Mapping**

AC-016 maps comment creation. AC-017 maps single-level replies. AC-018 maps
author soft deletion, `[deleted]`, preserved replies, and audit evidence.
AC-019 denies deletion by another user. AC-028 denies nested replies.

**Dependencies**

STORY-001, STORY-003.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-012: Archive and Restore Records

**User Story**

As an administrator, I want to archive a record and restore its prior lifecycle
state so that it can leave active use without being lost.

**Description**

Archive any lifecycle state, retain and discover archived records permanently,
restore the pre-archive state, and block archival of an Accepted original while
its replacement is Proposed.

**Related Requirements**

CR-USR-006; CR-FR-020–021; CR-BR-007, CR-BR-014; CR-NFR-008.

**Source Acceptance Criteria Mapping**

AC-020 maps administrator archival, retention, and discovery. AC-021 maps
restoration to the prior state. AC-026 maps the active-Proposed replacement
archive block.

**Dependencies**

STORY-002, STORY-005, STORY-007, STORY-009.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-013: Permanently Delete an Eligible Draft

**User Story**

As a Draft author, owner, or administrator, I want to permanently delete an
eligible Draft while retaining minimal audit evidence.

**Description**

Delete only current Drafts; remove their content, comments, and ordinary
history; retain record ID, actor, and timestamp permanently. Deny permanent
deletion of non-Draft records.

**Related Requirements**

CR-FR-022; CR-BR-008; CR-NFR-007–008.

**Source Acceptance Criteria Mapping**

AC-022 denies permanent deletion of non-Draft records. AC-027 maps authorized
Draft deletion and retained minimal audit evidence. AC-033–034 map audit
creation and permanent retention.

**Dependencies**

STORY-003, STORY-006, STORY-011, STORY-015.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-014: Protect Confidential Application Data

**User Story**

As a product stakeholder, I want confidential application data encrypted so
that it is protected in transit and at rest.

**Description**

Apply confidentiality controls to all in-scope application data while retaining
the team access boundary.

**Related Requirements**

CR-SCP-003; CR-NFR-001–002, CR-NFR-005.

**Source Acceptance Criteria Mapping**

AC-001 maps the team access boundary. AC-032 maps encryption in transit and at
rest.

**Dependencies**

STORY-001.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-015: Audit and Permanently Retain Governed Events

**User Story**

As a product stakeholder, I want governed actions audited and retained so that
important changes remain traceable.

**Description**

Record all approved audit event categories and retain audit entries and archived
records permanently.

**Related Requirements**

CR-FR-014, CR-FR-019–022; CR-NFR-007–008.

**Source Acceptance Criteria Mapping**

AC-013 maps immutable change history. AC-018 maps comment deletion audit.
AC-027 maps minimal Draft deletion audit. AC-033 enumerates audited events.
AC-034 maps permanent retention.

**Dependencies**

STORY-001, STORY-002, STORY-003.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-016: Meet Capacity and Operational Targets

**User Story**

As a product stakeholder, I want the MVP to meet its capacity, performance,
recovery, and browser targets so that it is usable under approved conditions.

**Description**

Validate operation for 25 users and 1,000 records; make primary content usable
within two seconds for the specified views; provide daily backup with approved
RPO/RTO; and support the approved Chrome and Edge versions. Availability and
accessibility remain best-effort scope constraints without formal targets.

**Related Requirements**

CR-SCP-002; CR-NFR-004, CR-NFR-006, CR-NFR-009–012.

**Source Acceptance Criteria Mapping**

AC-031 maps capacity and two-second usability. AC-035 maps daily backup, RPO 24
hours, and RTO 8 hours. AC-036 maps supported browser versions. No source
Acceptance Criterion is required for CR-NFR-010 or CR-NFR-012 because each is
explicitly an approved scope constraint rather than mandatory behavior.

**Dependencies**

STORY-003, STORY-009, STORY-014, STORY-015.

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

---

## 6. Engineering Tasks

### TASK-001: Integrate organizational authentication

Parent Story: STORY-001

Purpose: Authenticate users and enforce current designated-team membership on
application and record access.

Dependencies: None.

### TASK-002: Enforce role authorization

Parent Story: STORY-002

Purpose: Apply additive roles and administrator, approver, author, and owner
permissions consistently to governed actions.

Dependencies: TASK-001.

### TASK-003: Provide approver administration

Parent Story: STORY-002

Purpose: Allow administrators to designate approvers and audit designation
changes.

Dependencies: TASK-002.

### TASK-004: Provide Draft creation and required-content validation

Parent Story: STORY-003

Purpose: Capture all required record fields, author, owner, tags, Draft status,
and the information-handling notice.

Dependencies: TASK-001.

### TASK-005: Implement Draft editing and submission

Parent Story: STORY-004

Purpose: Enforce author editing and complete-record/approver validation before
Draft-to-Proposed transition.

Dependencies: TASK-003, TASK-004.

### TASK-006: Implement proposal decision transitions

Parent Story: STORY-005

Purpose: Enforce designated-approver acceptance/rejection, self-approval, and a
single valid outcome under concurrent actions.

Dependencies: TASK-002, TASK-005.

### TASK-007: Restart review after Proposed edits

Parent Story: STORY-005

Purpose: Atomically return edited Proposed records to Draft and invalidate prior
or in-progress review.

Dependencies: TASK-005, TASK-006.

### TASK-008: Implement ownership transfer

Parent Story: STORY-006

Purpose: Transfer ownership only for approved roles and statuses while
preserving author identity and auditability.

Dependencies: TASK-002, TASK-004.

### TASK-009: Handle author departure

Parent Story: STORY-006

Purpose: Retain records and enforce existing owner/administrator permissions
after author team membership ends.

Dependencies: TASK-001, TASK-008.

### TASK-010: Create controlled replacement versions

Parent Story: STORY-007

Purpose: Create one linked active Draft replacement for an Accepted record and
enforce its active interval.

Dependencies: TASK-003, TASK-006.

### TASK-011: Complete replacement acceptance

Parent Story: STORY-007

Purpose: Atomically accept the replacement, supersede the prior Accepted
version, and preserve valid links.

Dependencies: TASK-010.

### TASK-012: Persist immutable history and version navigation

Parent Story: STORY-008

Purpose: Retain immutable change evidence and expose navigation without cycles
or corrupted history.

Dependencies: TASK-004, TASK-011.

### TASK-013: Provide exact tag filtering

Parent Story: STORY-009

Purpose: Return all authorized records assigned the selected exact tag,
including historical and archived matches.

Dependencies: TASK-004.

### TASK-014: Provide tag administration

Parent Story: STORY-010

Purpose: Support team tag creation and atomic administrator rename, merge, and
association-only deletion.

Dependencies: TASK-002, TASK-004.

### TASK-015: Provide comments and single-level replies

Parent Story: STORY-011

Purpose: Add and view top-level comments and one reply level while denying
nested replies.

Dependencies: TASK-001, TASK-004.

### TASK-016: Soft-delete comments

Parent Story: STORY-011

Purpose: Enforce author-only soft deletion, `[deleted]` presentation, reply
preservation, and audit creation under concurrent activity.

Dependencies: TASK-015, TASK-021.

### TASK-017: Archive and restore records

Parent Story: STORY-012

Purpose: Enforce administrator-only archival, permanent retention, discovery,
and restoration to the pre-archive lifecycle status.

Dependencies: TASK-002, TASK-006, TASK-013.

### TASK-018: Enforce replacement archival guard

Parent Story: STORY-012

Purpose: Deny archival of an Accepted original while its active replacement is
Proposed.

Dependencies: TASK-010, TASK-017.

### TASK-019: Permanently delete eligible Drafts

Parent Story: STORY-013

Purpose: Delete approved Draft data atomically, deny other deletion, and retain
only the required permanent minimal audit event.

Dependencies: TASK-008, TASK-015, TASK-021.

### TASK-020: Apply data confidentiality controls

Parent Story: STORY-014

Purpose: Protect all application data in transit and at rest.

Dependencies: TASK-001.

### TASK-021: Record and retain audit events

Parent Story: STORY-015

Purpose: Create immutable audit evidence for every approved event category and
retain it permanently.

Dependencies: TASK-001, TASK-002, TASK-004.

### TASK-022: Validate capacity and response targets

Parent Story: STORY-016

Purpose: Verify the approved views become usable within two seconds under the
25-user and 1,000-record capacity.

Dependencies: TASK-013, TASK-020, TASK-021.

### TASK-023: Provide backup and recovery capability

Parent Story: STORY-016

Purpose: Perform daily backups and demonstrate RPO 24 hours and RTO 8 hours.

Dependencies: TASK-020, TASK-021.

### TASK-024: Validate supported browsers

Parent Story: STORY-016

Purpose: Verify all in-scope functions on current and previous major versions
of Chrome and Edge.

Dependencies: TASK-004–TASK-023.

---

## 7. Requirement Traceability Matrix

| Requirement | Story | Status |
|---|---|---|
| CR-BG-001–002, CR-OBJ-001–002 | STORY-003, STORY-005, STORY-008–013 | Covered |
| CR-USR-001–002 | STORY-001, STORY-011 | Covered |
| CR-USR-003 | STORY-003–005 | Covered |
| CR-USR-004–006 | STORY-002, STORY-012 | Covered |
| CR-USR-007–008 | STORY-003, STORY-006 | Covered |
| CR-USR-009–010 | STORY-002, STORY-007 | Covered |
| CR-SCP-001 | STORY-001–013 | Covered |
| CR-SCP-002 | STORY-016 | Covered |
| CR-SCP-003 | STORY-003, STORY-014 | Covered |
| CR-FR-001–002 | STORY-001 | Covered |
| CR-FR-003–005 | STORY-003, STORY-009 | Covered |
| CR-FR-006, CR-FR-023–024 | STORY-004–005 | Covered |
| CR-FR-006A, CR-FR-026 | STORY-006 | Covered |
| CR-FR-007–010 | STORY-004–005 | Covered |
| CR-FR-011–014 | STORY-007–008 | Covered |
| CR-FR-015–016, CR-FR-025 | STORY-009–010 | Covered |
| CR-FR-017–019 | STORY-011 | Covered |
| CR-FR-020–021 | STORY-012 | Covered |
| CR-FR-022 | STORY-013 | Covered |
| CR-NFR-001–002, CR-NFR-005 | STORY-001, STORY-014 | Covered |
| CR-NFR-003 | STORY-008 | Covered |
| CR-NFR-004, CR-NFR-006 | STORY-016 | Covered |
| CR-NFR-007–008 | STORY-013, STORY-015 | Covered |
| CR-NFR-009, CR-NFR-011 | STORY-016 | Covered |
| CR-NFR-010, CR-NFR-012 | STORY-016 | Covered |
| CR-BR-001–002, CR-BR-013, CR-BR-015 | STORY-002 | Covered |
| CR-BR-003–004, CR-BR-016 | STORY-004–005 | Covered |
| CR-BR-005–006, CR-BR-014 | STORY-007, STORY-012 | Covered |
| CR-BR-007 | STORY-012 | Covered |
| CR-BR-008 | STORY-013 | Covered |
| CR-BR-009 | STORY-008–009 | Covered |
| CR-BR-010 | STORY-003 | Covered |
| CR-BR-011 | STORY-006 | Covered |
| CR-BR-012 | STORY-011 | Covered |
| CR-BR-017 | STORY-010 | Covered |
| CR-US-001–014 | STORY-003–012 | Covered |
| CR-OOS-001–013 | All stories (scope guardrails) | Covered |

### Source Acceptance Criteria Coverage

| Acceptance Criteria | Story |
|---|---|
| AC-001 | STORY-001, STORY-014 |
| AC-002 | STORY-003 |
| AC-003 | STORY-002 |
| AC-004–005 | STORY-003–004 |
| AC-006–008 | STORY-005 |
| AC-009–011, AC-025, AC-039 | STORY-007 |
| AC-012–013 | STORY-008 |
| AC-014, AC-030 | STORY-006 |
| AC-015 | STORY-009 |
| AC-016–019, AC-028 | STORY-011 |
| AC-020–021, AC-026 | STORY-012 |
| AC-022, AC-027 | STORY-013 |
| AC-023 | STORY-002 |
| AC-024 | STORY-004 |
| AC-029, AC-040–042 | STORY-010 |
| AC-031, AC-035–036 | STORY-016 |
| AC-032 | STORY-014 |
| AC-033–034 | STORY-013, STORY-015 |
| AC-037 | STORY-003 |
| AC-038 | STORY-005, STORY-008 |

Every source Acceptance Criterion is mapped to at least one Story.

---

## 8. Story Dependency Map

- STORY-001 enables every authenticated product capability.
- STORY-002 depends on STORY-001 and enables governed lifecycle, versioning,
  archival, and tag administration.
- STORY-003 depends on STORY-001 and establishes the record used by all
  remaining functional Stories.
- STORY-004 depends on STORY-002 and STORY-003; STORY-005 depends on STORY-004.
- STORY-006 depends on role enforcement and record creation.
- STORY-007 depends on role administration and lifecycle decisions; STORY-008
  depends on created records and replacement versioning.
- STORY-009 and STORY-010 depend on tagged record creation; tag administration
  also depends on administrator authorization.
- STORY-011 depends on access control and record creation.
- STORY-012 depends on authorization, lifecycle, versioning, and discovery.
- STORY-013 depends on record ownership, comments, and audit retention.
- STORY-014 depends on access control. STORY-015 spans governed events and must
  be available before comment and Draft deletion are completed.
- STORY-016 is validated after the relevant functional, security, and audit
  capabilities exist.

Parallel development is practical after STORY-001–003: ownership, discovery,
comments, audit, and confidentiality can progress independently, while
versioning and archival remain lifecycle-dependent.

---

## 9. Recommended Implementation Order

1. STORY-001
2. STORY-002
3. STORY-003
4. STORY-015
5. STORY-004
6. STORY-005
7. STORY-006
8. STORY-014
9. STORY-009
10. STORY-010
11. STORY-011
12. STORY-007
13. STORY-008
14. STORY-012
15. STORY-013
16. STORY-016

This order establishes access, authorization, core records, and audit first.
Lifecycle then enables versioning and archival. Operational targets are
validated against the integrated MVP.

---

## 10. Planning Risks

- Concurrent proposal decisions or edits could violate the single-outcome
  lifecycle unless transitions are atomic.
- Replacement acceptance spans multiple records and could corrupt version
  links or Superseded state if partially completed.
- Immediate loss of team access depends on reliable membership and session
  invalidation behavior.
- Tag merge, rename, and deletion affect many references and require atomic
  record-preserving updates.
- Draft deletion must remove ordinary data while reliably preserving the
  minimal permanent audit event.
- Permanent retention and immutable history require controls against both
  application-level and operational modification or deletion.
- Soft comment deletion must remain consistent with concurrent replies.
- The two-second target includes user-visible usability rather than only server
  response time, so validation must cover the complete interaction boundary.
- Recovery objectives require repeatable restoration evidence, not backup
  creation alone.

---

## 11. Open Planning Questions

No open product or planning questions remain. Detailed test design, concurrency
control, transaction handling, session invalidation, and data-integrity
enforcement are assigned to engineering tasks without changing product
requirements.
