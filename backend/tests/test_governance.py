from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app()) as test_client:
        yield test_client
    designated_approver_ids.clear()


def select_identity(client: TestClient, identity_id: str) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": identity_id},
    )
    assert response.status_code == 200


def test_only_administrator_can_designate_and_remove_approvers(
    client: TestClient,
) -> None:
    select_identity(client, "maya-member")
    denied = client.post("/api/approvers", json={"identity_id": "arun-approver"})
    assert denied.status_code == 403
    assert client.get("/api/approvers").json() == {"approvers": []}

    select_identity(client, "zoe-admin")
    designated = client.post(
        "/api/approvers",
        json={"identity_id": "arun-approver"},
    )
    assert designated.status_code == 200
    assert [item["id"] for item in designated.json()["approvers"]] == [
        "arun-approver"
    ]

    removed = client.delete("/api/approvers/arun-approver")
    assert removed.status_code == 200
    assert removed.json() == {"approvers": []}


def test_approver_can_be_designated_and_removed_by_an_administrator(
    client: TestClient,
) -> None:
    select_identity(client, "zoe-admin")
    client.post("/api/approvers", json={"identity_id": "maya-member"})

    select_identity(client, "maya-member")
    permissions = client.get("/api/governance/permissions")
    assert permissions.status_code == 200
    assert permissions.json()["designated_approver"] is True
    assert "accept_proposals" in permissions.json()["permissions"]
    assert "reject_proposals" in permissions.json()["permissions"]
    assert "administer_approvers" not in permissions.json()["permissions"]


def test_additive_administrator_and_approver_permissions_are_preserved(
    client: TestClient,
) -> None:
    select_identity(client, "lee-admin-approver")
    client.post("/api/approvers", json={"identity_id": "lee-admin-approver"})

    permissions = client.get("/api/governance/permissions").json()
    assert permissions["designated_approver"] is True
    assert {
        "accept_proposals",
        "reject_proposals",
        "administer_approvers",
        "archive_records",
        "restore_records",
        "create_replacements",
        "abandon_replacements",
    }.issubset(permissions["permissions"])


def test_non_approvers_cannot_decide_and_admins_can_manage_replacements(
    client: TestClient,
) -> None:
    select_identity(client, "maya-member")
    ordinary_permissions = client.get("/api/governance/permissions").json()
    assert ordinary_permissions["designated_approver"] is False
    assert "accept_proposals" not in ordinary_permissions["permissions"]
    assert "create_replacements" not in ordinary_permissions["permissions"]

    select_identity(client, "zoe-admin")
    admin_permissions = client.get("/api/governance/permissions").json()
    assert "create_replacements" in admin_permissions["permissions"]
    assert "abandon_replacements" in admin_permissions["permissions"]
