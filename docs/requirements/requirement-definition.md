# Requirement Definition

**Product:** Internal Decision Record Application  
**Version:** 1.3
**Status:** Approved  
**Scope:** Minimum Viable Product (MVP)  
**Approval date:** 2026-09-10

## Requirement Classification

- **Confirmed Requirement (CR):** Approved product behavior or scope.
- **Open Question (OQ):** An unresolved product decision that must not be
  implemented by assumption.
- **Scope Constraint:** An approved limit that does not require application
  behavior.

Resolved assumptions, recommendations, and questions from prior versions are
removed from the active requirement set. Their disposition is recorded in
**Resolution Traceability**.

# Background

**CR-BG-001 — Confirmed Requirement**

The team needs an internal web application for recording important technical and
business decisions.

**CR-BG-002 — Confirmed Requirement**

The application must preserve enough context for team members to understand in
the future why a decision was made.

**CR-BG-003 — Confirmed Requirement**

The current MVP environment cannot support organizational single sign-on in the
short term. The MVP will therefore demonstrate the decision-record workflows
with preconfigured Mock users and demo or synthetic data.

# Objective

**CR-OBJ-001 — Confirmed Requirement**

Provide one MVP demonstration environment where the team can create, review,
approve, discover, discuss, version, and retain decision records using
preconfigured Mock identities and demo or synthetic data.

**CR-OBJ-002 — Confirmed Requirement**

Preserve the history and rationale of decisions, including decisions that are
rejected, replaced, or archived.

# Users

## User Roles

**CR-USR-001 — Confirmed Requirement**

The MVP models one internal team with up to 25 preconfigured Mock users.

**CR-USR-002 — Confirmed Requirement**

All team members may view decision records and add comments.

**CR-USR-003 — Confirmed Requirement**

Team members may create decision records. Authors may edit records they authored
only while those records are editable and have not been marked Abandoned.

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
a Draft that has not been marked Abandoned, or Proposed. A transfer changes the
owner but not the author.

**CR-USR-009 — Confirmed Requirement**

The administrator is the highest responsible person; there is no separate
highest-responsible-person role. Administrators may create replacement versions
of Accepted records and may mark replacement-version Drafts as Abandoned.

**CR-USR-010 — Confirmed Requirement**

A user may hold multiple roles simultaneously. Permissions from all roles held
by the user are additive.

**CR-USR-011 — Confirmed Requirement**

A person using the MVP may choose any preconfigured Mock identity. The choice
establishes the identity and roles used to demonstrate application behavior; it
does not verify the person's identity or membership in the modeled team.

# Scope

## MVP Scope

**CR-SCP-001 — Confirmed Requirement**

The MVP includes:

- Preconfigured Mock users and a login or entry screen on which a person chooses
  the Mock identity used in the application.
- Creation and viewing of technical and business decision records.
- Author editing of editable records.
- A defined review and decision lifecycle.
- Administrator assignment of approvers.
- Versioning of Accepted decisions.
- Administrator abandonment of replacement-version Drafts as a retained,
  replacement-specific condition.
- Immutable change history.
- Exact filtering by one tag.
- Team-member tag creation and association of one or more tags with records.
- Adding top-level comments and author-only soft deletion of one's own comments.
- Administrator-controlled archival and restoration.
- Role-based ownership transfer.
- No deletion of decision records in any lifecycle state.

**CR-SCP-002 — Confirmed Requirement**

The MVP must support up to 25 preconfigured Mock users and 1,000 decision
records.

**CR-SCP-003 — Confirmed Requirement**

The MVP may contain only demo or synthetic data. Real internal confidential
information, regulated personal information, and health information are
prohibited.

# Functional Requirements

## Mock Identity Selection

**CR-FR-027 — Confirmed Requirement**

The MVP must provide a login or entry screen that lists the preconfigured
identities as Mock users and allows a person to choose one before entering the
application.

**CR-FR-028 — Confirmed Requirement**

The application must use the selected Mock identity and its configured roles for
role-dependent behavior and user attribution. Selection of a Mock identity must
not be treated as authentication of the person making the selection.

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

An author must be able to edit a record they authored while it is a Draft that
has not been marked Abandoned, or while it is Proposed. Saving an edit to a
Proposed record must automatically return it to Draft, invalidate any prior or
in-progress review, and require resubmission before another review.

**CR-FR-006A — Confirmed Requirement**

The application must maintain author and owner as distinct record attributes.
The author, owner, or an administrator may transfer ownership only while the
record is a Draft that has not been marked Abandoned, or Proposed; authorship
must remain unchanged.

