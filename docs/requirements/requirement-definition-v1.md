# Requirement Definition

**Product:** Internal Decision Record Application  
**Version:** 1.1  
**Status:** Approved  
**Scope:** Minimum Viable Product (MVP)  
**Approval date:** 2026-09-01

## Requirement Classification

- **Confirmed Requirement (CR):** Approved product behavior or scope.
- **Open Question (OQ):** An unresolved product decision that must not be
  implemented by assumption.
- **Scope Constraint:** An approved limit that does not require application
  behavior.

Resolved assumptions, recommendations, and questions from Version 1.0 are
removed from the active requirement set. Their disposition is recorded in
**Resolution Traceability**.

# Background

**CR-BG-001 — Confirmed Requirement**

The team needs an internal web application for recording important technical and
business decisions.

**CR-BG-002 — Confirmed Requirement**

The application must preserve enough context for team members to understand in
the future why a decision was made.

# Objective

**CR-OBJ-001 — Confirmed Requirement**

Provide one place where the team can create, review, approve, discover, discuss,
version, and retain decision records.

**CR-OBJ-002 — Confirmed Requirement**

Preserve the history and rationale of decisions, including decisions that are
rejected, replaced, or archived.

# Users

## User Roles

**CR-USR-001 — Confirmed Requirement**

The MVP serves one internal team with up to 25 members.

**CR-USR-002 — Confirmed Requirement**

All team members may view decision records and add comments.

**CR-USR-003 — Confirmed Requirement**

Team members may create decision records. Authors may edit records they authored
only while those records are editable.

**CR-USR-004 — Confirmed Requirement**

Approvers are designated by an administrator.

**CR-USR-005 — Confirmed Requirement**

Approvers may approve their own decision records.

**CR-USR-006 — Confirmed Requirement**

Only administrators may archive or restore decision records.

**CR-USR-007 — Confirmed Requirement**

Author and owner are distinct roles for a decision record.

**CR-USR-008 — Confirmed Requirement**

The author, owner, or an administrator may transfer ownership while a record is
Draft or Proposed. A transfer changes the owner but not the author.

**CR-USR-009 — Confirmed Requirement**

The administrator is the highest responsible person; there is no separate
highest-responsible-person role. Administrators may create replacement versions
of Accepted records.

**CR-USR-010 — Confirmed Requirement**

A user may hold multiple roles simultaneously. Permissions from all roles held
by the user are additive.

# Scope

## MVP Scope

**CR-SCP-001 — Confirmed Requirement**

The MVP includes:

- Organizational single sign-on and access restricted to one internal team.
- Creation and viewing of technical and business decision records.
- Author editing of editable records.
- A defined review and decision lifecycle.
- Administrator assignment of approvers.
- Versioning of Accepted decisions.
- Immutable change history, except for ordinary change history removed with the
  permitted permanent deletion of a Draft.
- Exact filtering by one tag.
- Adding comments, single-level replies, and soft deletion of one's own
  comments.
- Administrator-controlled archival and restoration.
- Role-based ownership transfer.
- Team tag creation and administrator tag administration.

**CR-SCP-002 — Confirmed Requirement**

The MVP must support up to 25 users and 1,000 decision records.

**CR-SCP-003 — Confirmed Requirement**

Decision records may contain internal confidential information but must not
contain regulated personal information or health information.

# Functional Requirements

## Authentication and Access

**CR-FR-001 — Confirmed Requirement**

Users must authenticate through the organization's single sign-on service.

**CR-FR-002 — Confirmed Requirement**

Only authenticated members of the designated internal team may access the
application or its decision records.

## Decision Record Creation and Editing

**CR-FR-003 — Confirmed Requirement**

A team member must be able to create a decision record in Draft status.

**CR-FR-004 — Confirmed Requirement**

Every decision record must contain:

- Title.
- Context.
- Decision.
- Rationale.
- Alternatives considered.
- Consequences.
- Owner.
- Decision date.

**CR-FR-005 — Confirmed Requirement**

A decision record must support one or more tags for discovery.

**CR-FR-006 — Confirmed Requirement**

An author must be able to edit a record they authored while it is Draft or
Proposed. Saving an edit to a Proposed record must automatically return it to
Draft, invalidate any prior or in-progress review, and require resubmission
before another review.

