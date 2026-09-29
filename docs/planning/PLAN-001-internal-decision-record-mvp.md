# Development Plan

**Plan ID:** PLAN-001
**Version:** 1.2
**Status:** APPROVED
**Approval date:** 2026-09-29

## 1. Source Requirement

Requirement document: `docs/requirements/requirement-definition.md`

Requirement version: 1.3

Requirement status: Approved

Planning date: 2026-09-29

---

## 2. Planning Summary

This plan delivers the Internal Decision Record Application demonstration MVP
for one modeled internal team. The work is organized around Mock identity
selection, role-dependent behavior, decision authoring and lifecycle,
replacement versioning, immutable history, discovery, top-level comments,
archival, auditability, and operational compatibility.

Mock identity selection and core record creation are foundational. Role
administration and lifecycle behavior precede replacement versioning and
archival. Immutable audit behavior is cross-cutting and must be available before
governed actions are completed.

Version 1.3 removes organizational SSO, a real access-security boundary, record
deletion, backup and recovery, encryption at rest, tag administration, comment
replies, and a formal response-time target from MVP scope. It adds a permanent,
retained, replacement-specific Abandoned condition for replacement-version
Drafts. The MVP uses only demo or synthetic data.

No product-level planning blocker remains. Principal engineering risks are
atomic lifecycle outcomes, immutable history, replacement abandonment,
consistent Mock-identity attribution, permanent audit retention, and preserving
record links and archival state.

---

## 3. Planning Readiness

### Blocking Gaps

No blocking requirement gaps identified.

### Non-blocking Gaps

No non-blocking requirement gaps identified. Responsiveness, availability, and
accessibility are approved best-effort scope constraints without mandatory
measurable targets.

### Joint Plan and Test Design Readiness

TEST-001 Version 2.0 predates typed dependency and deferred-execution fields.
Its cross-Story cases do not distinguish the Story whose requirement is covered
from the later Story that owns execution. The Test Design Agent must migrate
TEST-001 and obtain Human approval before this Plan and Test Design are jointly
implementation-ready. TC-002-02–04, TC-003-02, TC-004-05, TC-005-03,
TC-006-02, TC-009-01, TC-013-01–02, and TC-015-01–03 require capabilities
delivered by later Stories. This Plan treats those relationships as
non-blocking integration validation rather than as earlier-Story completion
gates.

---

## 4. Epics

### EPIC-001: Mock Identity and Role Administration

Objective: Let a person select a clearly identified Mock identity and apply its
additive roles and attribution consistently without implying real
authentication or access protection.

Related Requirements: CR-BG-003; CR-USR-001, CR-USR-004–006,
CR-USR-009–011; CR-FR-009–010, CR-FR-027–028; CR-NFR-013; CR-BR-001–002,
CR-BR-013, CR-BR-015, CR-BR-018.

Stories: STORY-001, STORY-002

### EPIC-002: Decision Record Authoring and Lifecycle

Objective: Create complete decision records and move non-abandoned records
safely through the approved review lifecycle.

Related Requirements: CR-USR-003; CR-FR-003–010, CR-FR-023–024;
CR-BR-003–004, CR-BR-010, CR-BR-016.

Stories: STORY-003, STORY-004, STORY-005

### EPIC-003: Ownership, Versioning, and History

Objective: Preserve authorship and immutable history while supporting ownership
transfer, controlled replacement of Accepted decisions, and retained
abandonment of replacement Drafts.

Related Requirements: CR-USR-007–009; CR-FR-006A, CR-FR-011–014,
CR-FR-026, CR-FR-030; CR-NFR-003; CR-BR-005–006, CR-BR-011,
CR-BR-013–014, CR-BR-019.

Stories: STORY-006, STORY-007, STORY-008

### EPIC-004: Discovery and Basic Tags

Objective: Create and associate tags and discover retained records through one
exact tag filter.

Related Requirements: CR-FR-005, CR-FR-015–016, CR-FR-025; CR-BR-009.

Stories: STORY-009, STORY-010

### EPIC-005: Decision Discussion

Objective: Support top-level comments and auditable author-only soft deletion
without replies.

Related Requirements: CR-USR-002; CR-FR-017, CR-FR-019; CR-BR-012.

Stories: STORY-011

### EPIC-006: Archival, Restoration, and Record Retention

Objective: Archive and restore retained records while ensuring decision-record
deletion is unavailable in every lifecycle, replacement-specific, and archival
condition.

Related Requirements: CR-USR-006; CR-FR-020–021, CR-FR-029; CR-NFR-008;
CR-BR-007, CR-BR-014.

Stories: STORY-012, STORY-013

### EPIC-007: Demo Data, Audit, and Operational Quality

Objective: Enforce the demo-data boundary, provide HTTPS in deployed
environments, retain governed audit evidence, and meet approved capacity and
browser requirements.

Related Requirements: CR-SCP-002–003; CR-FR-014, CR-FR-019–021,
CR-FR-023, CR-FR-030; CR-NFR-004–008, CR-NFR-010–013; CR-BR-010.

Stories: STORY-014, STORY-015, STORY-016

---

## 5. User Stories

### STORY-001: Select a Mock Identity

**User Story**

As an MVP user, I want to choose a preconfigured Mock identity so that I can
demonstrate behavior associated with that identity's roles.

**Description**

Provide a login or entry screen listing preconfigured identities as Mock users.
Use the selected identity for roles and attribution while clearly communicating
that selection does not authenticate the person, verify team membership, or
protect data from unauthorized access.

