from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.governance import (
    designated_approver_ids,
    governance_lock,
    is_administrator,
    is_designated_approver,
    role_permissions,
)
from app.identities import MOCK_IDENTITIES, MockIdentity, find_mock_identity
from app.records import (
    DecisionRecord,
    DecisionRecordCreate,
    DecisionRecordStore,
    DecisionRecordUpdate,
    DraftSubmissionError,
    RecordActionError,
    RecordNotFoundError,
)

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
def list_decision_records(request: Request) -> DecisionRecordCollection:
    return DecisionRecordCollection(records=get_record_store(request).list())


@router.get("/decision-records/{record_id}", response_model=DecisionRecord)
def get_decision_record(record_id: str, request: Request) -> DecisionRecord:
    record = get_record_store(request).get(record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The decision record does not exist.",
        )
    return record


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
        return get_record_store(request).create(payload, author)
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
        return get_record_store(request).update(record_id, payload, author)
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
                has_designated_approver=bool(designated_approver_ids),
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
    with governance_lock:
        approvers = [
            identity
            for identity in MOCK_IDENTITIES
            if identity.id in designated_approver_ids
        ]
        return ApproverList(approvers=approvers)


@router.post("/approvers", response_model=ApproverList)
def designate_approver(
    designation: ApproverDesignation,
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

    with governance_lock:
        designated_approver_ids.add(identity.id)
        return list_designated_approvers()


@router.delete("/approvers/{identity_id}", response_model=ApproverList)
def remove_approver(
    identity_id: str,
    selected_identity_id: SelectedIdentityCookie = None,
) -> ApproverList:
    administrator = require_selected_identity(selected_identity_id)
    require_administrator(administrator)
    if find_mock_identity(identity_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The selected Mock identity does not exist.",
        )

    with governance_lock:
        designated_approver_ids.discard(identity_id)
        return list_designated_approvers()