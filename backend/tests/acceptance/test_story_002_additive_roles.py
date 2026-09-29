"""Validation-Agent-owned acceptance tests for STORY-002 (TS-002).

Expected behavior is derived from the approved Requirement Definition and
TEST-001 Test Design, not from the implementation.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.main import create_app

ADMINISTRATOR = "zoe-admin"
ORDINARY_MEMBER = "maya-member"
APPROVER_CANDIDATE = "arun-approver"
ADMIN_AND_APPROVER = "lee-admin-approver"
RECORD_FIELDS = {
    "title": "Define the deployment boundary",
    "context": "The demonstration needs a clear operational boundary.",
    "decision": "Run one application process.",
    "rationale": "Governance state is process-local.",
    "alternatives_considered": "Run multiple workers.",
    "consequences": "Horizontal scaling is out of scope.",
    "owner_id": ORDINARY_MEMBER,
    "decision_date": "2026-09-28",
    "tags": ["operations"],
}

ADMINISTRATOR_ONLY_PERMISSIONS = (
    "administer_approvers",
    "archive_records",
    "restore_records",
    "create_replacements",
    "abandon_replacements",
)

APPROVER_ONLY_PERMISSIONS = ("accept_proposals", "reject_proposals")


@pytest.fixture
def client() -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app()) as test_client:
        yield test_client
    designated_approver_ids.clear()


def select(client: TestClient, identity_id: str) -> None:
    assert (
        client.post("/api/mock-session", json={"identity_id": identity_id}).status_code
        == 200
    )


def approver_ids(client: TestClient) -> list[str]:
    return [item["id"] for item in client.get("/api/approvers").json()["approvers"]]


def permissions(client: TestClient) -> list[str]:
    response = client.get("/api/governance/permissions")
    assert response.status_code == 200
    return response.json()["permissions"]


def create_proposed(
    client: TestClient, author_id: str, approver_id: str
) -> dict[str, object]:
    select(client, ADMINISTRATOR)
    designated = client.post(
        "/api/approvers", json={"identity_id": approver_id}
    )
    assert designated.status_code == 200

    select(client, author_id)
    created = client.post("/api/decision-records", json=RECORD_FIELDS)
    assert created.status_code == 201
    submitted = client.post(
        f"/api/decision-records/{created.json()['id']}/submit"
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "Proposed"
    return submitted.json()


def test_tc_002_01_only_administrators_change_approver_designations(
    client: TestClient,
) -> None:
    """TC-002-01 / AC-003: administrator-only approver administration."""
    select(client, ADMINISTRATOR)
    assert (
        client.post(
            "/api/approvers", json={"identity_id": APPROVER_CANDIDATE}
        ).status_code
        == 200
    )
    assert approver_ids(client) == [APPROVER_CANDIDATE]

    select(client, ORDINARY_MEMBER)
    assert (
        client.post("/api/approvers", json={"identity_id": ORDINARY_MEMBER}).status_code
        == 403
    )
    assert client.delete(f"/api/approvers/{APPROVER_CANDIDATE}").status_code == 403
    assert approver_ids(client) == [APPROVER_CANDIDATE]

    select(client, ADMINISTRATOR)
    assert client.delete(f"/api/approvers/{APPROVER_CANDIDATE}").status_code == 200
    assert approver_ids(client) == []


def test_tc_002_01_approver_role_alone_cannot_administer_approvers(
    client: TestClient,
) -> None:
    """TC-002-01 / CR-BR-001: approver authority is not administrator authority."""
    select(client, ADMINISTRATOR)
    client.post("/api/approvers", json={"identity_id": APPROVER_CANDIDATE})

    select(client, APPROVER_CANDIDATE)
    assert (
        client.post("/api/approvers", json={"identity_id": ORDINARY_MEMBER}).status_code
        == 403
    )
    assert approver_ids(client) == [APPROVER_CANDIDATE]


@pytest.mark.parametrize("permission", ADMINISTRATOR_ONLY_PERMISSIONS)
def test_tc_002_02_non_administrator_holds_no_governed_permission(
    client: TestClient, permission: str
) -> None:
    """TC-002-02 / AC-003: governed actions are withheld from non-administrators."""
    select(client, ADMINISTRATOR)
    client.post("/api/approvers", json={"identity_id": APPROVER_CANDIDATE})

    select(client, APPROVER_CANDIDATE)
    assert permission not in permissions(client)

    select(client, ORDINARY_MEMBER)
    assert permission not in permissions(client)


@pytest.mark.parametrize("permission", APPROVER_ONLY_PERMISSIONS)
def test_tc_002_03_non_approver_holds_no_decision_permission(
    client: TestClient, permission: str
) -> None:
    """TC-002-03 / AC-006: only designated approvers may decide proposals."""
    select(client, ORDINARY_MEMBER)
    assert permission not in permissions(client)

    select(client, ADMINISTRATOR)
    assert permission not in permissions(client)


def test_tc_002_03_non_approvers_cannot_accept_or_reject_proposals(
    client: TestClient,
) -> None:
    """TC-002-03 / AC-006: denied decisions leave Proposed records unchanged."""
    proposed = create_proposed(client, ORDINARY_MEMBER, APPROVER_CANDIDATE)

    for identity_id in (ORDINARY_MEMBER, ADMINISTRATOR):
        select(client, identity_id)
        for outcome in ("Accepted", "Rejected"):
            response = client.post(
                f"/api/decision-records/{proposed['id']}/decision",
                json={"outcome": outcome},
            )
            assert response.status_code == 403
            assert client.get(
                f"/api/decision-records/{proposed['id']}"
            ).json() == proposed


def test_tc_002_04_designated_author_approver_keeps_decision_authority(
    client: TestClient,
) -> None:
    """TC-002-04 / AC-007: designation, not authorship, grants decision authority."""
    select(client, ADMINISTRATOR)
    client.post("/api/approvers", json={"identity_id": ORDINARY_MEMBER})

    select(client, ORDINARY_MEMBER)
    granted = permissions(client)
    assert client.get("/api/governance/permissions").json()["designated_approver"]
    for permission in APPROVER_ONLY_PERMISSIONS:
        assert permission in granted


@pytest.mark.parametrize("outcome", ["Accepted", "Rejected"])
def test_tc_002_04_designated_author_can_decide_own_proposal(
    client: TestClient, outcome: str
) -> None:
    """TC-002-04 / AC-007: a designated author may choose either outcome."""
    proposed = create_proposed(client, APPROVER_CANDIDATE, APPROVER_CANDIDATE)

    select(client, APPROVER_CANDIDATE)
    response = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": outcome},
    )

    assert response.status_code == 200
    assert response.json()["status"] == outcome


def test_tc_002_05_roles_are_additive_and_never_revoke_each_other(
    client: TestClient,
) -> None:
    """TC-002-05 / AC-023: held roles combine without mutual revocation."""
    select(client, ADMINISTRATOR)
    client.post("/api/approvers", json={"identity_id": ADMIN_AND_APPROVER})

    select(client, ADMIN_AND_APPROVER)
    combined = set(permissions(client))
    assert set(ADMINISTRATOR_ONLY_PERMISSIONS).issubset(combined)
    assert set(APPROVER_ONLY_PERMISSIONS).issubset(combined)

    select(client, ORDINARY_MEMBER)
    ordinary = set(permissions(client))
    assert ordinary.isdisjoint(ADMINISTRATOR_ONLY_PERMISSIONS)
    assert ordinary.isdisjoint(APPROVER_ONLY_PERMISSIONS)
    assert ordinary.issubset(combined)

    proposed = create_proposed(client, ADMIN_AND_APPROVER, ADMIN_AND_APPROVER)
    select(client, ADMIN_AND_APPROVER)
    decided = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert decided.status_code == 200
    assert decided.json()["status"] == "Accepted"


def test_tc_002_05_undesignated_administrator_cannot_decide(
    client: TestClient,
) -> None:
    """TC-002-05 / AC-023: an ungranted action stays denied for every held role."""
    select(client, ADMIN_AND_APPROVER)
    granted = set(permissions(client))

    assert set(ADMINISTRATOR_ONLY_PERMISSIONS).issubset(granted)
    assert granted.isdisjoint(APPROVER_ONLY_PERMISSIONS)
    proposed = create_proposed(client, ORDINARY_MEMBER, APPROVER_CANDIDATE)

    select(client, ADMIN_AND_APPROVER)
    response = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert response.status_code == 403
    assert client.get(f"/api/decision-records/{proposed['id']}").json() == proposed


def test_governed_administration_requires_a_selected_mock_identity(
    client: TestClient,
) -> None:
    """CR-BR-001: approver administration is unavailable without an actor."""
    response = client.post("/api/approvers", json={"identity_id": APPROVER_CANDIDATE})

    assert response.status_code == 400
    assert approver_ids(client) == []


def test_unknown_identity_cannot_be_designated_as_approver(
    client: TestClient,
) -> None:
    """CR-BR-001: designations are limited to configured Mock identities."""
    select(client, ADMINISTRATOR)

    response = client.post("/api/approvers", json={"identity_id": "not-configured"})

    assert response.status_code == 404
    assert approver_ids(client) == []
