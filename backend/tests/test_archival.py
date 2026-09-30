from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids, is_administrator
from app.identities import MOCK_IDENTITIES, MockIdentity
from app.main import create_app
from app.records import (
    DecisionRecord,
    DecisionRecordCreate,
    DecisionRecordStore,
    RecordActionError,
)


def payload() -> DecisionRecordCreate:
    return DecisionRecordCreate(
        title="Decision",
        context="Context",
        decision="Choose option A",
        rationale="Rationale",
        alternatives_considered="Option B",
        consequences="Consequences",
        owner_id="maya-member",
        decision_date="2026-09-11",
        tags=["architecture"],
    )


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        yield test_client
    designated_approver_ids.clear()


@pytest.mark.parametrize("identity", MOCK_IDENTITIES)
def test_store_archival_requires_administrator_and_valid_transition(
    identity: MockIdentity,
) -> None:
    store = DecisionRecordStore()
    record = store.create(payload(), MOCK_IDENTITIES[0])
    admin = next(person for person in MOCK_IDENTITIES if person.id == "zoe-admin")
    before = store.get(record.id)

    if not is_administrator(identity):
        with pytest.raises(PermissionError):
            store.set_archived(
                record.id, identity, archived=True, record_change=lambda *_: None
            )
        assert store.get(record.id) == before
    else:
        archived = store.set_archived(
            record.id, identity, archived=True, record_change=lambda *_: None
        )
        assert archived.status == "Draft"
        with pytest.raises(RecordActionError, match="already archived"):
            store.set_archived(
                record.id, identity, archived=True, record_change=lambda *_: None
            )
        restored = store.set_archived(
            record.id, identity, archived=False, record_change=lambda *_: None
        )
        assert restored == before
        with pytest.raises(RecordActionError, match="not archived"):
            store.set_archived(
                record.id, identity, archived=False, record_change=lambda *_: None
            )


def test_archival_does_not_commit_if_audit_fails() -> None:
    store = DecisionRecordStore()
    record = store.create(payload(), MOCK_IDENTITIES[0])
    admin = next(person for person in MOCK_IDENTITIES if person.id == "zoe-admin")

    def fail_audit(*_: DecisionRecord) -> None:
        raise OSError("audit unavailable")

    with pytest.raises(OSError, match="audit unavailable"):
        store.set_archived(record.id, admin, archived=True, record_change=fail_audit)
    assert store.get(record.id) == record

    archived = store.set_archived(
        record.id, admin, archived=True, record_change=lambda *_: None
    )
    with pytest.raises(OSError, match="audit unavailable"):
        store.set_archived(record.id, admin, archived=False, record_change=fail_audit)
    assert store.get(record.id) == archived


def test_simultaneous_archival_commits_only_one_transition() -> None:
    store = DecisionRecordStore()
    record = store.create(payload(), MOCK_IDENTITIES[0])
    admin = next(person for person in MOCK_IDENTITIES if person.id == "zoe-admin")
    changes: list[tuple[DecisionRecord, DecisionRecord]] = []

    def archive() -> bool:
        try:
            store.set_archived(
                record.id,
                admin,
                archived=True,
                record_change=lambda before, after: changes.append((before, after)),
            )
            return True
        except RecordActionError:
            return False

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: archive(), range(2)))
    assert sorted(results) == [False, True]
    assert len(changes) == 1
    assert changes[0][0].archived is False
    assert changes[0][1].archived is True


@pytest.mark.parametrize(
    "lifecycle", ["Draft", "Proposed", "Accepted", "Rejected", "Superseded"]
)
def test_archive_restore_preserves_each_lifecycle(lifecycle: str) -> None:
    store = DecisionRecordStore()
    record = store.create(payload(), MOCK_IDENTITIES[0])
    store._records[record.id] = record.model_copy(update={"status": lifecycle})
    original = store.get(record.id)
    assert original is not None
    admin = next(person for person in MOCK_IDENTITIES if person.id == "zoe-admin")

    archived = store.set_archived(
        record.id, admin, archived=True, record_change=lambda *_: None
    )
    assert archived.status == lifecycle
    assert archived.archived
    assert store.list_by_exact_tag("architecture") == [archived]
    restored = store.set_archived(
        record.id, admin, archived=False, record_change=lambda *_: None
    )
    assert restored == original