**CR-FR-006A — Confirmed Requirement**

The application must maintain author and owner as distinct record attributes.
The author, owner, or an administrator may transfer ownership only while the
record is Draft or Proposed; authorship must remain unchanged.

**CR-FR-023 — Confirmed Requirement**

Creation and editing screens must show a notice prohibiting entry of regulated
personal information and health information.

## Decision Lifecycle

**CR-FR-007 — Confirmed Requirement**

Decision records must use the lifecycle statuses Draft, Proposed, Accepted,
Rejected, and Superseded.

**CR-FR-008 — Confirmed Requirement**

The supported lifecycle transitions are:

- Draft to Proposed.
- Proposed to Draft, automatically when the Proposed record is edited.
- Proposed to Accepted.
- Proposed to Rejected.
- Accepted to Superseded, automatically when its replacement is accepted.

Archival and restoration do not change this transition list; archival is a
separate record condition.

**CR-FR-009 — Confirmed Requirement**

Only a designated approver may accept or reject a Proposed record.

**CR-FR-010 — Confirmed Requirement**

A designated approver may accept or reject a record they authored.

**CR-FR-024 — Confirmed Requirement**

A Draft must have at least one designated approver before it can be submitted to
Proposed. If it does not, submission must be prevented and an actionable message
must state that at least one designated approver is required.

## Versioning and Immutability

**CR-FR-011 — Confirmed Requirement**

An Accepted record must not be edited directly.

**CR-FR-012 — Confirmed Requirement**

Changes to an Accepted record must be made through a new version linked to that
record. Only an administrator may create the replacement version. An Accepted
record may have no more than one active replacement version. A replacement
version becomes active when its Draft is created and remains active until it is
Accepted, Rejected, or deleted.

**CR-FR-013 — Confirmed Requirement**

When a replacement version is accepted:

- The previous Accepted version must automatically become Superseded.
- The previous and replacement versions must remain linked.
- A user must be able to navigate between them.

**CR-FR-014 — Confirmed Requirement**

The application must retain an immutable version history showing what changed,
who made each change, and when. Rejected and Superseded records must be
completely immutable. The removal of ordinary change history when a Draft is
permanently deleted under CR-FR-022 is the only approved exception.

## Discovery and Tags

**CR-FR-015 — Confirmed Requirement**

Users must be able to apply an exact filter for one tag and receive records
assigned that exact tag.

**CR-FR-016 — Confirmed Requirement**

Rejected, Superseded, and archived records must remain discoverable to
authorized users.

**CR-FR-025 — Confirmed Requirement**

Any team member may create a tag. Only administrators may rename, merge, or
delete tags. Renaming a tag must update that tag's references on all associated
records. Merging a source tag into a target tag must replace the source tag with
the target tag on all records associated with the source tag. Deleting a tag
must remove only that tag association from associated records and must never
delete a record.

## Comments

**CR-FR-017 — Confirmed Requirement**

Team members must be able to add and view comments on a decision record.

**CR-FR-018 — Confirmed Requirement**

Team members must be able to add a single-level reply to a top-level comment.

**CR-FR-019 — Confirmed Requirement**

A team member may delete only their own comments. Deletion must be soft:
`[deleted]` must appear in place of the deleted comment, replies must remain
visible, and an audit record must be retained.

## Archival, Restoration, and Deletion

**CR-FR-020 — Confirmed Requirement**

Only an administrator may archive a decision record, and an administrator may do
so in any lifecycle status. An original Accepted record must not be archived
while it has an active Proposed replacement; archival becomes available after
that replacement review is resolved.

**CR-FR-021 — Confirmed Requirement**

Only an administrator may restore an archived record. Restoration must return
the record to the lifecycle status it held immediately before archival.

**CR-FR-022 — Confirmed Requirement**

Only a record currently in Draft may be permanently deleted. Its author, owner,
or an administrator may permanently delete it. Any non-Draft record is
archive-only and must not be permanently deleted. Permanent Draft deletion must
remove the record content, comments, and ordinary change history. It must
permanently retain a minimal audit event containing the record ID, actor, and
timestamp.

**CR-FR-026 — Confirmed Requirement**

If an author leaves the team, the record must be retained. Its owner or an
administrator may continue handling it through actions otherwise permitted to
that user by this document. Departure does not grant either user an additional
editing permission.