**CR-FR-023 — Confirmed Requirement**

The login or entry screen and all creation and editing screens must show a
notice that the MVP permits only demo or synthetic data and prohibits real
internal confidential information, regulated personal information, and health
information.

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
separate record condition. Abandoned is also a separate,
replacement-specific condition and is not a lifecycle status or lifecycle
transition.

**CR-FR-009 — Confirmed Requirement**

Only a designated approver may accept or reject a Proposed record.

**CR-FR-010 — Confirmed Requirement**

A designated approver may accept or reject a record they authored.

**CR-FR-024 — Confirmed Requirement**

A Draft that has not been marked Abandoned must have at least one designated
approver before it can be submitted to Proposed. If it does not, submission
must be prevented and an actionable message must state that at least one
designated approver is required. A Draft marked Abandoned cannot be submitted.

## Versioning and Immutability

**CR-FR-011 — Confirmed Requirement**

An Accepted record must not be edited directly.

**CR-FR-012 — Confirmed Requirement**

Changes to an Accepted record must be made through a new version linked to that
record. Only an administrator may create the replacement version. An Accepted
record may have no more than one active replacement version. A replacement
version becomes active when its Draft is created and remains active until it is
Accepted, Rejected, or marked Abandoned.

**CR-FR-013 — Confirmed Requirement**

When a replacement version is accepted:

- The previous Accepted version must automatically become Superseded.
- The previous and replacement versions must remain linked.
- A user must be able to navigate between them.

**CR-FR-014 — Confirmed Requirement**

The application must retain an immutable version history showing what changed,
who made each change, and when. Rejected and Superseded records must be
completely immutable.

**CR-FR-030 — Confirmed Requirement**

Only an administrator may mark an active replacement-version Draft as
Abandoned. Abandoned is a permanent, replacement-specific retained condition,
not a decision-record lifecycle status. The record retains Draft as its
lifecycle status, and marking it Abandoned must:

- Retain the replacement record and its link to the original Accepted record.
- Keep that retained link available for user navigation between the original
  Accepted record and the abandoned replacement.
- Leave the original record Accepted and unchanged.
- End the replacement's active-replacement interval so that an administrator
  may create a new replacement for the original Accepted record.
- Make the abandoned replacement record immutable. Its record content,
  lifecycle data, ownership, approver designations, and version content cannot
  be changed. Comments remain governed by the separate comment requirements,
  and archival or restoration may change only its separate archival condition.

The application must not allow Abandoned to be applied to an ordinary Draft
that was not created as a replacement version, a Proposed replacement, or an
Accepted, Rejected, or Superseded record. It must not provide a way to remove
the Abandoned condition or reactivate an abandoned replacement.

## Discovery and Tags

**CR-FR-015 — Confirmed Requirement**

Users must be able to apply an exact filter for one tag and receive records
assigned that exact tag.

**CR-FR-016 — Confirmed Requirement**

Rejected, Superseded, and archived records must remain discoverable to
users operating under a selected Mock identity.

**CR-FR-025 — Confirmed Requirement**

Any team member may create a tag and make it available for association with
decision records.

## Comments

**CR-FR-017 — Confirmed Requirement**

Team members must be able to add and view top-level comments on a decision
record.

**CR-FR-019 — Confirmed Requirement**

A team member may delete only their own comments. Deletion must be soft:
`[deleted]` must appear in place of the deleted comment, and an audit record
attributed to the deleting Mock identity must be retained.

## Archival, Restoration, and Record Non-deletion

**CR-FR-020 — Confirmed Requirement**

Only an administrator may archive a decision record, and an administrator may do
so in any lifecycle status. An original Accepted record must not be archived
while it has an active Proposed replacement; archival becomes available after
that replacement review is resolved.

**CR-FR-021 — Confirmed Requirement**

Only an administrator may restore an archived record. Restoration must return
the record to the lifecycle status it held immediately before archival.
Restoring an abandoned replacement Draft must preserve its Abandoned condition
and must not reactivate it.

**CR-FR-029 — Confirmed Requirement**

The MVP must not provide permanent or soft deletion of a decision record in any
lifecycle state or replacement-specific condition, including a replacement
Draft marked Abandoned. Archival and restoration remain available under
CR-FR-020 and CR-FR-021 and do not delete the record.

**CR-FR-026 — Confirmed Requirement**

