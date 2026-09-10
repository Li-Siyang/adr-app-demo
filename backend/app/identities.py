from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class Role(StrEnum):
    TEAM_MEMBER = "team-member"
    APPROVER = "approver"
    ADMINISTRATOR = "administrator"


class MockIdentity(BaseModel):
    id: str
    display_name: str
    label: str
    roles: tuple[Role, ...]
    is_mock: Literal[True] = True


MOCK_IDENTITIES: tuple[MockIdentity, ...] = (
    MockIdentity(
        id="maya-member",
        display_name="Maya Member",
        label="Maya Member (Mock User)",
        roles=(Role.TEAM_MEMBER,),
    ),
    MockIdentity(
        id="arun-approver",
        display_name="Arun Approver",
        label="Arun Approver (Mock User)",
        roles=(Role.TEAM_MEMBER, Role.APPROVER),
    ),
    MockIdentity(
        id="zoe-admin",
        display_name="Zoe Administrator",
        label="Zoe Administrator (Mock User)",
        roles=(Role.TEAM_MEMBER, Role.ADMINISTRATOR),
    ),
    MockIdentity(
        id="lee-admin-approver",
        display_name="Lee Administrator and Approver",
        label="Lee Administrator and Approver (Mock User)",
        roles=(Role.TEAM_MEMBER, Role.ADMINISTRATOR, Role.APPROVER),
    ),
)

_IDENTITIES_BY_ID = {identity.id: identity for identity in MOCK_IDENTITIES}


def find_mock_identity(identity_id: str | None) -> MockIdentity | None:
    if identity_id is None:
        return None
    return _IDENTITIES_BY_ID.get(identity_id)

