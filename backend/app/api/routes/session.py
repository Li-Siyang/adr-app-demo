import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentMember

router = APIRouter(tags=["session"])


class CurrentMemberResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str


@router.get("/me", response_model=CurrentMemberResponse)
def read_current_member(member: CurrentMember) -> CurrentMemberResponse:
    """Return the authenticated team member behind the current request."""
    return CurrentMemberResponse(
        id=member.id, email=member.email, display_name=member.display_name
    )
