from datetime import date
import json
from typing import Annotated, Literal

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from pydantic import BaseModel, field_validator

from app.audit import (
    AuditChange,
    AuditEvent,
    AuditEventStore,
    AuditEventType,
    create_audit_event,
)
from app.governance import (
    change_approver_designation,
    designated_approver_snapshot,
    governance_lock,
    is_administrator,
    is_designated_approver,
    role_permissions,
)
from app.identities import MOCK_IDENTITIES, MockIdentity, Role, find_mock_identity
from app.records import (
    CommentNotFoundError,
    DecisionComment,
    DecisionCommentCreate,
    DecisionRecord,
    DecisionRecordCreate,
    DecisionRecordStore,
    DecisionRecordUpdate,
    DraftSubmissionError,
    RecordActionError,
    RecordNotFoundError,
)
from app.tags import DuplicateTagError, TagStore

MOCK_IDENTITY_COOKIE = "adr_mock_identity"

router = APIRouter(prefix="/api")


class MockIdentitySelection(BaseModel):
    identity_id: str


class MockSession(BaseModel):
    selected_identity: MockIdentity | None


class AttributionPreview(BaseModel):
    actor: MockIdentity
    message: str


class DecisionRecordCollection(BaseModel):
    records: list[DecisionRecord]


class AuditEventCollection(BaseModel):
    events: list[AuditEvent]


class ApproverDesignation(BaseModel):
    identity_id: str


class DecisionSubmission(BaseModel):
    outcome: Literal["Accepted", "Rejected"]


class OwnershipTransfer(BaseModel):
    owner_id: str


class ApproverList(BaseModel):
    approvers: list[MockIdentity]


class GovernancePermissions(BaseModel):
    identity: MockIdentity
    designated_approver: bool
    permissions: list[str]


class TagCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def require_non_blank_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Tag name must not be blank.")
        return value


class TagCollection(BaseModel):
    tags: list[str]


class CreatedTag(BaseModel):
    name: str


SelectedIdentityCookie = Annotated[str | None, Cookie(alias=MOCK_IDENTITY_COOKIE)]


def require_selected_identity(
    selected_identity_id: SelectedIdentityCookie = None,
) -> MockIdentity:
    identity = find_mock_identity(selected_identity_id)
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Choose a Mock identity before continuing.",
        )
    return identity


def require_administrator(identity: MockIdentity) -> MockIdentity:
    if not is_administrator(identity):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an administrator Mock identity may perform this action.",
        )
    return identity


def get_record_store(request: Request) -> DecisionRecordStore:
    return request.app.state.record_store


def get_audit_event_store(request: Request) -> AuditEventStore:
    return request.app.state.audit_event_store


def get_tag_store(request: Request) -> TagStore:
    return request.app.state.tag_store


def require_team_member(identity: MockIdentity) -> MockIdentity:
    if Role.TEAM_MEMBER not in identity.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only a team-member Mock identity may create tags.",
        )
    return identity


def audit_value(value: object) -> str | bool | None:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return json.dumps(value)
    if isinstance(value, MockIdentity):
        return value.id
    return str(value)


def record_lifecycle_transition(
    request: Request,
    actor: MockIdentity,
    before: DecisionRecord,
    after: DecisionRecord,
    *,
    changed_fields: tuple[str, ...] = (),
    related_transition: tuple[DecisionRecord, DecisionRecord] | None = None,
) -> None:
    changes = []
    if before.status != after.status:
        changes.append(
            AuditChange(field="status", before=before.status, after=after.status)
        )
    for field in changed_fields:
        before_value = getattr(before, field)
        after_value = getattr(after, field)
        if before_value != after_value:
            changes.append(
                AuditChange(
                    field=field,
                    before=audit_value(before_value),
                    after=audit_value(after_value),
                )
            )
    events = []
    if related_transition is not None:
        related_before, related_after = related_transition
        changes.append(
            AuditChange(
                field=f"related_record.{related_before.id}.status",
                before=related_before.status,
                after=related_after.status,
            )
        )
        events.append(
            create_audit_event(
                event_type=AuditEventType.LIFECYCLE_TRANSITIONED,
                actor=actor,
                subject_type="decision_record",
                subject_id=related_before.id,
                changes=(
                    AuditChange(
                        field="status",
                        before=related_before.status,
                        after=related_after.status,
                    ),
                ),
            )
        )
    if not changes:
        return

    event_type = (
        AuditEventType.LIFECYCLE_TRANSITIONED
        if before.status != after.status
        else AuditEventType.RECORD_UPDATED
    )
    events.insert(
        0,
        create_audit_event(
            event_type=event_type,
            actor=actor,
            subject_type="decision_record",
            subject_id=before.id,
            changes=changes,
        ),
    )
    get_audit_event_store(request).record_many(events)