If an author leaves the team, the record must be retained. Its owner or an
administrator may continue handling it through actions otherwise permitted to
that user by this document. Departure does not grant either user an additional
editing permission.

# Non-functional Requirements

## Identity Limitation and Data Integrity

**CR-NFR-003 — Confirmed Requirement**

Historical versions, including replacement-version Drafts marked Abandoned,
must be immutable.

**CR-NFR-013 — Confirmed Requirement**

The MVP must clearly identify selectable identities as Mock and must not state or
imply that Mock identity selection authenticates a person, verifies team
membership, or creates a security boundary that protects application data from
unauthorized access.

## Data Protection

**CR-NFR-005 — Confirmed Requirement**

In deployed environments, application traffic between a user's client and the
application must use HTTPS. This requirement does not apply to local development.

## Capacity and Performance

**CR-NFR-004 — Confirmed Requirement**

The MVP must remain functional with up to 25 preconfigured Mock users and 1,000
decision records.

**CR-NFR-006 — Scope Constraint**

Usability responsiveness at the approved capacity is best effort. The MVP has
no formal response-time target or performance acceptance measurement.

## Audit and Retention

**CR-NFR-007 — Confirmed Requirement**

The application must create audit records for:

- User role changes and approver designation changes.
- Lifecycle transitions.
- Replacement-Draft abandonment actions.
- Archive and restore actions.
- Ownership transfers.
- Comment deletions.

**CR-NFR-008 — Confirmed Requirement**

Archived records and audit records must be retained permanently.

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

Authors may edit records they authored in a Draft that has not been marked
Abandoned, or in Proposed. Saving an edit to a Proposed record returns it to
Draft, invalidates prior and in-progress review, and requires resubmission.

**CR-BR-004 — Confirmed Requirement**

Accepted records cannot be edited directly; Rejected, Superseded, and
replacement-version Drafts marked Abandoned are immutable as decision records.

**CR-BR-005 — Confirmed Requirement**

An Accepted record can be changed only through a new linked version created by
an administrator.

**CR-BR-006 — Confirmed Requirement**

Acceptance of a replacement automatically supersedes the previous Accepted
version.

**CR-BR-007 — Confirmed Requirement**

Only administrators may archive or restore records. Any lifecycle status may be
archived, subject to CR-BR-014.

**CR-BR-009 — Confirmed Requirement**

Superseded and Rejected records remain available for future review.

**CR-BR-010 — Confirmed Requirement**

Only demo or synthetic data may be entered into or otherwise used in the MVP.
Real internal confidential information, regulated personal information, and
health information must not be entered, stored, or processed.

**CR-BR-011 — Confirmed Requirement**

The author, owner, or an administrator may transfer ownership only in a Draft
that has not been marked Abandoned, or in Proposed; authorship is unchanged.

**CR-BR-012 — Confirmed Requirement**

Only a comment's author may delete that comment. Deletion is soft and preserves
the `[deleted]` placeholder and an audit record attributed to the deleting Mock
identity.

**CR-BR-013 — Confirmed Requirement**

The administrator is the highest responsible person and the only role permitted
to create a replacement version.

**CR-BR-014 — Confirmed Requirement**

There may be only one active replacement per Accepted record. An original
Accepted record cannot be archived while that replacement is Proposed. A
replacement is active from creation of its Draft until it is Accepted or
Rejected, or until its Draft is marked Abandoned.

**CR-BR-015 — Confirmed Requirement**

Users may hold multiple roles, and their permissions are additive.

**CR-BR-016 — Confirmed Requirement**

A Draft that has not been marked Abandoned cannot become Proposed without at
least one designated approver. A Draft marked Abandoned cannot become Proposed.

**CR-BR-018 — Confirmed Requirement**

The selected Mock identity determines the roles and attribution used by the MVP.
Because any person may choose a preconfigured Mock identity, these roles govern
demonstrated application behavior but do not establish real-world authorization
or access control.

**CR-BR-019 — Confirmed Requirement**

Only an administrator may mark an active replacement-version Draft as
Abandoned. The Abandoned condition is permanent, retained,
replacement-specific, and immutable as defined by CR-FR-030. It is not a
decision-record lifecycle status, does not delete the record, does not change
the original Accepted record, and ends the active-replacement interval.

# User Stories

**CR-US-001 — Confirmed Requirement**

As a team member, I want to record a technical or business decision and its
rationale so that the team can understand it later.

**CR-US-002 — Confirmed Requirement**

As an author, I want to submit a complete Draft that has not been marked
Abandoned and has a designated approver so that it can be reviewed.