# Non-functional Requirements

## Security and Confidentiality

**CR-NFR-001 — Confirmed Requirement**

The application must prevent users outside the designated team from accessing
decision records.

**CR-NFR-002 — Confirmed Requirement**

The application must protect internal confidential decision information from
unauthorized access.

**CR-NFR-003 — Confirmed Requirement**

Historical versions must be immutable.

**CR-NFR-005 — Confirmed Requirement**

Application data must be encrypted in transit and at rest.

## Capacity and Performance

**CR-NFR-004 — Confirmed Requirement**

The MVP must remain functional with up to 25 authorized users and 1,000 decision
records.

**CR-NFR-006 — Confirmed Requirement**

The record list, record detail, and exact single-tag filter results must each
make their primary content usable within two seconds at the approved capacity of
up to 25 users and 1,000 records. Measurement begins with the user's initiating
action and ends when the primary content is usable. No percentile or
load-testing tool is prescribed.

## Audit and Retention

**CR-NFR-007 — Confirmed Requirement**

The application must create audit records for:

- Authentication events.
- User role changes and approver designation changes.
- Lifecycle transitions.
- Archive and restore actions.
- Ownership transfers.
- Comment deletions.
- Permanent Draft deletions; the permanently retained minimal event must contain
  the record ID, actor, and timestamp.

**CR-NFR-008 — Confirmed Requirement**

Archived records and audit records must be retained permanently.

## Backup and Recovery

**CR-NFR-009 — Confirmed Requirement**

Backups must be performed daily. The recovery point objective (RPO) is 24 hours
and the recovery time objective (RTO) is 8 hours.

## Availability, Accessibility, and Compatibility

**CR-NFR-010 — Scope Constraint**

Availability is best effort during business hours. There is no formal service
level agreement, and no business-hours schedule is defined by this requirement.

**CR-NFR-011 — Confirmed Requirement**

The application must support the current and immediately prior major versions of
Google Chrome and Microsoft Edge.

**CR-NFR-012 — Scope Constraint**

Accessibility is best effort only. The MVP has no accessibility compliance
target or certification requirement.

# Business Rules

**CR-BR-001 — Confirmed Requirement**

Administrators designate approvers.

**CR-BR-002 — Confirmed Requirement**

Self-approval is permitted when the author is a designated approver.

**CR-BR-003 — Confirmed Requirement**

Authors may edit records they authored in Draft or Proposed. Saving an edit to a
Proposed record returns it to Draft, invalidates prior and in-progress review,
and requires resubmission.

**CR-BR-004 — Confirmed Requirement**

Accepted records cannot be edited directly; Rejected and Superseded records are
completely immutable.

**CR-BR-005 — Confirmed Requirement**

An Accepted record can be changed only through a new linked version created by
an administrator.

**CR-BR-006 — Confirmed Requirement**

Acceptance of a replacement automatically supersedes the previous Accepted
version.

**CR-BR-007 — Confirmed Requirement**

Only administrators may archive or restore records. Any lifecycle status may be
archived, subject to CR-BR-014.

**CR-BR-008 — Confirmed Requirement**

Only current Draft records may be permanently deleted, by their author, owner,
or an administrator. Non-Draft records are archive-only. Permanent Draft
deletion removes the record content, comments, and ordinary change history while
permanently retaining a minimal audit event containing the record ID, actor, and
timestamp.

**CR-BR-009 — Confirmed Requirement**

Superseded and Rejected records remain available for future review.

**CR-BR-010 — Confirmed Requirement**

Regulated personal information and health information must not be entered into
decision records.

**CR-BR-011 — Confirmed Requirement**

The author, owner, or an administrator may transfer ownership only in Draft or
Proposed; authorship is unchanged.

**CR-BR-012 — Confirmed Requirement**

Only a comment's author may delete that comment. Deletion is soft and preserves
replies and an audit record.

**CR-BR-013 — Confirmed Requirement**

The administrator is the highest responsible person and the only role permitted
to create a replacement version.

**CR-BR-014 — Confirmed Requirement**

There may be only one active replacement per Accepted record. An original
Accepted record cannot be archived while that replacement is Proposed. A
replacement is active from creation of its Draft until it is Accepted, Rejected,
or deleted.