def record_comment_deletion(
    request: Request,
    actor: MockIdentity,
    record: DecisionRecord,
    before: DecisionComment,
    after: DecisionComment,
) -> None:
    get_audit_event_store(request).record(
        event_type=AuditEventType.COMMENT_DELETED,
        actor=actor,
        subject_type="decision_record",
        subject_id=record.id,
        changes=(
            AuditChange(
                field=f"comment.{before.id}.content",
                before=before.content,
                after=after.content,
            ),
            AuditChange(
                field=f"comment.{before.id}.deleted",
                before=before.deleted,
                after=after.deleted,
            ),
        ),
    )


@router.get("/mock-identities", response_model=list[MockIdentity])
def list_mock_identities() -> list[MockIdentity]:
    return list(MOCK_IDENTITIES)


@router.get("/mock-session", response_model=MockSession)
def get_mock_session(
    selected_identity_id: SelectedIdentityCookie = None,
) -> MockSession:
    return MockSession(selected_identity=find_mock_identity(selected_identity_id))


@router.post("/mock-session", response_model=MockSession)
def select_mock_identity(
    selection: MockIdentitySelection,
    response: Response,
) -> MockSession:
    identity = find_mock_identity(selection.identity_id)
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The selected Mock identity does not exist.",
        )

    response.set_cookie(
        key=MOCK_IDENTITY_COOKIE,
        value=identity.id,
        httponly=True,
        samesite="lax",
    )
    return MockSession(selected_identity=identity)


@router.delete("/mock-session", status_code=status.HTTP_204_NO_CONTENT)
def clear_mock_identity(response: Response) -> None:
    response.delete_cookie(MOCK_IDENTITY_COOKIE, httponly=True, samesite="lax")


@router.get("/attribution-preview", response_model=AttributionPreview)
def get_attribution_preview(
    selected_identity_id: SelectedIdentityCookie = None,
) -> AttributionPreview:
    identity = require_selected_identity(selected_identity_id)
    return AttributionPreview(
        actor=identity,
        message=f"Demonstration actions use {identity.display_name} for attribution.",
    )


@router.get("/decision-records", response_model=DecisionRecordCollection)
def list_decision_records(
    request: Request,
    tag: str | None = None,
) -> DecisionRecordCollection:
    store = get_record_store(request)
    records = store.list() if tag is None else store.list_by_exact_tag(tag)
    return DecisionRecordCollection(records=records)