**Related Requirements**

CR-BG-003; CR-USR-001, CR-USR-011; CR-FR-027–028; CR-NFR-013; CR-BR-018;
CR-US-015.

**Source Acceptance Criteria Mapping**

AC-043 maps Mock identity selection, configured roles, and subsequent
attribution. AC-044 maps the explicit absence of organizational SSO, identity
verification, team-membership verification, and a real security boundary.
AC-037 maps the demo-data notice on the login or entry screen.

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

As an administrator Mock identity, I want to designate approvers and apply
additive roles so that governed decision behavior can be demonstrated.

**Description**

Enforce administrator-only approver administration and replacement governance,
allow a Mock identity to hold additive roles, and permit a designated approver
to decide a record they authored.

**Related Requirements**

CR-USR-004–006, CR-USR-009–010; CR-FR-009–010; CR-BR-001–002,
CR-BR-013, CR-BR-015.

**Source Acceptance Criteria Mapping**

AC-003 maps administrator-only governed actions, including replacement creation
and abandonment. AC-006 maps denial for non-approvers. AC-007 maps
self-approval. AC-023 maps additive permissions.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-001 | Start | Selected Mock identity and role context are available. | Merged implementation and passing focused validation for Mock identity selection and role propagation. |
| STORY-005, STORY-007, STORY-012 | Integration-validation | Proposal decisions, replacement governance, archive, and restore are available for the complete administrator-only action matrix. | Passing deferred role-authorization regression for the later governed actions. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-003: Create a Complete Draft

**User Story**

As a team-member Mock identity, I want to create a structured Draft so that the
decision and its rationale can be reviewed and understood later.

**Description**

Create a Draft with all required content, distinct author and owner, one or more
tags, attribution to the selected Mock identity, and the mandatory
demo-or-synthetic-data notice.

**Related Requirements**

CR-BG-001–002; CR-OBJ-001–002; CR-USR-002–003, CR-USR-007; CR-SCP-003;
CR-FR-003–005, CR-FR-006A, CR-FR-023; CR-BR-010; CR-US-001.

**Source Acceptance Criteria Mapping**

AC-002 maps Draft creation and Mock-author attribution. AC-004 maps required
field validation at submission. AC-037 maps the prohibited-data notice.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-001 | Start | Mock author attribution is available for record creation. | Merged implementation and passing focused validation for selected-identity attribution. |
| STORY-004 | Integration-validation | Draft submission is available for missing-required-field regression. | Passing deferred required-field regression through the submission workflow. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-004: Edit and Submit a Draft

**User Story**

As an author Mock identity, I want to edit and submit a complete,
non-abandoned Draft so that an approver can review it.

**Description**

Allow the attributed author to edit eligible Draft content and transition it to
Proposed only when all required fields and at least one designated approver are
present. Abandoned replacement Drafts cannot be edited or submitted.

**Related Requirements**

CR-USR-003; CR-FR-006–008, CR-FR-024, CR-FR-030; CR-BR-003,
CR-BR-016, CR-BR-019; CR-US-002.

**Source Acceptance Criteria Mapping**

AC-004 maps incomplete Draft submission prevention. AC-005 maps valid
Draft-to-Proposed submission. AC-024 maps the approver requirement. AC-047 maps
the prohibition on editing or submitting an Abandoned replacement Draft.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-002 | Start | Administrator approver designation is available. | Merged implementation and passing focused validation for approver administration. |
| STORY-003 | Start | A complete editable Draft can be created and retained. | Merged implementation and passing focused validation for Draft creation. |
| STORY-007 | Integration-validation | An Abandoned replacement Draft is available for edit and submission denial regression. | Passing deferred abandoned-Draft regression. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-005: Review and Decide a Proposal

**User Story**

As a designated approver Mock identity, I want to accept or reject a Proposed
decision so that the modeled team has a clear outcome.

**Description**

Permit only designated approvers to decide a proposal. If the author edits a
Proposed record, return it to Draft, invalidate review, and require
resubmission. Rejected records are immutable.

**Related Requirements**

CR-FR-006–010, CR-FR-014; CR-BR-002–004; CR-US-003, CR-US-010.

**Source Acceptance Criteria Mapping**

AC-006–007 map approval authorization and self-approval. AC-008 maps automatic
return to Draft and review invalidation after editing. AC-038 maps immutability
of Rejected and Superseded records.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-004 | Start | An eligible Draft can be submitted to Proposed. | Merged implementation and passing focused validation for guarded Draft submission. |
| STORY-007 | Integration-validation | A Superseded record is available for terminal-state immutability regression. | Passing deferred Superseded-record regression. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-006: Transfer Record Ownership

**User Story**

As an author, owner, or administrator Mock identity, I want to transfer an
eligible Draft or Proposed record without changing authorship so that modeled
responsibility can change safely.

**Description**

Allow only approved roles and eligible record conditions to transfer ownership.
Retain records when an author leaves without granting additional permissions.
Abandoned replacement Drafts cannot be transferred.

**Related Requirements**

CR-USR-007–008; CR-FR-006A, CR-FR-026, CR-FR-030; CR-BR-011,
CR-BR-019; CR-US-011, CR-US-013.

**Source Acceptance Criteria Mapping**