**CR-US-003 — Confirmed Requirement**

As an approver, I want to accept or reject a Proposed decision, including my own,
so that the team has a clear outcome.

**CR-US-004 — Confirmed Requirement**

As a team member, I want to filter decisions by one exact tag so that I can
locate relevant decisions.

**CR-US-005 — Confirmed Requirement**

As a team member, I want to add a top-level comment so that I can contribute to
discussion.

**CR-US-006 — Confirmed Requirement**

As an administrator, I want to create a replacement version of an Accepted
decision so that it can evolve without altering history.

**CR-US-007 — Confirmed Requirement**

As a reader, I want to navigate between an original decision and its accepted
or abandoned replacement versions so that I can understand how the decision
evolved.

**CR-US-008 — Confirmed Requirement**

As an administrator, I want to designate approvers so that only designated Mock
approver identities can decide proposals.

**CR-US-009 — Confirmed Requirement**

As an administrator, I want to archive records in any lifecycle status and
restore their prior status so that records can leave active use without loss.

**CR-US-010 — Confirmed Requirement**

As an author, I want an edit to my Proposed record to restart submission and
review so that reviewers decide only the revised content.

**CR-US-011 — Confirmed Requirement**

As an author, owner, or administrator, I want to transfer ownership of a
non-abandoned Draft or a Proposed record without changing authorship.

**CR-US-012 — Confirmed Requirement**

As a comment author, I want to soft-delete my comment while preserving a visible
placeholder and audit attribution.

**CR-US-013 — Confirmed Requirement**

As an owner or administrator, I want to continue permitted handling of a retained
record after its author departs.

**CR-US-014 — Confirmed Requirement**

As a team member, I want to create tags and associate them with records so that
records remain discoverable.

**CR-US-015 — Confirmed Requirement**

As an MVP user, I want to choose a preconfigured Mock identity on the login or
entry screen so that I can demonstrate behavior associated with that identity's
roles.

**CR-US-016 — Confirmed Requirement**

As an administrator, I want to mark an unneeded replacement-version Draft as
Abandoned so that its record and original-version link are preserved while a
new replacement can be created.

# Acceptance Criteria

## Mock Identity and Roles

**AC-043**

Given the login or entry screen is displayed, then all available identities are
identified as preconfigured Mock users. When a person chooses one, then the
application opens using that Mock identity's configured roles and uses that
identity for subsequent user attribution.

**AC-044**

Given the login or entry screen or other identity-related MVP content is
displayed, then it does not require organizational SSO and does not state or
imply that choosing a Mock identity verifies the person, verifies team
membership, or protects application data from unauthorized access.

**AC-002**

Given a selected Mock team-member identity creates a record, when creation
completes, then the record is in Draft and the selected Mock identity is
recorded as its author.

**AC-003**

Given a non-administrator, when the user attempts to designate an approver,
archive, restore, create an Accepted record's replacement, or mark a replacement
Draft as Abandoned, then the action is denied.

**AC-023**

Given a selected Mock identity holds multiple roles, when role-dependent
behavior is evaluated, then an action is permitted if any role held grants it
and no role removes permission granted by another role.

## Required Content and Submission

**AC-004**

Given a Draft that has not been marked Abandoned is missing a required field,
when submission is attempted, then the transition is prevented and each missing
required field is identified.

**AC-005**

Given a Draft that has not been marked Abandoned has all required fields and at
least one designated approver, when the author submits it, then its status
becomes Proposed.

**AC-024**

Given a Draft that has not been marked Abandoned has no designated approver,
when submission is attempted, then it remains Draft and an actionable message
states that at least one designated approver must be designated.

**AC-037**

Given a person opens the login or entry screen or a creation or editing screen,
then a notice is visible that only demo or synthetic data may be used and that
real internal confidential information, regulated personal information, and
health information must not be entered.

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

Given a Superseded record or its accepted replacement, when a user views it
under a selected Mock identity, then the user can navigate to the related
version.

**AC-013**

Given a record has changed, when a user under a selected Mock identity views its
history, then the history identifies what changed, which Mock identity made the
change, and when, and its entries cannot be modified.

**AC-014**

Given the author, owner, or an administrator transfers a Draft that has not been
marked Abandoned, or a Proposed record, when transfer completes, then the owner
changes and author is unchanged. Given a Draft marked Abandoned, any other user,
or any other lifecycle status, the transfer is denied.

**AC-025**

Given an Accepted record already has an active replacement, when an
administrator attempts to create another, then creation is denied.