**CR-BR-015 — Confirmed Requirement**

Users may hold multiple roles, and their permissions are additive.

**CR-BR-016 — Confirmed Requirement**

A Draft cannot become Proposed without at least one designated approver.

**CR-BR-017 — Confirmed Requirement**

Tag rename updates references on every associated record. Tag merge replaces the
source tag with the target tag on every record associated with the source tag.
Tag deletion removes only that tag association and never deletes a record.

# User Stories

**CR-US-001 — Confirmed Requirement**

As a team member, I want to record a technical or business decision and its
rationale so that the team can understand it later.

**CR-US-002 — Confirmed Requirement**

As an author, I want to submit a complete Draft with a designated approver so
that it can be reviewed.

**CR-US-003 — Confirmed Requirement**

As an approver, I want to accept or reject a Proposed decision, including my own,
so that the team has a clear outcome.

**CR-US-004 — Confirmed Requirement**

As a team member, I want to filter decisions by one exact tag so that I can
locate relevant decisions.

**CR-US-005 — Confirmed Requirement**

As a team member, I want to comment and add a single-level reply so that I can
contribute to discussion.

**CR-US-006 — Confirmed Requirement**

As an administrator, I want to create a replacement version of an Accepted
decision so that it can evolve without altering history.

**CR-US-007 — Confirmed Requirement**

As a reader, I want to navigate between Superseded and replacement versions so
that I can understand how a decision evolved.

**CR-US-008 — Confirmed Requirement**

As an administrator, I want to designate approvers so that only authorized users
can decide proposals.

**CR-US-009 — Confirmed Requirement**

As an administrator, I want to archive records in any lifecycle status and
restore their prior status so that records can leave active use without loss.

**CR-US-010 — Confirmed Requirement**

As an author, I want an edit to my Proposed record to restart submission and
review so that reviewers decide only the revised content.

**CR-US-011 — Confirmed Requirement**

As an author, owner, or administrator, I want to transfer ownership of a Draft or
Proposed record without changing authorship.

**CR-US-012 — Confirmed Requirement**

As a comment author, I want to soft-delete my comment while preserving its
replies and audit evidence.

**CR-US-013 — Confirmed Requirement**

As an owner or administrator, I want to continue permitted handling of a retained
record after its author departs.

**CR-US-014 — Confirmed Requirement**

As a team member, I want to create tags, while administrators maintain the tag
set, so that records remain discoverable.

# Acceptance Criteria

## Authentication, Authorization, and Roles

**AC-001**

Given a user is not an authenticated member of the designated team, when the
user attempts to access the application or a decision record, then access is
denied.

**AC-002**

Given an authenticated team member creates a record, when creation completes,
then the record is in Draft and the creator is recorded as its author.

**AC-003**

Given a non-administrator, when the user attempts to designate an approver,
archive, restore, or create an Accepted record's replacement, then the action is
denied.

**AC-023**

Given a user holds multiple roles, when authorization is evaluated, then an
action is permitted if any role held grants it and no role removes permission
granted by another role.

## Required Content and Submission

**AC-004**

Given a Draft is missing a required field, when submission is attempted, then
the transition is prevented and each missing required field is identified.

**AC-005**

Given a Draft has all required fields and at least one designated approver, when
the author submits it, then its status becomes Proposed.

**AC-024**

Given a Draft has no designated approver, when submission is attempted, then it
remains Draft and an actionable message states that at least one designated
approver must be designated.

**AC-037**

Given a user opens a creation or editing screen, then a notice is visible that
regulated personal information and health information must not be entered.

## Approval and Lifecycle

**AC-006**

Given a Proposed record and a user who is not a designated approver, when the
user attempts to accept or reject it, then the action is denied.

**AC-007**

Given a Proposed record whose author is a designated approver, when that author
accepts or rejects it, then the selected transition succeeds.

**AC-008**

Given an author saves an edit to their Proposed record, then it automatically
becomes Draft, all prior and in-progress review is invalidated, and it cannot be
Accepted or Rejected until resubmitted to Proposed.

**AC-038**

Given a Rejected or Superseded record, when any user attempts to change its
record content, lifecycle data, or version content, then the change is denied.
Archival and restoration may change only its separate archival condition.

## Versioning and Ownership

**AC-009**