AC-014 maps the transfer actor and record-condition matrix while preserving
authorship. AC-030 maps retained records after author departure. AC-047 maps
immutability of ownership on Abandoned replacement Drafts.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-002 | Start | Additive actor-role evaluation is available. | Merged implementation and passing focused validation for governed role behavior. |
| STORY-003 | Start | Records retain distinct author and owner attributes. | Merged implementation and passing focused validation for Draft author and owner persistence. |
| STORY-007 | Integration-validation | An Abandoned replacement Draft is available for ownership-transfer denial regression. | Passing deferred abandoned-Draft ownership regression. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-007: Govern Replacement Versions

**User Story**

As an administrator Mock identity, I want to create, complete, or abandon one
replacement version of an Accepted record so that the decision can evolve
without altering retained history.

**Description**

Create one linked active replacement Draft when none exists. End its active
interval when it is Accepted, Rejected, or its Draft is marked Abandoned.
Acceptance atomically supersedes the previous Accepted version. Abandonment
retains the Draft and link, leaves the original Accepted, permits a new
replacement, and makes the abandoned replacement permanently immutable and
non-reactivatable.

**Related Requirements**

CR-USR-009; CR-FR-011–013, CR-FR-030; CR-BR-005–006, CR-BR-013–014,
CR-BR-019; CR-US-006, CR-US-016.

**Source Acceptance Criteria Mapping**

AC-009 maps direct-edit prevention for Accepted records. AC-010 maps controlled
replacement creation. AC-011 maps atomic supersession. AC-025 maps the
single-active-replacement rule. AC-039 maps all active-interval endpoints.
AC-046 maps valid abandonment and retained navigation. AC-047 maps
post-abandonment immutability, non-reactivation, and invalid abandonment
targets.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-002 | Start | Administrator and approver role capabilities are available. | PR #7 implementation evidence and passing focused role/approver validation, including TASK-003 evidence. |
| STORY-005 | Start | Accepted and Rejected lifecycle outcomes are available. | Merged implementation and passing focused validation for proposal decisions. |
| STORY-015 | Start | Reusable immutable audit-event recording is available; STORY-015 need not be Done. | PR #12 audit-foundation evidence and passing focused TASK-021 validation. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-008: View Immutable Change and Version History

**User Story**

As a reader using a Mock identity, I want to inspect change history and navigate
accepted, superseded, and abandoned replacement links so that I can understand
how a decision evolved.

**Description**

Expose immutable attributed change history and navigation between originals and
accepted or abandoned replacement versions without corrupting links or
reactivating abandoned records.

**Related Requirements**

CR-OBJ-002; CR-FR-013–014, CR-FR-030; CR-NFR-003; CR-BR-004–006,
CR-BR-009, CR-BR-019; CR-US-007.

**Source Acceptance Criteria Mapping**

AC-012 maps navigation between Superseded and accepted replacements. AC-013
maps immutable attributed history. AC-038 maps Rejected and Superseded
immutability. AC-046 maps navigation to retained abandoned replacements.
AC-047 maps abandoned-record immutability.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-003 | Start | Attributed record changes can be retained. | Merged implementation and passing focused validation for record persistence. |
| STORY-007 | Start | Replacement links and accepted, superseded, and abandoned outcomes are available. | Merged implementation and passing focused validation for replacement governance. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-009: Discover Records by Exact Tag

**User Story**

As a team-member Mock identity, I want to filter by one exact tag so that I can
find relevant current and retained historical records.

**Description**

Return matching records, including Rejected, Superseded, and archived records.
The MVP has no real authorization boundary and uses only demo or synthetic
data.

**Related Requirements**

CR-FR-005, CR-FR-015–016; CR-BR-009; CR-US-004.

**Source Acceptance Criteria Mapping**

AC-015 maps exact single-tag filtering, including matching Rejected,
Superseded, and archived records.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-003 | Start | Tagged records can be retained and retrieved. | Merged implementation and passing focused validation for record tag persistence. |
| STORY-005 | Integration-validation | Rejected and Superseded fixtures are available for exact-filter regression. | Passing deferred exact-tag regression against terminal lifecycle records. |
| STORY-012 | Integration-validation | Archived fixtures are available for exact-filter regression. | Passing deferred exact-tag regression against archived records. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-010: Create and Associate Tags

**User Story**

As a team-member Mock identity, I want to create tags and associate one or more
with records so that records remain discoverable.

**Description**

Allow team members to create tags and make them available for record
association. Tag rename, merge, and deletion are outside MVP scope.

**Related Requirements**

CR-FR-005, CR-FR-025; CR-US-014.

**Source Acceptance Criteria Mapping**

AC-029 maps team-member tag creation and association of one or more selected
tags with a record.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-001 | Start | A selected team-member Mock identity is available. | Merged implementation and passing focused validation for identity selection. |
| STORY-003 | Start | Records support tag association. | Merged implementation and passing focused validation for record tag persistence. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-011: Discuss a Decision

**User Story**

As a team-member Mock identity, I want to add a top-level comment and
soft-delete my own comment so that I can contribute to discussion while
retaining attribution.

**Description**

Support top-level comments and author-only soft deletion with a `[deleted]`
placeholder and audit evidence. Comment replies and editing are outside MVP
scope.

**Related Requirements**

CR-USR-002; CR-FR-017, CR-FR-019; CR-BR-012; CR-US-005, CR-US-012.

**Source Acceptance Criteria Mapping**

AC-016 maps top-level comment creation and Mock-identity attribution. AC-018
maps author soft deletion, the `[deleted]` placeholder, and audit evidence.
AC-019 denies deletion by another user.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-001 | Start | Mock actor attribution is available. | Merged implementation and passing focused validation for selected-identity attribution. |
| STORY-003 | Start | A retained decision record is available for comments. | Merged implementation and passing focused validation for record creation. |
| STORY-015 | Start | Reusable immutable audit-event recording is available; STORY-015 need not be Done. | Merged audit-foundation implementation and passing focused audit-event validation. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-012: Archive and Restore Records

