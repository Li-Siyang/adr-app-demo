from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.audit import AuditChange, AuditEventStore, AuditEventType
from app.governance import designated_approver_ids
from app.identities import MOCK_IDENTITIES
from app.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        yield test_client
    designated_approver_ids.clear()


def test_supports_every_approved_governed_event_category() -> None:
    assert set(AuditEventType) == {
        AuditEventType.RECORD_UPDATED,
        AuditEventType.USER_ROLE_CHANGED,
        AuditEventType.APPROVER_DESIGNATION_CHANGED,
        AuditEventType.LIFECYCLE_TRANSITIONED,
        AuditEventType.REPLACEMENT_DRAFT_ABANDONED,
        AuditEventType.RECORD_ARCHIVED,
        AuditEventType.RECORD_RESTORED,
        AuditEventType.OWNERSHIP_TRANSFERRED,
        AuditEventType.COMMENT_DELETED,
    }


def test_records_immutable_attributed_change_history_without_expiry(
    tmp_path: Path,
) -> None:
    store = AuditEventStore(tmp_path / "audit.sqlite3")
    event = store.record(
        event_type=AuditEventType.OWNERSHIP_TRANSFERRED,
        actor=MOCK_IDENTITIES[0],
        subject_type="decision_record",
        subject_id="decision-1",
        changes=(
            AuditChange(field="owner_id", before="maya-member", after="zoe-admin"),
        ),
    )

    assert store.get(event.id) == event
    assert store.list(subject_type="decision_record", subject_id="decision-1") == (
        event,
    )
    assert event.actor.id == "maya-member"
    assert event.occurred_at.tzinfo is not None
    assert event.changes[0].field == "owner_id"
    assert not hasattr(event, "expires_at")
    assert not hasattr(store, "delete")

    with pytest.raises(ValidationError):
        event.subject_id = "decision-2"
    with pytest.raises(ValidationError):
        event.expires_at = "2027-09-11"
    with pytest.raises(ValidationError):
        event.changes[0].after = "arun-approver"
    with pytest.raises(ValidationError):
        event.actor.display_name = "Changed"


def test_rejects_empty_or_no_op_audit_changes(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        AuditChange(field="", before=False, after=True)
    with pytest.raises(ValidationError):
        AuditChange(field="status", before="Draft", after="Draft")

    with pytest.raises(ValidationError):
        AuditEventStore(tmp_path / "audit.sqlite3").record(
            event_type=AuditEventType.RECORD_ARCHIVED,
            actor=MOCK_IDENTITIES[0],
            subject_type="decision_record",
            subject_id="decision-1",
            changes=(),
        )


def test_append_only_store_preserves_all_concurrent_events(tmp_path: Path) -> None:
    store = AuditEventStore(tmp_path / "audit.sqlite3")

    def record_event(index: int) -> None:
        store.record(
            event_type=AuditEventType.LIFECYCLE_TRANSITIONED,
            actor=MOCK_IDENTITIES[0],
            subject_type="decision_record",
            subject_id=f"decision-{index}",
            changes=(AuditChange(field="status", before="Draft", after="Proposed"),),
        )

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(record_event, range(20)))

    assert len(store.list()) == 20


def test_audit_events_survive_store_recreation(tmp_path: Path) -> None:
    database_path = tmp_path / "audit.sqlite3"
    first_store = AuditEventStore(database_path)
    event = first_store.record(
        event_type=AuditEventType.RECORD_ARCHIVED,
        actor=MOCK_IDENTITIES[2],
        subject_type="decision_record",
        subject_id="decision-1",
        changes=(AuditChange(field="archived", before=False, after=True),),
    )

    recreated_store = AuditEventStore(database_path)

    assert recreated_store.get(event.id) == event
    assert recreated_store.list() == (event,)


def test_approver_changes_create_attributed_audit_events(
    client: TestClient,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})

    designated = client.post(
        "/api/approvers",
        json={"identity_id": "arun-approver"},
    )
    removed = client.delete("/api/approvers/arun-approver")

    assert designated.status_code == 200
    assert removed.status_code == 200
    events = client.get("/api/audit-events").json()["events"]
    assert len(events) == 2
    assert [event["actor"]["id"] for event in events] == ["zoe-admin", "zoe-admin"]
    assert [event["subject_id"] for event in events] == [
        "arun-approver",
        "arun-approver",
    ]
    assert [event["changes"][0] for event in events] == [
        {"field": "designated_approver", "before": False, "after": True},
        {"field": "designated_approver", "before": True, "after": False},
    ]
    assert client.get(f"/api/audit-events/{events[0]['id']}").json() == events[0]


def test_denied_and_no_op_approver_requests_do_not_create_audit_events(
    client: TestClient,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    denied = client.post("/api/approvers", json={"identity_id": "arun-approver"})

    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    first = client.post("/api/approvers", json={"identity_id": "arun-approver"})
    duplicate = client.post("/api/approvers", json={"identity_id": "arun-approver"})

    assert denied.status_code == 403
    assert first.status_code == 200
    assert duplicate.status_code == 200
    assert len(client.get("/api/audit-events").json()["events"]) == 1


def test_concurrent_approver_updates_emit_one_event_per_change(
    client: TestClient,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})

    def designate() -> int:
        return client.post(
            "/api/approvers",
            json={"identity_id": "arun-approver"},
        ).status_code

    with ThreadPoolExecutor(max_workers=4) as executor:
        designation_statuses = list(executor.map(lambda _: designate(), range(20)))

    def remove() -> int:
        return client.delete("/api/approvers/arun-approver").status_code

    with ThreadPoolExecutor(max_workers=4) as executor:
        removal_statuses = list(executor.map(lambda _: remove(), range(20)))

    assert designation_statuses == [200] * 20
    assert removal_statuses == [200] * 20
    assert client.get("/api/approvers").json() == {"approvers": []}
    events = client.get("/api/audit-events").json()["events"]
    assert len(events) == 2
    assert [event["changes"][0]["after"] for event in events] == [True, False]