Given an Accepted record, when any user attempts to edit it directly, then the
edit is prevented.

**AC-010**

Given an Accepted record has no active replacement, when an administrator starts
a replacement, then a linked Draft is created without modifying the Accepted
record and counts as the active replacement from its creation.

**AC-011**

Given a replacement is accepted, when the transition completes, then the
previous Accepted version automatically becomes Superseded.

**AC-012**

Given a Superseded record or its accepted replacement, when an authorized user
views it, then the user can navigate to the related version.

**AC-013**

Given a record has changed, when an authorized user views its history, then the
history identifies what changed, who changed it, and when, and its entries cannot
be modified.

**AC-014**

Given the author, owner, or an administrator transfers a Draft or Proposed
record, when transfer completes, then the owner changes and author is unchanged.
Given any other user or lifecycle status, the transfer is denied.

**AC-025**

Given an Accepted record already has an active replacement, when an
administrator attempts to create another, then creation is denied.

**AC-039**

Given an active replacement, when it is Accepted, Rejected, or deleted, then it
ceases to count as the Accepted record's active replacement.

## Discovery, Tags, and Comments

**AC-015**

Given records have tags, when an authorized user applies one exact tag filter,
then records assigned that exact tag are returned, including matching Rejected,
Superseded, and archived records.

**AC-016**

Given an authenticated team member views a record, when the user adds a comment,
then it is visible on that record.

**AC-017**

Given a top-level comment, when an authenticated team member adds a reply, then
the single-level reply is visible with that comment.

**AC-018**

Given a comment author deletes their own comment, then `[deleted]` replaces its
content, existing replies remain visible, and an audit record of the deletion is
retained.

**AC-019**

Given a user attempts to delete another user's comment, then deletion is denied.

**AC-028**

Given a user attempts to reply to a reply, then the nested-reply action is not
available or is denied.

**AC-029**

Given a team member creates a tag, then it is available for assignment. Given a
non-administrator attempts to rename, merge, or delete a tag, then the action is
denied.

**AC-040**

Given an administrator renames a tag, when the rename completes, then references
on all associated records use the renamed tag.

**AC-041**

Given an administrator merges a source tag into a target tag, when the merge
completes, then the target tag replaces the source tag on all records associated
with the source tag.

**AC-042**

Given an administrator deletes a tag, when deletion completes, then only that
tag association is removed from associated records and no record is deleted.

## Archival, Restoration, Departure, and Deletion

**AC-020**

Given an administrator archives a record in any lifecycle status and no
replacement rule blocks it, then it is marked archived, retained permanently,
and remains discoverable to authorized users.

**AC-021**

Given an archived record, when an administrator restores it, then it returns to
the lifecycle status held immediately before archival.

**AC-022**

Given a non-Draft record, when permanent deletion is attempted, then the action
is unavailable or denied.

**AC-026**

Given an original Accepted record has an active Proposed replacement, when an
administrator attempts to archive the original, then archival is denied. After
that review resolves to Accepted or Rejected, the active-Proposed block no longer
applies.

**AC-027**

Given a current Draft, when its author, owner, or an administrator permanently
deletes it, then its record content, comments, and ordinary change history are
removed and are no longer available or restorable, while a minimal audit event
containing the record ID, actor, and timestamp is retained permanently. Given
any other user, deletion is denied.

**AC-030**

Given an author has left the team, then the authored record remains retained and
its owner or an administrator can perform every action otherwise granted to that
user by this document.

## Non-functional Criteria

**AC-031**

Given up to 1,000 records and test activity within the 25-user capacity, when a
user initiates opening the record list, opening a record detail, or applying an
exact single-tag filter, then the corresponding primary content is usable within
two seconds of that initiating action.

**AC-032**

Given application data is transmitted or stored, then it is encrypted in transit
and at rest.

**AC-033**

Given an authentication event, role or approver change, lifecycle transition,
archive or restore, ownership transfer, comment deletion, or permanent Draft
deletion, then an audit record is created for that event. A permanent Draft
deletion audit event contains the record ID, actor, and timestamp.

**AC-034**

Given an archived record or audit entry, including the minimal event retained
after permanent Draft deletion, then no retention expiry or permanent deletion
action is applied to it.

**AC-035**