**User Story**

As an administrator Mock identity, I want to archive a record and restore its
prior lifecycle and replacement-specific condition so that it can leave active
use without being lost or reactivated incorrectly.

**Description**

Archive eligible records, retain and discover them permanently, and restore the
pre-archive lifecycle status. Preserve Abandoned on restored replacement Drafts
and block archival of an Accepted original while its active replacement is
Proposed.

**Related Requirements**

CR-USR-006; CR-FR-020–021, CR-FR-030; CR-BR-007, CR-BR-014,
CR-BR-019; CR-NFR-008; CR-US-009.

**Source Acceptance Criteria Mapping**

AC-020 maps administrator archival, retention, and discovery. AC-021 maps
restoration to the prior lifecycle status. AC-026 maps the active-Proposed
replacement archive block. AC-047 maps preservation of the Abandoned condition
during archive and restore.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-002 | Start | Administrator role enforcement is available. | Merged implementation and passing focused validation for administrator-only actions. |
| STORY-005 | Start | Lifecycle outcomes to archive and restore are available. | Merged implementation and passing focused validation for proposal decisions. |
| STORY-007 | Start | Active, accepted, rejected, and abandoned replacement conditions are available. | Merged implementation and passing focused validation for replacement governance. |
| STORY-009 | Start | Exact-tag discovery can include archived records. | Merged implementation and passing focused validation for exact-tag discovery. |
| STORY-015 | Start | Reusable archive/restore audit recording is available; STORY-015 need not be Done. | Merged audit-foundation implementation and passing focused audit-event validation. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-013: Prevent Decision-Record Deletion

**User Story**

As a product stakeholder, I want decision-record deletion unavailable so that
every record remains retained and archival remains the only way to remove it
from active use.

**Description**

Do not expose or permit permanent or soft decision-record deletion in any
lifecycle, replacement-specific, or archival condition, including Abandoned.
This does not prevent author-only soft deletion of comment content.

**Related Requirements**

CR-SCP-001; CR-FR-029; CR-OOS-007.

**Source Acceptance Criteria Mapping**

AC-045 maps the absence or denial of decision-record deletion and preservation
of otherwise-permitted archival and restoration.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-003 | Start | Retained decision records exist without a delete capability. | Merged implementation and passing focused validation for record creation and retention. |
| STORY-007 | Integration-validation | Active and Abandoned replacement fixtures are available for deletion-denial regression. | Passing deferred record-deletion regression for replacement conditions. |
| STORY-012 | Integration-validation | Archived records and archive/restore actions are available for deletion-denial regression. | Passing deferred record-deletion regression for archived conditions. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-014: Enforce Demo Data and Deployed HTTPS Boundaries

**User Story**

As a product stakeholder, I want the MVP clearly limited to demo or synthetic
data and deployed traffic protected by HTTPS so that the demonstration remains
within its approved operating boundary.

**Description**

Display the required data-use notice at identity selection, creation, and edit
surfaces. Prohibit real internal confidential, regulated personal, and health
information. Use HTTPS for client-facing traffic in deployed environments;
local development is exempt.

**Related Requirements**

CR-SCP-003; CR-FR-023; CR-NFR-005; CR-BR-010; CR-OOS-006.

**Source Acceptance Criteria Mapping**

AC-037 maps the visible demo-data notice. AC-032 maps HTTPS in deployed
environments and the local-development exemption.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-001 | Start | The identity-entry surface is available for the data-use notice. | Merged implementation and passing focused validation for the entry surface. |
| STORY-003 | Start | Record creation and editing surfaces are available for the data-use notice. | Merged implementation and passing focused validation for record-entry surfaces. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-015: Audit and Permanently Retain Governed Events

**User Story**

As a product stakeholder, I want governed actions audited and retained so that
important changes remain traceable to Mock identities.

**Description**

Create audit evidence for role and approver changes, lifecycle transitions,
replacement-Draft abandonment, archive and restore, ownership transfer, and
comment deletion. Permanently retain audit entries and archived records.

**Related Requirements**

CR-FR-014, CR-FR-019–021, CR-FR-030; CR-NFR-007–008.

**Source Acceptance Criteria Mapping**

AC-013 maps immutable attributed history. AC-018 maps comment-deletion audit.
AC-033 maps all approved audit event categories and required abandonment and
comment-deletion attribution. AC-034 maps permanent retention. AC-046 maps the
abandonment audit event.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-001 | Start | Mock actor attribution is available. | Merged implementation and passing focused validation for selected-identity attribution. |
| STORY-002 | Start | Role and approver changes can emit governed events. | Merged implementation and passing focused validation for role and approver administration. |
| STORY-003 | Start | Retained records and change events are available. | Merged implementation and passing focused validation for record persistence. |
| STORY-005, STORY-006, STORY-007, STORY-011, STORY-012 | Integration-validation | All later governed event categories are available for end-to-end audit coverage. | Passing deferred audit regression for lifecycle, ownership, abandonment, comment deletion, archive, and restore events. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

### STORY-016: Meet Capacity and Compatibility Requirements

**User Story**

As a product stakeholder, I want the MVP to remain functional at approved
capacity and in supported browsers so that its workflows can be demonstrated
under approved conditions.

**Description**

