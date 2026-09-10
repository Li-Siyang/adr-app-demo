from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, Response, status
from pydantic import BaseModel

from app.identities import MOCK_IDENTITIES, MockIdentity, find_mock_identity

MOCK_IDENTITY_COOKIE = "adr_mock_identity"

router = APIRouter(prefix="/api")


class MockIdentitySelection(BaseModel):
    identity_id: str


class MockSession(BaseModel):
    selected_identity: MockIdentity | None


class AttributionPreview(BaseModel):
    actor: MockIdentity
    message: str


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


@router.get("/mock-identities", response_model=list[MockIdentity])
def list_mock_identities() -> tuple[MockIdentity, ...]:
    return MOCK_IDENTITIES


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