Given normal backup operations, then a backup is performed each day. Given
recovery is required, recovery supports no more than 24 hours of data loss and
restoration within 8 hours.

**AC-036**

Given the application is used on the current or immediately prior major version
of Chrome or Edge, then all in-scope functions are supported.

# Edge Cases

The following are either governed by confirmed requirements or require
engineering treatment without an additional product decision:

- If an author leaves, the record is retained; the owner or administrator may
  use only their otherwise-granted permissions. If an owner leaves, ownership
  may be transferred only while Draft or Proposed.
- A user who loses team membership must no longer be granted application access;
  session invalidation mechanics are an engineering concern.
- Concurrent decisions on the same Proposed record must not produce more than
  one lifecycle outcome; the concurrency mechanism is an engineering concern.
- Editing during review invokes AC-008, invalidating that review.
- A rejected replacement remains Rejected and the original remains Accepted.
- A second active replacement is denied under AC-025.
- A replacement counts as active from creation of its Draft until it is
  Accepted, Rejected, or deleted.
- Version links must not corrupt history or create cycles; enforcement is an
  engineering data-integrity concern.
- Archival of an original with an active Proposed replacement is denied under
  AC-026.
- A departed comment author's comments remain retained; only the author can
  request their deletion while authorized.
- Soft deletion of a comment with replies follows AC-018.
- Concurrent reply and deletion requests must preserve the soft-deleted
  placeholder, replies, and audit entry; transaction handling is an engineering
  concern.
- Archive and restore of a Draft returns it to Draft, after which Draft deletion
  rules apply.
- Tag rename, merge, and deletion follow the reference and record-preservation
  behavior in CR-BR-017.
- Permanent Draft deletion removes record content, comments, and ordinary change
  history while permanently retaining the required minimal audit event.

# Out of Scope

The following are approved MVP scope constraints:

**CR-OOS-001 — Confirmed Requirement:** Email notifications.

**CR-OOS-002 — Confirmed Requirement:** File attachments.

**CR-OOS-003 — Confirmed Requirement:** Microsoft Teams, Slack, Jira, and GitHub
integrations.

**CR-OOS-004 — Confirmed Requirement:** Access for external collaborators.

**CR-OOS-005 — Confirmed Requirement:** Organization-wide or multi-team access.

**CR-OOS-006 — Confirmed Requirement:** Storage or processing of regulated
personal information or health information.

**CR-OOS-007 — Confirmed Requirement:** Permanent deletion of non-Draft decision
records.

**CR-OOS-008 — Confirmed Requirement:** In-application notifications.

**CR-OOS-009 — Confirmed Requirement**

Comment editing, nested replies, mentions, and thread resolution.

**CR-OOS-010 — Confirmed Requirement**

Full-text search and combined owner, date, or status filters.

**CR-OOS-011 — Confirmed Requirement**

Exports, reports, and printable views. No special future export or reporting
accommodation beyond the MVP's current structured fields is required.

**CR-OOS-012 — Scope Constraint**

Accessibility compliance certification or a mandatory accessibility standard.

**CR-OOS-013 — Scope Constraint**

A formal availability SLA.

# Open Questions

No unresolved product question currently blocks Development Planning. Test
design, transaction handling, session invalidation, concurrency control, and
data-integrity enforcement are implementation details that may become
engineering tasks and do not require additional product decisions.

# Requirement Traceability

| Requirement area | Acceptance criteria or constraint |
|---|---|
| CR-BG-001–002, CR-OBJ-001–002 | Delivered collectively by AC-002, AC-005–018, AC-020–021, and AC-033–034 |
| CR-USR-001–010 | AC-001–003, AC-006–007, AC-014, AC-023, AC-029 |
| CR-SCP-001–003 | AC-001–005, AC-015–021, AC-024, AC-028–032, AC-037 |
| CR-FR-001–003 | AC-001–002 |
| CR-FR-004–006A | AC-004–005, AC-008, AC-014 |
| CR-FR-007–010, CR-FR-024 | AC-005–008, AC-024, AC-038 |
| CR-FR-011–014 | AC-009–013, AC-025, AC-038–039 |
| CR-FR-015–019, CR-FR-025 | AC-015–019, AC-028–029, AC-040–042 |
| CR-FR-020–022, CR-FR-026 | AC-020–022, AC-026–027, AC-030, AC-033–034 |
| CR-FR-023 | AC-037 |
| CR-NFR-001–005 | AC-001, AC-009, AC-013, AC-032, AC-038 |
| CR-NFR-006 | AC-031 |
| CR-NFR-007–009 | AC-018, AC-033–035 |
| CR-NFR-010, CR-NFR-012 | Approved scope constraints; no mandatory measurable target |
| CR-NFR-011 | AC-036 |
| CR-BR-001–017 | AC-003, AC-005–010, AC-014, AC-018–027, AC-038–042 |
| CR-US-001–014 | Covered by the corresponding functional criteria above |
| CR-OOS-001–013 | Approved scope constraints |

