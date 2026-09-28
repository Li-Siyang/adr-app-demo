from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.identities import find_mock_identity
from app.main import create_app
from app.records import (
    DecisionRecordCreate,
    DecisionRecordStore,
)


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


def create(client: TestClient) -> dict:
    select(client, "maya-member")
    response = client.post(
        "/api/decision-records",
        json={
            "title": "Service boundary",
            "context": "Legacy coupling",
            "decision": "Separate modules",
            "rationale": "Independent change",
            "alternatives_considered": "Remain coupled",
            "consequences": "Two modules",
            "owner_id": "arun-approver",
            "decision_date": "2026-09-11",
            "tags": ["architecture"],
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.parametrize("status", ["Draft", "Proposed"])
@pytest.mark.parametrize(
    "actor", ["maya-member", "arun-approver", "zoe-admin", "lee-admin-approver"]
)
def test_author_owner_and_admin_transfer_without_rewriting_author_or_status(
    client: TestClient, status: str, actor: str
) -> None:
    original = create(client)
    if status == "Proposed":
        designated_approver_ids.add("arun-approver")
        assert client.post(
            f"/api/decision-records/{original['id']}/submit"
        ).status_code == 200
    select(client, actor)
    response = client.post(
        f"/api/decision-records/{original['id']}/owner",
        json={"owner_id": "zoe-admin"},
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["owner"]["id"] == "zoe-admin"
    assert updated["author"] == original["author"]
    assert updated["status"] == status
    assert client.get(f"/api/decision-records/{original['id']}").json() == updated
    events = client.get(
        f"/api/decision-records/{original['id']}/audit-events"
    ).json()["events"]
    ownership_events = [
        event for event in events if event["event_type"] == "ownership_transferred"
    ]
    assert len(ownership_events) == 1
    assert ownership_events[0]["actor"]["id"] == actor
    assert ownership_events[0]["changes"] == [
        {"field": "owner", "before": "arun-approver", "after": "zoe-admin"}
    ]


@pytest.mark.parametrize("status", ["Draft", "Proposed"])
def test_unrelated_user_cannot_transfer_in_any_status(
    client: TestClient, status: str
) -> None:
    original = create(client)
    assert client.post(
        f"/api/decision-records/{original['id']}/owner",
        json={"owner_id": "lee-admin-approver"},
    ).status_code == 200
    if status == "Proposed":
        designated_approver_ids.add("arun-approver")
        assert client.post(
            f"/api/decision-records/{original['id']}/submit"
        ).status_code == 200
    store = client.app.state.record_store
    select(client, "arun-approver")
    response = client.post(
        f"/api/decision-records/{original['id']}/owner",
        json={"owner_id": "zoe-admin"},
    )
    assert response.status_code == 403
    assert store.get(original["id"]).owner.id == "lee-admin-approver"
    events = client.get(
        f"/api/decision-records/{original['id']}/audit-events"
    ).json()["events"]
    assert len(
        [
            event
            for event in events
            if event["event_type"] == "ownership_transferred"
        ]
    ) == 1


@pytest.mark.parametrize("status", ["Accepted", "Rejected", "Superseded"])
def test_terminal_status_disallows_transfer_for_all_approved_actors(
    client: TestClient, status: str
) -> None:
    original = create(client)
    store = client.app.state.record_store
    with store._lock:
        store._records[original["id"]] = store._records[original["id"]].model_copy(
            update={"status": status}
        )
    for actor in ("maya-member", "arun-approver", "zoe-admin"):
        select(client, actor)
        response = client.post(
            f"/api/decision-records/{original['id']}/owner",
            json={"owner_id": "lee-admin-approver"},
        )
        assert response.status_code == 409
    assert (
        client.get(f"/api/decision-records/{original['id']}").json()["owner"]
        == original["owner"]
    )
    assert (
        client.get(f"/api/decision-records/{original['id']}/audit-events").json()[
            "events"
        ]
        == []
    )


def test_abandoned_draft_disallows_transfer_and_remains_retained(
    client: TestClient,
) -> None:
    original = create(client)
    store = client.app.state.record_store
    with store._lock:
        store._records[original["id"]] = store._records[original["id"]].model_copy(
            update={"abandoned": True}
        )
    for actor in ("maya-member", "arun-approver", "zoe-admin"):
        select(client, actor)
        response = client.post(
            f"/api/decision-records/{original['id']}/owner",
            json={"owner_id": "lee-admin-approver"},
        )
        assert response.status_code == 409
    retained = client.get(f"/api/decision-records/{original['id']}").json()
    assert retained["owner"] == original["owner"]
    assert retained["author"] == original["author"]
    assert retained["abandoned"] is True
    assert (
        client.get(f"/api/decision-records/{original['id']}/audit-events").json()[
            "events"
        ]
        == []
    )


def test_invalid_transfer_requests_leave_record_and_audit_unchanged(
    client: TestClient,
) -> None:
    original = create(client)
    for owner_id, expected in (
        ("not-configured", 422),
        ("arun-approver", 409),
    ):
        response = client.post(
            f"/api/decision-records/{original['id']}/owner",
            json={"owner_id": owner_id},
        )
        assert response.status_code == expected
    assert client.post(
        "/api/decision-records/not-found/owner",
        json={"owner_id": "zoe-admin"},
    ).status_code == 404
    assert client.get(f"/api/decision-records/{original['id']}").json() == original
    assert (
        client.get(f"/api/decision-records/{original['id']}/audit-events").json()[
            "events"
        ]
        == []
    )


def test_author_departure_does_not_grant_owner_or_admin_edit_permission(
    client: TestClient,
) -> None:
    original = create(client)
    # No session for the author remains selected after switching Mock identity.
    for actor in ("arun-approver", "zoe-admin"):
        select(client, actor)
        denied = client.put(
            f"/api/decision-records/{original['id']}",
            json={"title": "Unauthorised edit"},
        )
        assert denied.status_code == 403
    transferred = client.post(
        f"/api/decision-records/{original['id']}/owner",
        json={"owner_id": "zoe-admin"},
    )
    assert transferred.status_code == 200
    assert transferred.json()["author"] == original["author"]
    assert client.get(f"/api/decision-records/{original['id']}").status_code == 200
    assert client.put(
        f"/api/decision-records/{original['id']}",
        json={"title": "Still not the author"},
    ).status_code == 403


def test_audit_failure_does_not_mutate_owner() -> None:
    store = DecisionRecordStore()
    author = find_mock_identity("maya-member")
    assert author is not None
    record = store.create(
        DecisionRecordCreate(
            title="Title",
            context="Context",
            decision="Decision",
            rationale="Rationale",
            alternatives_considered="Alternative",
            consequences="Consequence",
            owner_id="arun-approver",
            decision_date="2026-09-11",
            tags=["architecture"],
        ),
        author,
    )

    def fail_audit(before: object, after: object) -> None:
        raise RuntimeError("audit storage unavailable")

    with pytest.raises(RuntimeError, match="audit storage unavailable"):
        store.transfer_owner(
            record.id, "zoe-admin", author, record_change=fail_audit
        )
    assert store.get(record.id) == record


def test_store_transfer_changes_only_owner_and_records_audit_before_commit() -> None:
    store = DecisionRecordStore()
    author = find_mock_identity("maya-member")
    assert author is not None
    original = store.create(
        DecisionRecordCreate(
            title="Title",
            context="Context",
            decision="Decision",
            rationale="Rationale",
            alternatives_considered="Alternative",
            consequences="Consequence",
            owner_id="arun-approver",
            decision_date="2026-09-11",
            tags=["architecture"],
        ),
        author,
    )
    observed = []

    def record_audit(before: object, after: object) -> None:
        observed.append((before, after))

    transferred = store.transfer_owner(
        original.id,
        "zoe-admin",
        author,
        record_change=record_audit,
    )

    assert transferred.owner.id == "zoe-admin"
    assert transferred.author == original.author
    assert transferred.status == original.status
    assert transferred.model_copy(update={"owner": original.owner}) == original
    assert observed == [(original, transferred)]
