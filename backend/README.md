# ADR demonstration backend

This FastAPI application implements the STORY-001 Mock identity entry flow,
the STORY-003 structured Draft creation flow, the STORY-004 author editing
and guarded Draft submission flow, STORY-005 proposal decisions and review
restart after author edits, STORY-006 ownership transfer, STORY-007 replacement
version creation, acceptance and abandonment, and STORY-009 exact-tag record
discovery. STORY-010 adds team-member tag creation and multi-tag record
association. Available tags are maintained in the application process and can
be selected when creating or editing a record. Tag rename, merge, and deletion
are not supported. STORY-015 provides append-only audit-event storage and
read-only retrieval for governed actions.
STORY-012 adds administrator-only archival and restoration. Archival is a
separate condition: the lifecycle status and replacement-specific Abandoned
condition remain intact. Archived records remain available in lists, exact-tag
results, and version links; restore returns them to active use without changing
their lifecycle status. An Accepted original with an active Proposed replacement
cannot be archived. Other edits and transitions on archived records require
restoration first. A replacement Draft cannot be submitted while its Accepted
original is archived; the UI hides its submission action but still allows
editing. Archive and restore actions produce attributed audit events.
STORY-011 adds attributed top-level comments to decision records. Comment authors
may soft-delete their own comments; deleted content is replaced by `[deleted]`
and an immutable audit event records the actor and content change. Replies and
comment editing are not supported.
Identity selection is intentionally not authentication and does not create an
access-control boundary.

STORY-013 keeps permanent and soft decision-record deletion unavailable in
every lifecycle, replacement-specific, and archival condition. Archival and
restoration remain available under their rules; this retention boundary applies
to decision records, not comment content.

Records are retained in the application process for this demonstration. They
capture the selected Mock identity as author, a distinct configured owner,
required decision context, one or more tags, and the demo-data boundary notice.
Authors can edit their own eligible Drafts and Proposed records. Editing a
Proposed record returns it to Draft and requires resubmission. Only designated
approvers can accept or reject a Proposed record, including when they authored
it; Rejected records are immutable. Decisions and review restarts are serialized
with approver changes and recorded as attributed lifecycle audit events.
Users operating under a selected Mock identity can list all retained records or
create tags, associate one or more available tags with records, list all
available tags, or apply one exact tag filter. Tag discovery does not exclude
records based on lifecycle or archival condition.
The author, current owner, or administrator Mock identity may transfer an
ordinary Draft or Proposed record to a different configured owner. The author
remains unchanged, and the transfer is recorded with its acting identity and
previous/new owner in the audit store. Terminal and Abandoned records cannot
change owner. If an author leaves the modeled team, their record and author
attribution remain; neither the owner nor administrator receives author-only
editing permission as a result.
Only an administrator can create one linked replacement Draft for an Accepted
record or abandon an active replacement Draft. The new Draft copies the
Accepted decision content and owner and attributes its authorship to the
administrator who created it. Acceptance atomically marks the replacement
Accepted and the prior version Superseded. Rejection or abandonment ends the
active interval; abandonment keeps the linked Draft as Draft, permanently
immutable, and permits another replacement for the still-Accepted original.
The record list exposes links between each original and its retained
replacement versions.
Audit events are durably retained in `backend/data/audit.sqlite3` with the
acting Mock identity, timestamp, subject, and immutable field-level changes.
The record cards expose a Change history disclosure for each retained record,
including attributed content edits and replacement-version changes. The
existing approver designation flow records these events; later governed
workflows can use the same audit store.

Decision records and approver designations are process-local demonstration
state, so this MVP must run as a single application process (the default
`uvicorn app.main:app` invocation). Do not deploy multiple workers: governance
state would diverge between workers even though audit history is shared.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Test

```powershell
pytest
```