**AC-039**

Given an active replacement, when it is Accepted, Rejected, or its Draft is
marked Abandoned, then it ceases to count as the Accepted record's active
replacement.

**AC-046**

Given an Accepted record has an active replacement-version Draft, when an
administrator marks that Draft as Abandoned, then the replacement retains Draft
as its lifecycle status, gains the permanent replacement-specific Abandoned
condition, and no longer counts as active. The replacement record and its link
to the original are retained and users can navigate between them; the original
remains Accepted and unchanged; an audit record identifies the action,
administrator, and time; and an administrator can create a new linked
replacement.

**AC-047**

Given a replacement-version Draft marked Abandoned, when any user attempts to
change its record content, lifecycle data, ownership, approver designations, or
version content, remove its Abandoned condition, reactivate it, or submit it,
then the action is denied. An administrator may still archive or restore it;
restoration preserves both its Draft lifecycle status and its Abandoned
condition. Given an ordinary Draft, a Proposed replacement, or an Accepted,
Rejected, or Superseded record, when an administrator attempts to mark it
Abandoned, then the action is denied.

## Discovery, Tags, and Comments

**AC-015**

Given records have tags, when a user under a selected Mock identity applies one
exact tag filter, then records assigned that exact tag are returned, including
matching Rejected, Superseded, and archived records.

**AC-016**

Given a selected Mock team-member identity views a record, when the user adds a
comment, then it is visible on that record and attributed to that Mock identity.

**AC-018**

Given a comment author deletes their own comment, then `[deleted]` replaces its
content and an audit record attributed to the deleting Mock identity is
retained.

**AC-019**

Given a user attempts to delete another user's comment, then deletion is denied.

**AC-029**

Given a team member creates a tag, then it is available for association with one
or more decision records. Given a team member associates one or more tags with a
record, then each selected tag is associated with that record.

## Archival, Restoration, Departure, and Record Non-deletion

**AC-020**

Given an administrator archives a record in any lifecycle status and no
replacement rule blocks it, then it is marked archived, retained permanently,
and remains discoverable to users under selected Mock identities.

**AC-021**

Given an archived record, when an administrator restores it, then it returns to
the lifecycle status held immediately before archival.

**AC-026**

Given an original Accepted record has an active Proposed replacement, when an
administrator attempts to archive the original, then archival is denied. After
that review resolves to Accepted or Rejected, the active-Proposed block no longer
applies.

**AC-030**

Given an author has left the team, then the authored record remains retained and
its owner or an administrator can perform every action otherwise granted to that
user by this document.

**AC-045**

Given a decision record in any lifecycle, replacement-specific, or archival
condition, including a replacement Draft marked Abandoned, when any user
attempts to delete the record, then no permanent or soft record-deletion action
is available or the attempt is denied. The record remains available for
otherwise-permitted archival or restoration.

## Non-functional Criteria

**AC-031**

Given 25 preconfigured Mock users and 1,000 decision records, when each in-scope
function is exercised, then it continues to satisfy its applicable functional
acceptance criteria. No response-time assertion applies.

**AC-032**

Given a deployed environment, when a user accesses or uses the application, then
the client-facing application connection and subsequent application traffic use
HTTPS. No equivalent HTTPS acceptance check is required for local development.

**AC-033**

Given a role or approver change, lifecycle transition, archive or restore,
replacement-Draft abandonment, ownership transfer, or comment deletion, then an
audit record is created for that event. A replacement-Draft abandonment audit
record identifies the acting administrator and time. A comment-deletion audit
record identifies the deleting Mock identity.

**AC-034**

Given an archived record or audit entry, then no retention expiry or permanent
deletion action is applied to it.

**AC-036**

Given the application is used on the current or immediately prior major version
of Chrome or Edge, then all in-scope functions are supported.

# Edge Cases

The following are either governed by confirmed requirements or require
engineering treatment without an additional product decision:

- If an author leaves, the record is retained; the owner or administrator may
  use only their otherwise-granted permissions. If an owner leaves, ownership
  may be transferred only while the record is a Draft that has not been marked
  Abandoned, or Proposed.
- A person may select a Mock identity configured with any role, including
  administrator. The resulting permissions demonstrate role behavior only and
  do not verify or authorize the person in the real world.
- Concurrent decisions on the same Proposed record must not produce more than
  one lifecycle outcome; the concurrency mechanism is an engineering concern.
