from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.audit import AuditChange, AuditEvent, AuditEventStore, AuditEventType
from app.governance import (
    change_approver_designation,
    designated_approver_snapshot,
    is_administrator,
    is_designated_approver,
    role_permissions,
)
from app.identities import MOCK_IDENTITIES, MockIdentity, find_mock_identity
from app.records import DecisionRecord, DecisionRecordCreate, DecisionRecordStore

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


class ApproverList(BaseModel):
    approvers: list[MockIdentity]


class GovernancePermissions(BaseModel):
    identity: MockIdentity
    designated_approver: bool
    permissions: list[str]


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
        return get_record_store(request).create(payload, author)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.get("/governance/permissions", response_model=GovernancePermissions)
def get_governance_permissions(
    selected_identity_id: SelectedIdentityCookie = None,
) -> GovernancePermissions:
    identity = require_selected_identity(selected_identity_id)
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