@router.get("/tags", response_model=TagCollection)
def list_tags(
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> TagCollection:
    require_selected_identity(selected_identity_id)
    return TagCollection(tags=get_tag_store(request).list())


@router.post(
    "/tags",
    response_model=CreatedTag,
    status_code=status.HTTP_201_CREATED,
)
def create_tag(
    payload: TagCreate,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> CreatedTag:
    require_team_member(require_selected_identity(selected_identity_id))
    try:
        return CreatedTag(name=get_tag_store(request).create(payload.name))
    except DuplicateTagError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tag with this exact name already exists.",
        ) from error


@router.get("/audit-events", response_model=AuditEventCollection)
def list_audit_events(
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> AuditEventCollection:
    require_selected_identity(selected_identity_id)
    return AuditEventCollection(events=list(get_audit_event_store(request).list()))


@router.get("/audit-events/{event_id}", response_model=AuditEvent)
def get_audit_event(
    event_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> AuditEvent:
    require_selected_identity(selected_identity_id)
    event = get_audit_event_store(request).get(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The audit event does not exist.",
        )
    return event


@router.get(
    "/decision-records/{record_id}/audit-events",
    response_model=AuditEventCollection,
)
def list_decision_record_audit_events(
    record_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> AuditEventCollection:
    require_selected_identity(selected_identity_id)
    record = get_record_store(request).get(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The decision record does not exist.",
        )
    return AuditEventCollection(
        events=list(
            get_audit_event_store(request).list(
                subject_type="decision_record",
                subject_id=record_id,
            )
        )
    )


@router.get("/decision-records/{record_id}", response_model=DecisionRecord)
def get_decision_record(record_id: str, request: Request) -> DecisionRecord:
    record = get_record_store(request).get(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The decision record does not exist.",
        )
    return record


@router.post(
    "/decision-records/{record_id}/comments",
    response_model=DecisionComment,
    status_code=status.HTTP_201_CREATED,
)
def add_decision_comment(
    record_id: str,
    payload: DecisionCommentCreate,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionComment:
    actor = require_team_member(require_selected_identity(selected_identity_id))
    try:
        return get_record_store(request).add_comment(
            record_id,
            payload.content,
            actor,
        )
    except RecordNotFoundError as error:
        raise_record_action_error(error)


@router.delete(
    "/decision-records/{record_id}/comments/{comment_id}",
    response_model=DecisionComment,
)
def delete_decision_comment(
    record_id: str,
    comment_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionComment:
    actor = require_team_member(require_selected_identity(selected_identity_id))
    try:
        return get_record_store(request).soft_delete_comment(
            record_id,
            comment_id,
            actor,
            record_change=lambda record, before, after: record_comment_deletion(
                request,
                actor,
                record,
                before,
                after,
            ),
        )
    except CommentNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The comment does not exist.",
        ) from error
    except (RecordNotFoundError, PermissionError, RecordActionError) as error:
        raise_record_action_error(error)


def raise_record_action_error(error: Exception) -> None:
    if isinstance(error, RecordNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The decision record does not exist.",
        ) from error
    if isinstance(error, PermissionError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    if isinstance(error, RecordActionError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    raise error


@router.post(
    "/decision-records",
    response_model=DecisionRecord,
    status_code=status.HTTP_201_CREATED,
)
def create_decision_record(
    payload: DecisionRecordCreate,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    author = require_selected_identity(selected_identity_id)
    try:
        record = get_record_store(request).create(payload, author)
        get_tag_store(request).ensure(record.tags)
        return record
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.put("/decision-records/{record_id}", response_model=DecisionRecord)
def update_decision_record(
    record_id: str,
    payload: DecisionRecordUpdate,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    author = require_selected_identity(selected_identity_id)
    try:
        with governance_lock:
            record = get_record_store(request).update(
                record_id,
                payload,
                author,
                record_change=lambda before, after: record_lifecycle_transition(
                    request,
                    author,
                    before,
                    after,
                    changed_fields=tuple(
                        payload.model_dump(exclude_unset=True).keys()
                    ),
                ),
            )
        get_tag_store(request).ensure(record.tags)
        return record
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except (RecordNotFoundError, PermissionError, RecordActionError) as error:
        raise_record_action_error(error)


@router.post(
    "/decision-records/{record_id}/decision",
    response_model=DecisionRecord,
)
def decide_decision_record(
    record_id: str,
    decision: DecisionSubmission,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    actor = require_selected_identity(selected_identity_id)
    with governance_lock:
        if not is_designated_approver(actor):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only a designated approver may decide a Proposed record.",
            )
        try:
            return get_record_store(request).decide(
                record_id,
                decision.outcome,
                record_change=lambda before, after, related_transition: (
                    record_lifecycle_transition(
                        request,
                        actor,
                        before,
                        after,
                        related_transition=related_transition,
                    )
                ),
            )
        except (RecordNotFoundError, PermissionError, RecordActionError) as error:
            raise_record_action_error(error)


@router.post(
    "/decision-records/{record_id}/replacements",
    response_model=DecisionRecord,
    status_code=status.HTTP_201_CREATED,
)
def create_replacement_version(
    record_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    administrator = require_selected_identity(selected_identity_id)
    require_administrator(administrator)
    try:
        with governance_lock:
            record_store = get_record_store(request)
            original = record_store.get(record_id)

            def record_replacement_history(
                replacement: DecisionRecord,
            ) -> None:
                if original is None:
                    raise RuntimeError(
                        "Replacement history requires an existing original record."
                    )
                previous_replacements = original.replacement_record_ids
                get_audit_event_store(request).record_many(
                    (
                        create_audit_event(
                            event_type=AuditEventType.LIFECYCLE_TRANSITIONED,
                            actor=administrator,
                            subject_type="decision_record",
                            subject_id=replacement.id,
                            changes=(
                                AuditChange(
                                    field="status",
                                    before=None,
                                    after="Draft",
                                ),
                                AuditChange(
                                    field="replaces_record_id",
                                    before=None,
                                    after=record_id,
                                ),
                            ),
                        ),
                        create_audit_event(
                            event_type=AuditEventType.RECORD_UPDATED,
                            actor=administrator,
                            subject_type="decision_record",
                            subject_id=record_id,
                            changes=(
                                AuditChange(
                                    field="replacement_record_ids",
                                    before=json.dumps(previous_replacements),
                                    after=json.dumps(
                                        [*previous_replacements, replacement.id]
                                    ),
                                ),
                            ),
                        ),
                    )
                )

            return record_store.create_replacement(
                record_id,
                administrator,
                record_change=record_replacement_history,
            )
    except (RecordNotFoundError, PermissionError, RecordActionError) as error:
        raise_record_action_error(error)


@router.post(
    "/decision-records/{record_id}/abandon",
    response_model=DecisionRecord,
)
def abandon_replacement_version(
    record_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    administrator = require_selected_identity(selected_identity_id)
    require_administrator(administrator)
    try:
        with governance_lock:
            return get_record_store(request).abandon_replacement(
                record_id,
                administrator,
                record_change=lambda before, after: get_audit_event_store(
                    request
                ).record(
                    event_type=AuditEventType.REPLACEMENT_DRAFT_ABANDONED,
                    actor=administrator,
                    subject_type="decision_record",
                    subject_id=record_id,
                    changes=(
                        AuditChange(
                            field="abandoned",
                            before=before.abandoned,
                            after=after.abandoned,
                        ),
                    ),
                ),
            )
    except (RecordNotFoundError, PermissionError, RecordActionError) as error:
        raise_record_action_error(error)


def change_record_archival(
    record_id: str,
    request: Request,
    selected_identity_id: str | None,
    *,
    archived: bool,
) -> DecisionRecord:
    administrator = require_administrator(require_selected_identity(selected_identity_id))
    try:
        with governance_lock:
            return get_record_store(request).set_archived(
                record_id,
                administrator,
                archived=archived,
                record_change=lambda before, after: get_audit_event_store(
                    request
                ).record(
                    event_type=(
                        AuditEventType.RECORD_ARCHIVED
                        if archived
                        else AuditEventType.RECORD_RESTORED
                    ),
                    actor=administrator,
                    subject_type="decision_record",
                    subject_id=record_id,
                    changes=(
                        AuditChange(
                            field="archived",
                            before=before.archived,
                            after=after.archived,
                        ),
                    ),
                ),
            )
    except (RecordNotFoundError, PermissionError, RecordActionError) as error:
        raise_record_action_error(error)


@router.post("/decision-records/{record_id}/archive", response_model=DecisionRecord)
def archive_decision_record(
    record_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    return change_record_archival(record_id, request, selected_identity_id, archived=True)


@router.post("/decision-records/{record_id}/restore", response_model=DecisionRecord)
def restore_decision_record(
    record_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    return change_record_archival(record_id, request, selected_identity_id, archived=False)


@router.post(
    "/decision-records/{record_id}/owner",
    response_model=DecisionRecord,
)
def transfer_decision_record_owner(
    record_id: str,
    transfer: OwnershipTransfer,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    actor = require_selected_identity(selected_identity_id)
    try:
        with governance_lock:
            return get_record_store(request).transfer_owner(
                record_id,
                transfer.owner_id,
                actor,
                record_change=lambda before, after: get_audit_event_store(
                    request
                ).record(
                    event_type=AuditEventType.OWNERSHIP_TRANSFERRED,
                    actor=actor,
                    subject_type="decision_record",
                    subject_id=record_id,
                    changes=(
                        AuditChange(
                            field="owner",
                            before=before.owner.id,
                            after=after.owner.id,
                        ),
                    ),
                ),
            )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    except (RecordNotFoundError, PermissionError, RecordActionError) as error:
        raise_record_action_error(error)


@router.post(
    "/decision-records/{record_id}/submit",
    response_model=DecisionRecord,
)
def submit_decision_record(
    record_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> DecisionRecord:
    author = require_selected_identity(selected_identity_id)
    try:
        with governance_lock:
            return get_record_store(request).submit(
                record_id,
                author,
                has_designated_approver=bool(designated_approver_snapshot()),
            )
    except DraftSubmissionError as error:
        detail: dict[str, object] = {
            "message": "The Draft cannot be submitted.",
            "missing_fields": error.missing_fields,
        }
        if error.approver_required:
            detail["approver"] = (
                "At least one designated approver must be designated before "
                "submitting this Draft."
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        ) from error
    except (RecordNotFoundError, PermissionError, RecordActionError) as error:
        raise_record_action_error(error)


@router.get("/governance/permissions", response_model=GovernancePermissions)
def get_governance_permissions(
    selected_identity_id: SelectedIdentityCookie = None,
) -> GovernancePermissions:
    identity = require_selected_identity(selected_identity_id)
    # One locked snapshot keeps the flag and permission list consistent.
    with governance_lock:
        return GovernancePermissions(
            identity=identity,
            designated_approver=is_designated_approver(identity),
            permissions=sorted(role_permissions(identity)),
        )


@router.get("/approvers", response_model=ApproverList)
def list_designated_approvers() -> ApproverList:
    designated_ids = designated_approver_snapshot()
    approvers = [
        identity for identity in MOCK_IDENTITIES if identity.id in designated_ids
    ]
    return ApproverList(approvers=approvers)


@router.post("/approvers", response_model=ApproverList)
def designate_approver(
    designation: ApproverDesignation,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> ApproverList:
    administrator = require_selected_identity(selected_identity_id)
    require_administrator(administrator)
    identity = find_mock_identity(designation.identity_id)
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The selected Mock identity does not exist.",
        )

    change_approver_designation(
        identity.id,
        designated=True,
        record_change=lambda: get_audit_event_store(request).record(
            event_type=AuditEventType.APPROVER_DESIGNATION_CHANGED,
            actor=administrator,
            subject_type="mock_identity",
            subject_id=identity.id,
            changes=(
                AuditChange(
                    field="designated_approver",
                    before=False,
                    after=True,
                ),
            ),
        ),
    )
    return list_designated_approvers()


@router.delete("/approvers/{identity_id}", response_model=ApproverList)
def remove_approver(
    identity_id: str,
    request: Request,
    selected_identity_id: SelectedIdentityCookie = None,
) -> ApproverList:
    administrator = require_selected_identity(selected_identity_id)
    require_administrator(administrator)
    if find_mock_identity(identity_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The selected Mock identity does not exist.",
        )

    change_approver_designation(
        identity_id,
        designated=False,
        record_change=lambda: get_audit_event_store(request).record(
            event_type=AuditEventType.APPROVER_DESIGNATION_CHANGED,
            actor=administrator,
            subject_type="mock_identity",
            subject_id=identity_id,
            changes=(
                AuditChange(
                    field="designated_approver",
                    before=True,
                    after=False,
                ),
            ),
        ),
    )
    return list_designated_approvers()
