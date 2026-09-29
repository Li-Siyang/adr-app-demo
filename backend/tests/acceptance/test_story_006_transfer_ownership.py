"""Independent API/integration coverage for STORY-006, TS-006."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.main import create_app


AUTHOR = "maya-member"
OWNER = "arun-approver"
ADMIN = "zoe-admin"
OTHER = "lee-admin-approver"


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        yield test_client
    designated_approver_ids.clear()


def select(client: TestClient, identity_id: str) -> None:
    response = client.post("/api/mock-session", json={"identity_id": identity_id})
    assert response.status_code == 200


def create_record(client: TestClient) -> dict:
    select(client, AUTHOR)
    response = client.post(
        "/api/decision-records",
        json={
            "title": "Choose a service boundary",
            "context": "Services currently share deployment concerns.",
            "decision": "Separate their deployment boundaries.",
            "rationale": "Independent releases reduce coupling.",
            "alternatives_considered": "Retain a shared deployment.",
            "consequences": "Two deployments must be maintained.",
            "owner_id": OWNER,
            "decision_date": "2026-09-28",
            "tags": ["architecture"],
        },
    )
    assert response.status_code == 201
    assert response.json()["author"]["id"] == AUTHOR
    assert response.json()["owner"]["id"] == OWNER
    return response.json()


def propose(client: TestClient, record_id: str) -> None:
    designated_approver_ids.add(OWNER)
    select(client, AUTHOR)
    response = client.post(f"/api/decision-records/{record_id}/submit")
    assert response.status_code == 200
    assert response.json()["status"] == "Proposed"


def transfer(client: TestClient, record_id: str, new_owner: str):
    return client.post(
        f"/api/decision-records/{record_id}/owner",
        json={"owner_id": new_owner},
    )


def retained(client: TestClient, record_id: str) -> dict:
    response = client.get(f"/api/decision-records/{record_id}")
    assert response.status_code == 200
    return response.json()


def events(client: TestClient, record_id: str) -> list[dict]:
    response = client.get(f"/api/decision-records/{record_id}/audit-events")
    assert response.status_code == 200
    return response.json()["events"]


@pytest.mark.parametrize("state", ["Draft", "Proposed"])
@pytest.mark.parametrize("actor", [AUTHOR, OWNER, ADMIN])
def test_tc_006_01_author_owner_admin_transfer_without_changing_author(
    client: TestClient, state: str, actor: str
) -> None:
    original = create_record(client)
    if state == "Proposed":
        propose(client, original["id"])
    select(client, actor)

    response = transfer(client, original["id"], OTHER)

    assert response.status_code == 200
    updated = response.json()
    assert updated["owner"]["id"] == OTHER
    assert updated["author"] == original["author"]
    assert updated["status"] == state
    assert retained(client, original["id"]) == updated
    audit = [
        event for event in events(client, original["id"])
        if event["event_type"] == "ownership_transferred"
    ]
    assert len(audit) == 1
    assert audit[0]["actor"]["id"] == actor
    assert audit[0]["changes"] == [
        {"field": "owner", "before": OWNER, "after": OTHER}
    ]
    assert audit[0]["occurred_at"]


@pytest.mark.parametrize("state", ["Draft", "Proposed"])
def test_tc_006_02_unrelated_user_cannot_transfer_editable_record(
    client: TestClient, state: str
) -> None:
    original = create_record(client)
    if state == "Proposed":
        propose(client, original["id"])
    # Reassign to an administrator, leaving the former owner unrelated.
    select(client, AUTHOR)
    allowed = transfer(client, original["id"], ADMIN)
    assert allowed.status_code == 200
    before = allowed.json()
    audit_before = events(client, original["id"])
    select(client, OWNER)

    denied = transfer(client, original["id"], OTHER)

    assert denied.status_code == 403
    assert retained(client, original["id"]) == before
    assert events(client, original["id"]) == audit_before


@pytest.mark.parametrize("state", ["Accepted", "Rejected", "Superseded"])
@pytest.mark.parametrize("actor", [AUTHOR, OWNER, ADMIN])
def test_tc_006_02_terminal_record_refuses_transfer(
    client: TestClient, state: str, actor: str
) -> None:
    original = create_record(client)
    propose(client, original["id"])
    if state in ("Accepted", "Rejected"):
        select(client, OWNER)
        decided = client.post(
            f"/api/decision-records/{original['id']}/decision",
            json={"outcome": state},
        )
        assert decided.status_code == 200
    else:
        # Supersession is STORY-007: construct only this approved precondition.
        store = client.app.state.record_store
        with store._lock:
            record = store._records[original["id"]]
            store._records[original["id"]] = record.model_copy(
                update={"status": "Superseded"}
            )
    before = retained(client, original["id"])
    audit_before = events(client, original["id"])
    select(client, actor)

    denied = transfer(client, original["id"], OTHER)

    assert denied.status_code == 409
    assert retained(client, original["id"]) == before
    assert events(client, original["id"]) == audit_before


@pytest.mark.parametrize("actor", [AUTHOR, OWNER, ADMIN])
def test_tc_006_02_abandoned_replacement_draft_refuses_transfer(
    client: TestClient, actor: str
) -> None:
    original = create_record(client)
    # STORY-007 supplies replacement creation/abandonment; inject the
    # approved retained Draft+Abandoned precondition, not a new workflow.
    store = client.app.state.record_store
    with store._lock:
        record = store._records[original["id"]]
        store._records[original["id"]] = record.model_copy(
            update={"abandoned": True}
        )
    before = retained(client, original["id"])
    audit_before = events(client, original["id"])
    select(client, actor)

    denied = transfer(client, original["id"], OTHER)

    assert denied.status_code == 409
    assert retained(client, original["id"]) == before
    assert events(client, original["id"]) == audit_before
    assert any(
        record["id"] == original["id"]
        for record in client.get("/api/decision-records").json()["records"]
    )


def test_tc_006_03_author_departure_preserves_only_preexisting_permissions(
    client: TestClient,
) -> None:
    original = create_record(client)
    record_id = original["id"]
    # The Mock author is no longer selected; subsequent operations use only
    # the retained owner and administrator, without a new author grant.
    for actor in (OWNER, ADMIN):
        select(client, actor)
        assert retained(client, record_id)["author"] == original["author"]
        assert client.put(
            f"/api/decision-records/{record_id}",
            json={"title": "Edit by non-author"},
        ).status_code == 403
        assert client.post(
            f"/api/decision-records/{record_id}/submit"
        ).status_code == 403
        assert retained(client, record_id)["title"] == original["title"]

    select(client, OWNER)
    first = transfer(client, record_id, OTHER)
    assert first.status_code == 200
    select(client, ADMIN)
    second = transfer(client, record_id, OWNER)
    assert second.status_code == 200
    final = retained(client, record_id)
    assert final["author"] == original["author"]
    assert final["owner"]["id"] == OWNER
    assert final["status"] == "Draft"
    select(client, OWNER)
    assert client.put(
        f"/api/decision-records/{record_id}", json={"title": "Still not author"}
    ).status_code == 403
    assert len(
        [
            event for event in events(client, record_id)
            if event["event_type"] == "ownership_transferred"
        ]
    ) == 2