Validate all in-scope behavior with 25 preconfigured Mock users and 1,000
decision records, without a response-time assertion. Support the current and
immediately prior major versions of Chrome and Edge. Responsiveness,
availability, and accessibility remain best-effort scope constraints.

**Related Requirements**

CR-SCP-002; CR-NFR-004, CR-NFR-006, CR-NFR-010–012.

**Source Acceptance Criteria Mapping**

AC-031 maps functional behavior at approved capacity without a response-time
assertion. AC-036 maps supported browser versions. No source Acceptance
Criterion is required for CR-NFR-006, CR-NFR-010, or CR-NFR-012 because each is
explicitly an approved scope constraint rather than mandatory measurable
behavior.

**Dependencies**

| Story | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- |
| STORY-001–STORY-015 | Integration-validation | The complete in-scope MVP is integrated for capacity and browser validation. | Passing full acceptance suite at approved capacity and on each required browser/version combination. |

**Priority**

Must

**Definition of Done**

All mapped source Acceptance Criteria are satisfied; required automated tests
are implemented; existing tests pass; documentation is updated when required;
the Pull Request is reviewed.

---

## 6. Engineering Tasks

The canonical typed dependencies, required outcomes, and satisfaction evidence
for every Task are defined in Section 8.1. Each Task below incorporates its
corresponding Section 8.1 entry.

### TASK-001: Provide Mock identity selection

Parent Story: STORY-001

Purpose: Present preconfigured identities as Mock users, establish the selected
identity for roles and attribution, and communicate the absence of real
authentication or access protection.

Dependencies: None.

### TASK-002: Enforce role-dependent behavior

Parent Story: STORY-002

Purpose: Apply additive administrator, approver, author, and owner permissions
consistently to governed actions under the selected Mock identity.

Dependencies: See TASK-002 in Section 8.1.

### TASK-003: Provide approver administration

Parent Story: STORY-002

Purpose: Allow administrator Mock identities to designate approvers.

Dependencies: See TASK-003 in Section 8.1.

### TASK-004: Provide Draft creation and required-content validation

Parent Story: STORY-003

Purpose: Capture all required fields, Mock author, owner, tags, Draft status,
and the demo-or-synthetic-data notice.

Dependencies: See TASK-004 in Section 8.1.

### TASK-005: Implement Draft editing and submission

Parent Story: STORY-004

Purpose: Enforce author editing and complete-record and approver validation
before a non-abandoned Draft transitions to Proposed.

Dependencies: See TASK-005 in Section 8.1.

### TASK-006: Implement proposal decision transitions

Parent Story: STORY-005

Purpose: Enforce designated-approver acceptance or rejection, self-approval,
and one valid outcome under concurrent actions.

Dependencies: See TASK-006 in Section 8.1.

### TASK-007: Restart review after Proposed edits

Parent Story: STORY-005

Purpose: Atomically return edited Proposed records to Draft and invalidate
prior or in-progress review.

Dependencies: See TASK-007 in Section 8.1.

### TASK-008: Implement ownership transfer

Parent Story: STORY-006

Purpose: Transfer ownership only for approved actors and eligible record
conditions while preserving author identity and auditability.

Dependencies: See TASK-008 in Section 8.1.

### TASK-009: Handle modeled author departure

Parent Story: STORY-006

Purpose: Retain records and enforce otherwise-granted owner and administrator
behavior after a preconfigured Mock author is represented as having left.

Dependencies: See TASK-009 in Section 8.1.

### TASK-010: Create controlled replacement versions

Parent Story: STORY-007

Purpose: Create one linked active Draft replacement for an Accepted record and
enforce its active interval.

Dependencies: See TASK-010 in Section 8.1.

### TASK-011: Complete replacement acceptance

Parent Story: STORY-007

Purpose: Atomically accept a replacement, supersede the prior Accepted version,
and preserve valid links.

Dependencies: See TASK-011 in Section 8.1.

### TASK-012: Persist immutable history and version navigation

Parent Story: STORY-008

Purpose: Retain immutable attributed change evidence and expose navigation
across accepted, superseded, and abandoned replacement links without cycles or
corruption.

Dependencies: See TASK-012 in Section 8.1.

### TASK-013: Provide exact tag filtering

Parent Story: STORY-009

Purpose: Return records assigned the selected exact tag, including matching
Rejected, Superseded, and archived records.

Dependencies: See TASK-013 in Section 8.1.

### TASK-014: Provide basic tag creation and association

Parent Story: STORY-010

Purpose: Let team-member Mock identities create tags and associate one or more
tags with decision records.

Dependencies: See TASK-014 in Section 8.1.

### TASK-015: Provide top-level comments

Parent Story: STORY-011

Purpose: Add and view attributed top-level comments without reply behavior.

Dependencies: See TASK-015 in Section 8.1.

### TASK-016: Soft-delete comments

Parent Story: STORY-011

Purpose: Enforce author-only soft deletion, `[deleted]` presentation, and audit
creation under concurrent deletion attempts.

Dependencies: See TASK-016 in Section 8.1.

### TASK-017: Archive and restore records

Parent Story: STORY-012

Purpose: Enforce administrator-only archival, permanent retention, discovery,
and restoration of lifecycle and replacement-specific conditions.

Dependencies: See TASK-017 in Section 8.1.

### TASK-018: Enforce replacement archival guard

Parent Story: STORY-012

Purpose: Deny archival of an Accepted original while its active replacement is
Proposed and preserve Abandoned through archive and restore.

Dependencies: See TASK-018 in Section 8.1.

### TASK-019: Prevent decision-record deletion