def test_decision_record_history_filters_events_and_rejects_unknown_record(
    client: TestClient,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    created = client.post(
        "/api/decision-records",
        json={
            "title": "Audit history",
            "context": "History must be queryable.",
            "decision": "Use subject filtering.",
            "rationale": "Unrelated events must not be returned.",
            "alternatives_considered": "Return every event.",
            "consequences": "History stays focused.",
            "owner_id": "maya-member",
            "decision_date": "2026-09-11",
            "tags": ["audit"],
        },
    ).json()
    store = client.app.state.audit_event_store
    expected = store.record(
        event_type=AuditEventType.OWNERSHIP_TRANSFERRED,
        actor=MOCK_IDENTITIES[0],
        subject_type="decision_record",
        subject_id=created["id"],
        changes=(
            AuditChange(
                field="owner_id",
                before="maya-member",
                after="zoe-admin",
            ),
        ),
    )
    store.record(
        event_type=AuditEventType.COMMENT_DELETED,
        actor=MOCK_IDENTITIES[0],
        subject_type="decision_record",
        subject_id="another-record",
        changes=(AuditChange(field="content", before="text", after="[deleted]"),),
    )

    response = client.get(f"/api/decision-records/{created['id']}/audit-events")

    assert response.status_code == 200
    assert [event["id"] for event in response.json()["events"]] == [expected.id]
    assert (
        client.get("/api/decision-records/not-configured/audit-events").status_code
        == 404
    )


def test_record_edits_are_retained_as_attributed_immutable_history(
    client: TestClient,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    created = client.post(
        "/api/decision-records",
        json={
            "title": "Original title",
            "context": "History describes later edits.",
            "decision": "Keep each revision.",
            "rationale": "The event store is append-only.",
            "alternatives_considered": "Overwrite the earlier value.",
            "consequences": "Readers can inspect authorship.",
            "owner_id": "maya-member",
            "decision_date": "2026-09-11",
            "tags": ["history"],
        },
    ).json()

    updated = client.put(
        f"/api/decision-records/{created['id']}",
        json={"title": "Revised title"},
    )
    no_op = client.put(
        f"/api/decision-records/{created['id']}",
        json={"title": "Revised title"},
    )
    history_response = client.get(
        f"/api/decision-records/{created['id']}/audit-events"
    )

    assert updated.status_code == 200
    assert no_op.status_code == 200
    assert history_response.status_code == 200
    events = history_response.json()["events"]
    assert len(events) == 1
    assert events[0]["event_type"] == "record_updated"
    assert events[0]["actor"]["id"] == "maya-member"
    assert events[0]["occurred_at"]
    assert events[0]["changes"] == [
        {"field": "title", "before": "Original title", "after": "Revised title"}
    ]
    assert (
        client.delete(f"/api/audit-events/{events[0]['id']}").status_code == 405
    )


def test_replacement_link_change_is_retained_for_both_versions(
    client: TestClient,
) -> None:
    payload = {
        "title": "Original decision",
        "context": "The history view needs a linked version.",
        "decision": "Keep each version independently navigable.",
        "rationale": "Each record owns its immutable history.",
        "alternatives_considered": "Store the link only on the replacement.",
        "consequences": "Readers can follow the relationship in both directions.",
        "owner_id": "maya-member",
        "decision_date": "2026-09-11",
        "tags": ["history"],
    }
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    assert client.post(
        "/api/approvers",
        json={"identity_id": "arun-approver"},
    ).status_code == 200
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    original = client.post("/api/decision-records", json=payload).json()
    assert client.post(
        f"/api/decision-records/{original['id']}/submit"
    ).status_code == 200
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})
    assert client.post(
        f"/api/decision-records/{original['id']}/decision",
        json={"outcome": "Accepted"},
    ).status_code == 200
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    replacement = client.post(
        f"/api/decision-records/{original['id']}/replacements"
    ).json()

    original_history = client.get(
        f"/api/decision-records/{original['id']}/audit-events"
    ).json()["events"]
    replacement_history = client.get(
        f"/api/decision-records/{replacement['id']}/audit-events"
    ).json()["events"]
    link_change = next(
        event
        for event in original_history
        if any(
            change["field"] == "replacement_record_ids"
            for change in event["changes"]
        )
    )

    assert replacement["replaces_record_id"] == original["id"]
    assert client.get(
        f"/api/decision-records/{original['id']}"
    ).json()["replacement_record_ids"] == [replacement["id"]]
    assert link_change["actor"]["id"] == "zoe-admin"
    assert link_change["changes"] == [
        {
            "field": "replacement_record_ids",
            "before": "[]",
            "after": f'["{replacement["id"]}"]',
        }
    ]
    assert replacement_history[-1]["subject_id"] == replacement["id"]
    assert replacement_history[-1]["changes"] == [
        {"field": "status", "before": None, "after": "Draft"},
        {
            "field": "replaces_record_id",
            "before": None,
            "after": original["id"],
        },
    ]


def test_unknown_audit_event_returns_not_found(client: TestClient) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    response = client.get("/api/audit-events/not-configured")

    assert response.status_code == 404
    assert response.json()["detail"] == "The audit event does not exist."


def test_audit_history_requires_selected_mock_identity(client: TestClient) -> None:
    response = client.get("/api/audit-events")

    assert response.status_code == 400
    assert response.json()["detail"] == "Choose a Mock identity before continuing."