- Editing during review invokes AC-008, invalidating that review.
- A rejected replacement remains Rejected and the original remains Accepted.
- A second active replacement is denied under AC-025.
- A replacement counts as active from creation of its Draft until it is
  Accepted, Rejected, or its Draft is marked Abandoned.
- Only an active replacement-version Draft can be marked Abandoned, and only by
  an administrator. Ordinary Drafts, Proposed replacements, Accepted, Rejected,
  and Superseded records cannot be marked Abandoned.
- An abandoned replacement retains Draft as its lifecycle status, its
  replacement-specific Abandoned condition, its record, and its link to the
  original Accepted record. It is immutable as a decision record, cannot be
  submitted or reactivated, does not supersede or otherwise change the original,
  and no longer prevents creation of a new replacement.
- Version links must not corrupt history or create cycles; enforcement is an
  engineering data-integrity concern.
- Archival of an original with an active Proposed replacement is denied under
  AC-026.
- A departed comment author's comments remain retained; only the author can
  request their deletion through the Mock identity attributed as the comment
  author and subject to the otherwise-applicable rules.
- Concurrent comment-deletion requests must preserve one soft-deleted
  placeholder and the required audit attribution; transaction handling is an
  engineering concern.
- Archive and restore of a Draft returns it to Draft. Neither action deletes the
  record.
- An archived replacement remains active unless it becomes Accepted, Rejected,
  or Abandoned; archival and restoration do not alter its lifecycle status or
  its Abandoned condition. Restoring an abandoned replacement Draft does not
  reactivate it.
- Decision-record deletion remains unavailable in every lifecycle,
  replacement-specific, and archival condition, including Abandoned, under
  AC-045.

# Out of Scope

The following are approved MVP scope constraints:

**CR-OOS-001 — Confirmed Requirement:** Email notifications.

**CR-OOS-002 — Confirmed Requirement:** File attachments.

**CR-OOS-003 — Confirmed Requirement:** Microsoft Teams, Slack, Jira, and GitHub
integrations.

**CR-OOS-004 — Confirmed Requirement:** External-collaborator identities and
workflows.

**CR-OOS-005 — Confirmed Requirement:** Organization-wide or multi-team
identities and workflows.

**CR-OOS-006 — Confirmed Requirement:** Storage or processing of real internal
confidential information, regulated personal information, or health
information.

**CR-OOS-007 — Confirmed Requirement:** Permanent or soft deletion of decision
records in any lifecycle, replacement-specific, or archival condition,
including Abandoned.

**CR-OOS-008 — Confirmed Requirement:** In-application notifications.

**CR-OOS-009 — Confirmed Requirement**

Comment editing, all comment replies, mentions, and thread resolution.

**CR-OOS-010 — Confirmed Requirement**

Full-text search and combined owner, date, or status filters.

**CR-OOS-011 — Confirmed Requirement**

Exports, reports, and printable views. No special future export or reporting
accommodation beyond the MVP's current structured fields is required.

**CR-OOS-012 — Scope Constraint**

Accessibility compliance certification or a mandatory accessibility standard.

**CR-OOS-013 — Scope Constraint**

A formal availability SLA.

**CR-OOS-014 — Confirmed Requirement**

Production-grade identity and access control, including organizational SSO,
verification of team membership, and enforcement of a real security boundary.
No production authentication behavior or future implementation approach is
defined by this MVP requirement.

The following additional exclusions are approved for Version 1.3 and do not
define or imply a future solution:

- Backup and recovery, including daily backups, recovery point objectives,
  recovery time objectives, and restoration evidence.
- Encryption at rest.
- Tag administration, including tag rename, merge, and deletion.
- A formal response-time target or performance acceptance measurement.

# Open Questions

No unresolved product question currently blocks Development Planning.
Post-abandonment behavior is fully defined by CR-FR-030: the retained
replacement-version Draft is immutable and cannot be reactivated.
Production-grade identity, backup and recovery, encryption at rest, tag
administration, comment replies, decision-record deletion, and a formal
response-time target are outside MVP scope and have no defined future
implementation requirements. Test design, transaction handling, concurrency
control, and data-integrity enforcement are implementation details that may
become engineering tasks and do not require additional product decisions.

# Requirement Traceability