Parent Story: STORY-013

Purpose: Ensure no permanent or soft decision-record deletion action is exposed
or accepted in any lifecycle, replacement-specific, or archival condition.

Dependencies: See TASK-019 in Section 8.1.

### TASK-020: Apply demo-data and HTTPS controls

Parent Story: STORY-014

Purpose: Present the approved data-use notices and require HTTPS for
client-facing traffic in deployed environments while exempting local
development.

Dependencies: See TASK-020 in Section 8.1.

### TASK-021: Record and retain audit events

Parent Story: STORY-015

Purpose: Create immutable audit evidence for every approved event category and
retain audit entries and archived records permanently.

Dependencies: See TASK-021 in Section 8.1.

### TASK-022: Validate approved functional capacity

Parent Story: STORY-016

Purpose: Verify all in-scope functions continue to satisfy their mapped
Acceptance Criteria with 25 preconfigured Mock users and 1,000 records, without
a response-time assertion.

Dependencies: See TASK-022 in Section 8.1.

### TASK-024: Validate supported browsers

Parent Story: STORY-016

Purpose: Verify all in-scope functions on the current and immediately prior
major versions of Chrome and Edge.

Dependencies: See TASK-024 in Section 8.1.

### TASK-025: Abandon a replacement-version Draft

Parent Story: STORY-007

Purpose: Let an administrator permanently mark only an active replacement Draft
as Abandoned, retain and audit it and its link, end its active interval, deny
reactivation or mutation, and permit a new replacement.

Dependencies: See TASK-025 in Section 8.1.

Retired from the Version 1.3 active plan: TASK-023 (backup and recovery).
TASK-019, TASK-020, and TASK-022 retain their identifiers but have been
redefined to match the approved Version 1.3 requirements.

---

## 7. Requirement Traceability Matrix

| Requirement | Story | Status |
|---|---|---|
| CR-BG-001–003, CR-OBJ-001–002 | STORY-001, STORY-003, STORY-005, STORY-007–STORY-015 | Covered |
| CR-USR-001–002 | STORY-001, STORY-003, STORY-011 | Covered |
| CR-USR-003 | STORY-003–STORY-005 | Covered |
| CR-USR-004–006 | STORY-002, STORY-012 | Covered |
| CR-USR-007–008 | STORY-003, STORY-006 | Covered |
| CR-USR-009–010 | STORY-002, STORY-007 | Covered |
| CR-USR-011 | STORY-001 | Covered |
| CR-SCP-001 | STORY-001–STORY-013 | Covered |
| CR-SCP-002 | STORY-016 | Covered |
| CR-SCP-003 | STORY-003, STORY-014 | Covered |
| CR-FR-003–005 | STORY-003, STORY-009–STORY-010 | Covered |
| CR-FR-006, CR-FR-023–024 | STORY-003–STORY-005, STORY-014 | Covered |
| CR-FR-006A, CR-FR-026 | STORY-006 | Covered |
| CR-FR-007–010 | STORY-004–STORY-005 | Covered |
| CR-FR-011–014, CR-FR-030 | STORY-007–STORY-008 | Covered |
| CR-FR-015–017, CR-FR-019, CR-FR-025 | STORY-009–STORY-011 | Covered |
| CR-FR-020–021 | STORY-012 | Covered |
| CR-FR-027–028 | STORY-001 | Covered |
| CR-FR-029 | STORY-013 | Covered |
| CR-NFR-003 | STORY-007–STORY-008 | Covered |
| CR-NFR-004 | STORY-016 | Covered |
| CR-NFR-005 | STORY-014 | Covered |
| CR-NFR-006, CR-NFR-010, CR-NFR-012 | STORY-016 | Covered as scope constraints |
| CR-NFR-007–008 | STORY-007, STORY-011–STORY-012, STORY-015 | Covered |
| CR-NFR-011 | STORY-016 | Covered |
| CR-NFR-013 | STORY-001 | Covered |
| CR-BR-001–002, CR-BR-013, CR-BR-015 | STORY-002 | Covered |
| CR-BR-003–004, CR-BR-016 | STORY-004–STORY-005 | Covered |
| CR-BR-005–006, CR-BR-014, CR-BR-019 | STORY-007–STORY-008, STORY-012 | Covered |
| CR-BR-007 | STORY-012 | Covered |
| CR-BR-009 | STORY-008–STORY-009 | Covered |
| CR-BR-010 | STORY-003, STORY-014 | Covered |
| CR-BR-011 | STORY-006 | Covered |
| CR-BR-012 | STORY-011 | Covered |
| CR-BR-018 | STORY-001 | Covered |
| CR-US-001–016 | STORY-001–STORY-012 | Covered |
| CR-OOS-001–014 and Version 1.3 exclusions | All stories | Covered as scope guardrails |

### Source Acceptance Criteria Coverage

| Acceptance Criteria | Story |
|---|---|
| AC-002 | STORY-003 |
| AC-003 | STORY-002 |
| AC-004–005 | STORY-003–STORY-004 |
| AC-006–008 | STORY-005 |
| AC-009–011, AC-025, AC-039, AC-046–047 | STORY-007 |
| AC-012–013 | STORY-008 |
| AC-014, AC-030 | STORY-006 |
| AC-015 | STORY-009 |
| AC-016, AC-018–019 | STORY-011 |
| AC-020–021, AC-026 | STORY-012 |
| AC-023 | STORY-002 |
| AC-024 | STORY-004 |
| AC-029 | STORY-010 |
| AC-031, AC-036 | STORY-016 |
| AC-032 | STORY-014 |
| AC-033–034 | STORY-015 |
| AC-037 | STORY-001, STORY-003, STORY-014 |
| AC-038 | STORY-005, STORY-008 |
| AC-043–044 | STORY-001 |
| AC-045 | STORY-013 |