## Resolution Traceability from Version 1.0

| Former item | Resolution in Version 1.1 |
|---|---|
| ASM-USR-001 | Confirmed as CR-USR-010 and CR-BR-015 |
| ASM-002 | Confirmed in CR-FR-014 and CR-BR-004 |
| ASM-003 / REC-004 | Confirmed in CR-FR-021 and AC-021 |
| ASM-005 | Confirmed and narrowed in CR-FR-015 and AC-015 |
| REC-NFR-001 | Confirmed as CR-NFR-006 and made measurable by AC-031 |
| REC-NFR-002 | Rejected as a mandatory target; CR-NFR-012 and CR-OOS-012 apply |
| REC-NFR-003 | Confirmed as CR-NFR-005 and AC-032 |
| REC-NFR-004 | Confirmed and expanded as CR-NFR-007 and AC-033 |
| REC-001 | Confirmed as CR-FR-024, CR-BR-016, and AC-024 |
| REC-002 | Confirmed as CR-FR-012, CR-BR-014, and AC-025 |
| REC-005 | Confirmed as CR-FR-023 and AC-037 |
| ASM-OOS-001 | Confirmed as CR-OOS-010 |
| OQ-001 | Resolved by CR-FR-006A and AC-014 |
| OQ-002 | Resolved by CR-USR-009 and CR-BR-013 |
| OQ-003 | Resolved by CR-FR-006 and AC-008 |
| OQ-004 | Resolved by CR-FR-019 and AC-018 |
| OQ-005 | Resolved by CR-FR-018, CR-OOS-009, and AC-028 |
| OQ-006 | Resolved by CR-FR-025 and AC-029, AC-040–042 |
| OQ-007 | Resolved by CR-FR-012, CR-BR-014, AC-025, and AC-039 |
| OQ-008 | Resolved by CR-FR-026 and AC-030 |
| OQ-009 | Resolved by CR-FR-020–021 and AC-020–021 |
| OQ-010 | Resolved by CR-FR-022, CR-NFR-007–008, and AC-027, AC-033–034 |
| OQ-012 | Resolved by CR-NFR-005–012 and AC-031–036 |
| OQ-013 | Resolved by CR-OOS-011 |

# Definition of Done

The MVP requirement definition is ready for Development Planning when:

1. All Priority Questions are resolved.
2. Assumptions affecting lifecycle, permissions, or MVP scope are confirmed or
   rejected.
3. Every Confirmed Requirement has a measurable acceptance criterion or is
   explicitly identified as a scope constraint.
4. Role permissions and every allowed lifecycle transition are unambiguous.
5. Ownership-transfer permissions, conditions, and lifecycle rules are defined.
6. The administrator's highest-responsible-person role and authorization are
   defined.
7. Re-review behavior after editing a Proposed record is defined.
8. Comment deletion and reply behavior, including deleted comments with replies,
   is defined.
9. Required non-functional targets are measurable and approved.
10. Product stakeholders approve this document as the MVP requirement baseline.
11. Open product questions that affect required data behavior or acceptance
    measurement are resolved.

## Readiness Assessment

Version 1.1 is stakeholder-approved and resolves all Version 1.0 Priority
Questions, assumptions, and recommendations. The four subsequently approved
decisions make the mandatory performance target measurable, define tag mutation
effects, define permanent Draft deletion and its retained audit event, and
define the active-replacement interval. Every item in this document's Definition
of Done is satisfied. The remaining test-design, transaction, session,
concurrency, and integrity considerations are engineering-resolvable
implementation details, not unresolved product decisions. Version 1.1 is
**READY for Development Planning**.