def test_api_archive_restore_preserve_state_and_emit_attributed_events(
    client: TestClient,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    created = client.post(
        "/api/decision-records", json=payload().model_dump(mode="json")
    ).json()
    path = f"/api/decision-records/{created['id']}"
    assert client.post(f"{path}/archive").status_code == 403
    assert client.post(f"{path}/restore").status_code == 403
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})

    archived = client.post(f"{path}/archive")
    assert archived.status_code == 200
    assert archived.json()["archived"] is True
    assert archived.json()["status"] == created["status"]
    assert client.get("/api/decision-records", params={"tag": "architecture"}).json()[
        "records"
    ] == [archived.json()]
    assert client.get(path).json() == archived.json()
    assert client.post(f"{path}/archive").status_code == 409
    assert client.put(path, json={"title": "Changed"}).status_code == 409
    assert client.post(f"{path}/submit").status_code == 409
    restored = client.post(f"{path}/restore")
    assert restored.status_code == 200
    assert restored.json() == created
    assert client.post(f"{path}/restore").status_code == 409
    events = client.get(f"{path}/audit-events").json()["events"]
    assert [event["event_type"] for event in events] == [
        "record_archived", "record_restored"
    ]
    assert [event["changes"][0] for event in events] == [
        {"field": "archived", "before": False, "after": True},
        {"field": "archived", "before": True, "after": False},
    ]
    assert all(event["actor"]["id"] == "zoe-admin" for event in events)
    assert client.post("/api/decision-records/missing/archive").status_code == 404


def test_guard_blocks_proposed_replacement_and_abandoned_survives_restore(
    client: TestClient,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    original = client.post(
        "/api/decision-records", json=payload().model_dump(mode="json")
    ).json()
    designated_approver_ids.add("arun-approver")
    client.post(f"/api/decision-records/{original['id']}/submit")
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})
    client.post(
        f"/api/decision-records/{original['id']}/decision",
        json={"outcome": "Accepted"},
    )
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    replacement = client.post(
        f"/api/decision-records/{original['id']}/replacements"
    ).json()
    original_path = f"/api/decision-records/{original['id']}"
    replacement_path = f"/api/decision-records/{replacement['id']}"

    assert client.post(f"{original_path}/archive").status_code == 200
    assert client.post(f"{replacement_path}/submit").status_code == 409
    assert client.post(f"{original_path}/restore").status_code == 200
    assert client.post(f"{replacement_path}/submit").status_code == 200
    blocked = client.post(f"{original_path}/archive")
    assert blocked.status_code == 409
    assert client.get(original_path).json()["archived"] is False
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})
    assert client.post(
        f"{replacement_path}/decision", json={"outcome": "Rejected"}
    ).status_code == 200
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    assert client.post(f"{original_path}/archive").status_code == 200
    assert client.post(f"{original_path}/restore").status_code == 200

    abandoned = client.post(f"{original_path}/replacements").json()
    abandoned_path = f"/api/decision-records/{abandoned['id']}"
    assert client.post(f"{abandoned_path}/abandon").status_code == 200
    assert client.post(f"{abandoned_path}/archive").status_code == 200
    restored = client.post(f"{abandoned_path}/restore")
    assert restored.status_code == 200
    assert restored.json()["status"] == "Draft"
    assert restored.json()["abandoned"] is True
    assert restored.json()["replaces_record_id"] == original["id"]
    assert client.post(f"{abandoned_path}/submit").status_code == 409
    assert client.put(abandoned_path, json={"title": "Changed"}).status_code == 409


def test_accepted_replacement_ends_proposed_archival_guard(
    client: TestClient,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    original = client.post(
        "/api/decision-records", json=payload().model_dump(mode="json")
    ).json()
    designated_approver_ids.add("arun-approver")
    client.post(f"/api/decision-records/{original['id']}/submit")
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})
    client.post(
        f"/api/decision-records/{original['id']}/decision",
        json={"outcome": "Accepted"},
    )
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    replacement = client.post(
        f"/api/decision-records/{original['id']}/replacements"
    ).json()
    client.post(f"/api/decision-records/{replacement['id']}/submit")
    assert client.post(
        f"/api/decision-records/{original['id']}/archive"
    ).status_code == 409
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})
    assert client.post(
        f"/api/decision-records/{replacement['id']}/decision",
        json={"outcome": "Accepted"},
    ).status_code == 200
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    archived = client.post(f"/api/decision-records/{original['id']}/archive")
    assert archived.status_code == 200
    assert archived.json()["status"] == "Superseded"
    assert archived.json()["archived"] is True