Every active source Acceptance Criterion in Requirement Version 1.3 is mapped
to at least one Story. Retired criteria from prior versions are not mapped as
active work.

---

## 8. Story Dependency Map

| Story | Depends on | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- | --- |
| STORY-002 | STORY-001 | Start | Selected Mock identity and role context. | Passing focused identity and role-propagation validation. |
| STORY-002 | STORY-005; STORY-007; STORY-012 | Integration-validation | Later governed actions for the complete administrator-only action matrix. | Passing deferred role-authorization regression. |
| STORY-003 | STORY-001 | Start | Mock actor attribution. | Passing focused selected-identity attribution validation. |
| STORY-003 | STORY-004 | Integration-validation | Draft submission for missing-required-field regression. | Passing deferred required-field regression. |
| STORY-004 | STORY-002; STORY-003 | Start | Approver designation and complete editable Draft. | Passing focused validation for both named capabilities. |
| STORY-004 | STORY-007 | Integration-validation | Abandoned Draft for edit/submission denial regression. | Passing deferred abandoned-Draft regression. |
| STORY-005 | STORY-004 | Start | Guarded Draft-to-Proposed submission. | Passing focused Draft-submission validation. |
| STORY-005 | STORY-007 | Integration-validation | Superseded record for terminal-state immutability regression. | Passing deferred Superseded-record regression. |
| STORY-006 | STORY-002; STORY-003 | Start | Additive role evaluation and distinct author/owner persistence. | Passing focused validation for both named capabilities. |
| STORY-006 | STORY-007 | Integration-validation | Abandoned Draft for ownership-transfer denial regression. | Passing deferred abandoned-Draft ownership regression. |
| STORY-007 | STORY-002; STORY-005; STORY-015 | Start | Administrator/approver roles, proposal outcomes, and reusable audit recording. | PR #7 and PR #12 foundation evidence plus passing focused lifecycle validation; predecessor Stories need not all be Done. |
| STORY-008 | STORY-003; STORY-007 | Start | Retained change data and governed replacement links. | Passing focused record-persistence and replacement validation. |
| STORY-009 | STORY-003 | Start | Tagged-record persistence. | Passing focused record-tag validation. |
| STORY-009 | STORY-005; STORY-012 | Integration-validation | Terminal and archived fixtures for exact-tag regression. | Passing deferred exact-tag regression. |
| STORY-010 | STORY-001; STORY-003 | Start | Team-member identity and record tag association. | Passing focused validation for both named capabilities. |
| STORY-011 | STORY-001; STORY-003; STORY-015 | Start | Actor attribution, retained records, and reusable audit recording. | Passing focused validation for all named foundations. |
| STORY-012 | STORY-002; STORY-005; STORY-007; STORY-009; STORY-015 | Start | Administrator enforcement, lifecycle/replacement conditions, archived discovery, and audit recording. | Passing focused validation for each named capability. |
| STORY-013 | STORY-003 | Start | Retained records with no record-delete capability. | Passing focused record-retention validation. |
| STORY-013 | STORY-007; STORY-012 | Integration-validation | Replacement and archived conditions for deletion-denial regression. | Passing deferred record-deletion regression. |
| STORY-014 | STORY-001; STORY-003 | Start | Identity, creation, and editing surfaces. | Passing focused surface validation. |
| STORY-015 | STORY-001; STORY-002; STORY-003 | Start | Actor attribution, role/approver events, and retained record events. | Passing focused validation for each named foundation. |
| STORY-015 | STORY-005; STORY-006; STORY-007; STORY-011; STORY-012 | Integration-validation | Remaining governed event categories. | Passing deferred end-to-end audit regression. |
| STORY-016 | STORY-001–STORY-015 | Integration-validation | Complete integrated MVP. | Passing capacity and browser suites. |

The Start graph is acyclic and contains no Completion dependencies. Every Story
can start when its named capability evidence exists, without waiting for a
predecessor Story status to become Done. Integration-validation relationships
do not block development start or Story completion. TEST-001 must preserve the
coverage Story while assigning later execution ownership before joint
implementation readiness can be approved.

## 8.1 Task Dependency Map