| Requirement area | Acceptance criteria or constraint |
|---|---|
| CR-BG-001–003, CR-OBJ-001–002 | Delivered collectively by AC-002, AC-005–016, AC-018–021, AC-031–034, AC-037, AC-043–047 |
| CR-USR-001–011 | AC-002–003, AC-006–007, AC-014, AC-023, AC-029, AC-043–044, AC-046–047 |
| CR-SCP-001–003 | AC-002–005, AC-015–016, AC-018–021, AC-024, AC-029–031, AC-037, AC-043–047 |
| CR-FR-003 | AC-002 |
| CR-FR-004–006A | AC-004–005, AC-008, AC-014 |
| CR-FR-007–010, CR-FR-024 | AC-005–008, AC-024, AC-038 |
| CR-FR-011–014, CR-FR-030 | AC-009–013, AC-025, AC-038–039, AC-046–047 |
| CR-FR-015–017, CR-FR-019, CR-FR-025 | AC-015–016, AC-018–019, AC-029 |
| CR-FR-020–021, CR-FR-026, CR-FR-029 | AC-020–021, AC-026, AC-030, AC-045 |
| CR-FR-023 | AC-037 |
| CR-FR-027–028 | AC-002, AC-043–044 |
| CR-NFR-003 | AC-009, AC-013, AC-038, AC-047 |
| CR-NFR-005 | AC-032 |
| CR-NFR-004 | AC-031 |
| CR-NFR-006, CR-NFR-010, CR-NFR-012 | Approved scope constraints; no mandatory measurable target |
| CR-NFR-007–008 | AC-018, AC-033–034, AC-046 |
| CR-NFR-011 | AC-036 |
| CR-NFR-013 | AC-044 |
| CR-BR-001–007, CR-BR-009–016, CR-BR-018–019 | AC-003, AC-005–010, AC-014, AC-018–021, AC-023–026, AC-029–030, AC-037–039, AC-043–047 |
| CR-US-001–016 | Covered by the corresponding functional criteria above |
| CR-OOS-001–014 | Approved scope constraints |
| Version 1.3 additional exclusions | Approved scope constraints for backup/recovery, encryption at rest, tag administration, and a formal response-time target or performance acceptance measurement |

Historical resolution tables below preserve the IDs that applied in their named
versions. Items retired from the active Version 1.3 definition are explicitly
identified in **Resolution Traceability from Version 1.2**.

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

## Resolution Traceability from Version 1.1

| Version 1.1 item | Resolution in Version 1.2 |
|---|---|
| CR-SCP-001, CR-FR-001–002, AC-001 | Organizational SSO and designated-team access enforcement were removed from the MVP. CR-FR-027–028 and AC-043–044 define the approved preconfigured Mock-user selection behavior. |
| CR-USR-001 | Revised to define the modeled team as up to 25 preconfigured Mock users. |
| CR-SCP-003, CR-FR-023, CR-BR-010, AC-037, CR-OOS-006 | Revised to allow only demo or synthetic data and to prohibit real internal confidential information, regulated personal information, and health information. |
| CR-NFR-001–002 | Removed because Mock identity selection is not a real security boundary and the MVP must not contain information that requires internal-confidentiality protection. CR-NFR-013 and AC-044 define the approved limitation. |
| CR-NFR-005, AC-032 | Unchanged. Restricting the MVP to demo or synthetic data does not remove the separately approved encryption requirement. |
| CR-NFR-007, AC-033 | Authentication-event auditing was removed. All other approved audit events remain unchanged. |
| Former team-membership edge case | Immediate access revocation and session invalidation were removed because the MVP neither verifies team membership nor provides a real access-control boundary. |
| CR-OOS-004–006, CR-OOS-014 | Clarified that external, organization-wide, and multi-team identity workflows and all production-grade identity and access control are outside MVP scope. |

## Resolution Traceability from Version 1.2

