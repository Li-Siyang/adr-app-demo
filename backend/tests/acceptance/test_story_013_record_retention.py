"""Independent acceptance coverage for STORY-013, TS-013."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.identities import MOCK_IDENTITIES
from app.main import create_app

RECORD_FIELDS = {
    "title": "Retain every decision record",
    "context": "Records must remain retained in every condition.",
    "decision": "Keep record deletion unavailable.",
    "rationale": "Archival is reversible and preserves the record.",
    "alternatives_considered": "Permanently or softly delete the record.",
    "consequences": "The record remains available for permitted actions.",
    "owner_id": "maya-member",
    "decision_date": "2026-10-01",
    "tags": ["retention"],
}


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        yield test_client
    designated_approver_ids.clear()


def select(client: TestClient, identity_id: str) -> None:
    assert client.post(
        "/api/mock-session", json={"identity_id": identity_id}
    ).status_code == 200


def create_accepted(client: TestClient) -> dict:
    select(client, "maya-member")
    created = client.post("/api/decision-records", json=RECORD_FIELDS)
    assert created.status_code == 201
    assert client.post(
        f"/api/decision-records/{created.json()['id']}/submit"
    ).status_code == 200
    select(client, "arun-approver")
    accepted = client.post(
        f"/api/decision-records/{created.json()['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert accepted.status_code == 200
    return accepted.json()


@pytest.mark.parametrize(
    ("status", "archived", "abandoned", "replacement"),
    [
        pytest.param("Draft", False, False, False, id="draft"),
        pytest.param("Proposed", False, False, False, id="proposed"),
        pytest.param("Accepted", False, False, False, id="accepted"),
        pytest.param("Rejected", False, False, False, id="rejected"),
        pytest.param("Superseded", False, False, False, id="superseded"),
        pytest.param("Draft", False, False, True, id="active-replacement-draft"),
        pytest.param("Proposed", False, False, True, id="active-replacement-proposed"),
        pytest.param("Draft", False, True, True, id="abandoned-replacement"),
        pytest.param("Draft", True, False, False, id="archived"),
        pytest.param("Accepted", True, False, False, id="archived-accepted"),
        pytest.param("Draft", True, True, True, id="archived-abandoned-replacement"),
    ],
)
def test_every_identity_is_denied_record_deletion_and_record_is_retained(
    client: TestClient,
    status: str,
    archived: bool,
    abandoned: bool,
    replacement: bool,
) -> None:
    select(client, "zoe-admin")
    assert client.post(
        "/api/approvers", json={"identity_id": "arun-approver"}
    ).status_code == 200

    if replacement or status in ("Accepted", "Superseded"):
        original = create_accepted(client)
        if replacement or status == "Superseded":
            select(client, "zoe-admin")
            created = client.post(
                f"/api/decision-records/{original['id']}/replacements"
            )
            assert created.status_code == 201
            record_id = created.json()["id"]
            assert record_id in client.get(
                f"/api/decision-records/{original['id']}"
            ).json()["replacement_record_ids"]
        else:
            record_id = original["id"]
    else:
        select(client, "maya-member")
        created = client.post("/api/decision-records", json=RECORD_FIELDS)
        assert created.status_code == 201
        record_id = created.json()["id"]

    if status in ("Proposed", "Rejected", "Superseded"):
        select(
            client,
            "zoe-admin" if replacement or status == "Superseded" else "maya-member",
        )
        assert client.post(
            f"/api/decision-records/{record_id}/submit"
        ).status_code == 200
        if status in ("Rejected", "Superseded"):
            select(client, "arun-approver")
            assert client.post(
                f"/api/decision-records/{record_id}/decision",
                json={"outcome": "Accepted" if status == "Superseded" else "Rejected"},
            ).status_code == 200
            if status == "Superseded":
                record_id = original["id"]

    if abandoned:
        select(client, "zoe-admin")
        result = client.post(f"/api/decision-records/{record_id}/abandon")
        assert result.status_code == 200
        assert result.json()["abandoned"] is True
    if archived:
        select(client, "zoe-admin")
        result = client.post(f"/api/decision-records/{record_id}/archive")
        assert result.status_code == 200
        assert result.json()["archived"] is True

    path = f"/api/decision-records/{record_id}"
    retained = client.get(path).json()
    assert retained["status"] == status
    assert retained["archived"] is archived
    assert retained["abandoned"] is abandoned
    if replacement:
        assert retained["replaces_record_id"] == original["id"]
        assert record_id in client.get(
            f"/api/decision-records/{original['id']}"
        ).json()["replacement_record_ids"]
    listed = client.get("/api/decision-records").json()["records"]

    for identity in MOCK_IDENTITIES:
        select(client, identity.id)
        assert client.delete(path).status_code == 405
        assert client.put(path, json={"deleted": True}).status_code == 422
        assert client.get(path).json() == retained
        assert client.get("/api/decision-records").json()["records"] == listed

    if archived:
        select(client, "zoe-admin")
        restored = client.post(f"{path}/restore")
        assert restored.status_code == 200
        assert restored.json() == {**retained, "archived": False}