| Parent Story | Task | Depends on | Type | Required capability or outcome | Satisfaction evidence |
| --- | --- | --- | --- | --- | --- |
| STORY-002 | TASK-002 | TASK-001 | Start | Selected identity and configured roles. | Passing focused TASK-001 validation. |
| STORY-002 | TASK-003 | TASK-002 | Start | Governed additive role evaluation. | Passing focused TASK-002 validation. |
| STORY-003 | TASK-004 | TASK-001 | Start | Selected-identity attribution. | Passing focused TASK-001 validation. |
| STORY-004 | TASK-005 | TASK-003; TASK-004 | Start | Approver administration and complete Draft persistence. | Passing focused TASK-003 and TASK-004 validation. |
| STORY-005 | TASK-006 | TASK-002; TASK-005; TASK-021 | Start | Role enforcement, Proposed records, and reusable audit recording. | Passing focused validation for each named capability. |
| STORY-005 | TASK-007 | TASK-005; TASK-006 | Start | Draft submission and proposal decisions. | Passing focused TASK-005 and TASK-006 validation. |
| STORY-006 | TASK-008 | TASK-002; TASK-004; TASK-021 | Start | Role enforcement, author/owner persistence, and reusable audit recording. | Passing focused validation for each named capability. |
| STORY-006 | TASK-009 | TASK-001; TASK-008 | Start | Mock identity selection and ownership transfer. | Passing focused TASK-001 and TASK-008 validation. |
| STORY-007 | TASK-010 | TASK-003; TASK-006 | Start | Administrator/approver administration and Accepted/Rejected outcomes. | Passing focused TASK-003 and TASK-006 validation. |
| STORY-007 | TASK-011 | TASK-010 | Start | Active replacement creation and linking. | Passing focused TASK-010 validation. |
| STORY-008 | TASK-012 | TASK-004; TASK-011; TASK-025 | Start | Retained records, replacement acceptance, and abandonment links. | Passing focused validation for each named capability. |
| STORY-009 | TASK-013 | TASK-004 | Start | Tagged-record persistence. | Passing focused TASK-004 validation. |
| STORY-010 | TASK-014 | TASK-001; TASK-004 | Start | Team-member identity and record tag persistence. | Passing focused TASK-001 and TASK-004 validation. |
| STORY-011 | TASK-015 | TASK-001; TASK-004 | Start | Actor attribution and retained records. | Passing focused TASK-001 and TASK-004 validation. |
| STORY-011 | TASK-016 | TASK-015; TASK-021 | Start | Attributed comments and reusable audit recording. | Passing focused TASK-015 and TASK-021 validation. |
| STORY-012 | TASK-017 | TASK-002; TASK-006; TASK-013 | Start | Administrator enforcement, lifecycle outcomes, and exact-tag discovery. | Passing focused validation for each named capability. |
| STORY-012 | TASK-018 | TASK-010; TASK-017; TASK-025 | Start | Active replacements, archive/restore, and Abandoned preservation. | Passing focused validation for each named capability. |
| STORY-013 | TASK-019 | TASK-004 | Start | Retained record persistence without delete behavior. | Passing focused TASK-004 validation. |
| STORY-013 | TASK-019 | TASK-017; TASK-025 | Integration-validation | Archived and Abandoned fixtures for deletion-denial regression. | Passing deferred TASK-019 regression for both conditions. |
| STORY-014 | TASK-020 | TASK-001; TASK-004 | Start | Entry, creation, and editing surfaces. | Passing focused TASK-001 and TASK-004 validation. |
| STORY-015 | TASK-021 | TASK-001; TASK-002; TASK-004 | Start | Actor attribution, governed role events, and retained record events. | Passing focused validation for each named capability. |
| STORY-016 | TASK-022 | TASK-001–TASK-021; TASK-025 | Start | Complete integrated functional scope at approved capacity. | Merged capability evidence and passing focused validation for every active Task. |
| STORY-016 | TASK-024 | TASK-001–TASK-022; TASK-025 | Start | Complete integrated scope and capacity fixtures. | Passing TASK-022 capacity validation and merged capability evidence. |
| STORY-007 | TASK-025 | TASK-010; TASK-021 | Start | Active replacement Draft and reusable audit recording. | Passing focused TASK-010 and TASK-021 validation. |

TASK-001 has no dependency. The Task Start graph is acyclic and contains no
Completion dependencies. Every Task has an executable start path, and each
parent Story has at least one Task order that reaches completion.

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
9. STORY-010
10. STORY-011
11. STORY-007
12. STORY-008
13. STORY-009
14. STORY-012
15. STORY-013
16. STORY-016

This order establishes Mock identity, role behavior, core records, and audit
support first. Lifecycle then enables replacement governance, immutable
history, and archival. Deletion denial is verified after the applicable record
conditions exist. Capacity and compatibility are validated against the
integrated MVP. Start dependencies are capability gates, not predecessor-Done
gates; integration-validation items run when their execution-owning later
Stories are available.

---

## 10. Planning Risks

- Concurrent proposal decisions or edits could violate the single-outcome
  lifecycle unless transitions are atomic.
- Replacement acceptance spans multiple records and could corrupt links or
  Superseded state if partially completed.
- Replacement abandonment must atomically end the active interval, preserve the
  original link, create audit evidence, and enforce permanent immutability
  without becoming a lifecycle status.
- Mock identity selection affects every attributed and role-dependent action;
  inconsistent propagation could produce incorrect permissions or history.
- Permanent retention and immutable history require controls against
  application-level modification or deletion.
- Archival and restoration must preserve the prior lifecycle status and the
  Abandoned replacement-specific condition without reactivation.
- Concurrent comment-deletion requests must produce one stable `[deleted]`
  presentation and correct audit attribution.
- Functional-capacity validation must exercise all in-scope behavior with 25
  Mock users and 1,000 records even though no response-time assertion applies.
- Until TEST-001 is migrated, its single-Story test ownership can be
  misinterpreted as an earlier-Story completion gate and recreate the lifecycle
  deadlock this Plan removes.
- The existing STORY-001 SSO implementation and legacy Test Design do not
  satisfy this plan and must not be treated as evidence for Version 1.3.

---

## 11. Open Planning Questions

No open product questions remain. Concurrency control, transaction handling,
Mock-identity state propagation, audit immutability, link integrity, and
capacity-test execution are engineering concerns represented by the tasks above
without changing the approved product requirements.

The Test Design Agent must decide the execution-owning Story and execution
designation for the cross-Story cases identified in Section 3. This is an
artifact-migration action, not a new product decision.