| Version 1.2 item | Resolution in Version 1.3 |
|---|---|
| CR-SCP-001 | Revised to remove Draft deletion, comment replies, and tag administration; to retain top-level comments, author-only comment soft deletion, team tag creation and association, and archival/restoration; and to state that no decision record may be deleted. |
| CR-FR-012, CR-BR-014, AC-039, replacement edge cases | Revised so an active replacement ends when Accepted, Rejected, or its Draft is marked Abandoned. Deletion is not a lifecycle outcome. |
| New CR-FR-030, CR-BR-019, CR-US-016, AC-046–047 | Added the administrator-only, replacement-specific Abandoned condition for an active replacement Draft. The abandoned record and original-version link are retained, the original remains Accepted, the abandoned record is immutable and cannot be reactivated, a new replacement may be created, and Abandoned is not a global lifecycle status or deletion. |
| CR-FR-014 | Revised to remove the exception that allowed ordinary history to be removed with a permanently deleted Draft. |
| CR-FR-018, AC-017, AC-028 | Retired. Comment replies, including single-level and nested replies, are outside MVP scope under revised CR-OOS-009. |
| CR-FR-019, CR-BR-012, CR-US-005, CR-US-012, AC-018, comment edge cases | Revised to cover top-level comments and author-only soft deletion with a `[deleted]` placeholder and audit attribution, without reply behavior. |
| CR-FR-022, CR-BR-008, AC-022, AC-027 | Retired. New CR-FR-029 and AC-045 state that decision records cannot be permanently or softly deleted in any lifecycle or archival condition. CR-OOS-007 was expanded accordingly. |
| CR-FR-025, CR-US-014, AC-029 | Revised to retain team-member tag creation and record association only. |
| CR-BR-017, AC-040–042 | Retired. Tag rename, merge, and deletion are outside MVP scope. |
| CR-NFR-005, AC-032 | Revised to require observable HTTPS use for deployed environments only. Encryption at rest was removed, and local development has no HTTPS requirement. |
| CR-NFR-006, AC-031 | The two-second response target and its measurement were removed. CR-NFR-006 is now a best-effort usability Scope Constraint; AC-031 now verifies functional capacity only. |
| CR-NFR-007, AC-033 | Revised to remove permanent Draft-deletion audit behavior. Comment-deletion audit attribution remains required. |
| CR-NFR-008, AC-034 | Retained for archived records and audit records, with all references to permanent Draft-deletion audit retention removed. |
| CR-NFR-009, AC-035 | Retired. Backup and recovery, including daily backup, RPO, RTO, and restoration evidence, are outside MVP scope without a defined future solution. |
| CR-OOS-009 | Revised to place all comment replies outside MVP scope. |
| Non-functional exclusions | Encryption at rest and a formal response-time target or performance acceptance measurement are outside MVP scope. |

# Definition of Done

The MVP requirement definition is ready for Development Planning when:

1. All Priority Questions are resolved.
2. Assumptions affecting lifecycle, permissions, or MVP scope are confirmed or
   rejected.
3. Every Confirmed Requirement has a measurable acceptance criterion or is
   explicitly identified as a scope constraint.
4. Role permissions and every allowed lifecycle transition are unambiguous.
5. Ownership-transfer permissions, conditions, and lifecycle rules are defined.
6. The administrator's highest-responsible-person role and permissions are
   defined.
7. Re-review behavior after editing a Proposed record is defined.
8. Top-level comment behavior and author-only soft deletion with a `[deleted]`
   placeholder and audit attribution are defined; comment replies are explicitly
   outside scope.
9. Required non-functional behaviors are measurable and approved; any
   intentionally non-measurable target is identified as a Scope Constraint.
10. Mock identity selection, role attribution, and its lack of a real security
    boundary are explicit and testable.
11. The demo-or-synthetic-only data restriction and all prohibited information
    categories are explicit wherever users enter data.
12. Product stakeholders approve this document as the MVP requirement baseline.
13. Open product questions that affect required data behavior or acceptance
    measurement are resolved.
14. Decision-record deletion is unavailable in every lifecycle,
    replacement-specific, and archival condition, including Abandoned, and
    remains distinct from archival and restoration.
15. Removed backup/recovery, encryption-at-rest, tag-administration, comment-reply,
    and formal response-time requirements are documented as outside MVP scope.
16. Administrator-only abandonment of an active replacement-version Draft is
    testable as a retained, immutable, non-deletion condition that ends the
    active-replacement interval without adding a global lifecycle status;
    inapplicable record types and post-abandonment behavior are explicit.

## Readiness Assessment

Version 1.3 is stakeholder-approved. It retains the unaffected Version 1.2
requirements and incorporates the approved removal of backup and recovery,
decision-record deletion, encryption at rest, tag administration, comment
replies, and the formal response-time target. It also incorporates the approved
administrator-only Abandoned condition for replacement-version Drafts, including
retention, immutability, auditability, the active-replacement endpoint, and
continued preservation through archive and restore. It retains
archival/restoration, top-level comment soft deletion, team-member tag creation
and association, HTTPS for deployed environments, and functional capacity for
25 preconfigured Mock users and 1,000 decision records. It does not define
future solutions for the removed capabilities. Every item in this document's
Definition of Done is satisfied. The remaining test-design, transaction,
concurrency, and integrity considerations are engineering-resolvable
implementation details, not unresolved product decisions. Version 1.3 is
**READY for Development Planning**.
