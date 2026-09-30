"""Validation-Agent-owned acceptance coverage for STORY-012 and owned regressions.

Expected behavior comes from Requirement Definition 1.3 and TEST-001 2.1,
not from the implementation or its developer-owned tests.
"""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.identities import MOCK_IDENTITIES
from app.main import create_app

ADMINISTRATOR = "zoe-admin"
AUTHOR = "maya-member"
APPROVER = "arun-approver"
TARGET_TAG = "story-012-validation"


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        select(test_client, ADMINISTRATOR)
        response = test_client.post(
            "/api/approvers", json={"identity_id": APPROVER}
        )
        assert response.status_code == 200
        yield test_client
    designated_approver_ids.clear()


def select(client: TestClient, identity_id: str) -> None:
    response = client.post("/api/mock-session", json={"identity_id": identity_id})
    assert response.status_code == 200


def create_draft(client: TestClient, title: str) -> dict:
    select(client, AUTHOR)
    response = client.post(
        "/api/decision-records",
        json={
            "title": title,
            "context": "Archived decisions must remain retained and discoverable.",
            "decision": "Use reversible archival.",
            "rationale": "Lifecycle history must not be lost.",
            "alternatives_considered": "Delete retired records.",
            "consequences": "Administrators can restore the prior state.",
            "owner_id": AUTHOR,
            "decision_date": "2026-09-30",
            "tags": [TARGET_TAG],
        },
    )
    assert response.status_code == 201
    return response.json()


def get_record(client: TestClient, record_id: str) -> dict:
    response = client.get(f"/api/decision-records/{record_id}")
    assert response.status_code == 200
    return response.json()


def submit(client: TestClient, record_id: str, actor: str = AUTHOR) -> dict:
    select(client, actor)
    response = client.post(f"/api/decision-records/{record_id}/submit")
    assert response.status_code == 200
    return response.json()


def decide(client: TestClient, record_id: str, outcome: str) -> dict:
    select(client, APPROVER)
    response = client.post(
        f"/api/decision-records/{record_id}/decision",
        json={"outcome": outcome},
    )
    assert response.status_code == 200
    return response.json()


def create_accepted(client: TestClient, title: str) -> dict:
    return decide(client, submit(client, create_draft(client, title)["id"])["id"], "Accepted")


def create_replacement(client: TestClient, original_id: str) -> dict:
    select(client, ADMINISTRATOR)
    response = client.post(f"/api/decision-records/{original_id}/replacements")
    assert response.status_code == 201
    return response.json()


def create_lifecycle_record(client: TestClient, lifecycle: str) -> dict:
    title = f"{lifecycle} archival validation"
    if lifecycle == "Draft":
        return create_draft(client, title)
    proposed = submit(client, create_draft(client, title)["id"])
    if lifecycle == "Proposed":
        return proposed
    if lifecycle in ("Accepted", "Rejected"):
        return decide(client, proposed["id"], lifecycle)
    original = decide(client, proposed["id"], "Accepted")
    replacement = create_replacement(client, original["id"])
    submit(client, replacement["id"], ADMINISTRATOR)
    decide(client, replacement["id"], "Accepted")
    superseded = get_record(client, original["id"])
    assert superseded["status"] == "Superseded"
    return superseded


def archive(client: TestClient, record_id: str) -> dict:
    select(client, ADMINISTRATOR)
    response = client.post(f"/api/decision-records/{record_id}/archive")
    assert response.status_code == 200
    return response.json()


def test_tc_012_01_and_03_archive_discover_and_restore_every_lifecycle(
    client: TestClient,
) -> None:
    """TC-012-01/03 and archived TC-009-01 leg: state survives discovery."""
    lifecycles = ("Draft", "Proposed", "Accepted", "Rejected", "Superseded")
    originals = {
        record["id"]: record
        for record in (create_lifecycle_record(client, state) for state in lifecycles)
    }

    for record_id, original in originals.items():
        archived = archive(client, record_id)
        assert archived["archived"] is True
        assert archived["status"] == original["status"]
        assert get_record(client, record_id) == archived

    discovered = client.get(
        "/api/decision-records", params={"tag": TARGET_TAG}
    ).json()["records"]
    discovered_by_id = {record["id"]: record for record in discovered}
    assert set(originals).issubset(discovered_by_id)
    assert all(discovered_by_id[record_id]["archived"] for record_id in originals)

    for record_id, original in originals.items():
        select(client, ADMINISTRATOR)
        restored = client.post(f"/api/decision-records/{record_id}/restore")
        assert restored.status_code == 200
        assert restored.json() == original


def test_tc_012_02_and_tc_002_02_nonadministrators_cannot_govern_records(
    client: TestClient,
) -> None:
    """Every administrator-only record action is denied without state changes."""
    unarchived = create_draft(client, "Role matrix unarchived")
    archived = archive(client, create_draft(client, "Role matrix archived")["id"])
    original = create_accepted(client, "Role matrix original")
    replacement = create_replacement(client, original["id"])

    for actor in (AUTHOR, APPROVER):
        select(client, actor)
        cases = (
            (f"/api/decision-records/{unarchived['id']}/archive", unarchived["id"]),
            (f"/api/decision-records/{archived['id']}/restore", archived["id"]),
            (f"/api/decision-records/{original['id']}/replacements", original["id"]),
            (f"/api/decision-records/{replacement['id']}/abandon", replacement["id"]),
        )
        for path, record_id in cases:
            before = get_record(client, record_id)
            response = client.post(path)
            assert response.status_code == 403
            assert get_record(client, record_id) == before


@pytest.mark.parametrize("outcome", ["Accepted", "Rejected"])
def test_tc_012_04_active_proposed_replacement_guard_ends_after_review(
    client: TestClient, outcome: str
) -> None:
    """An Accepted original is blocked only while its replacement is Proposed."""
    original = create_accepted(client, f"Replacement guard {outcome}")
    replacement = create_replacement(client, original["id"])
    submit(client, replacement["id"], ADMINISTRATOR)

    select(client, ADMINISTRATOR)
    blocked = client.post(f"/api/decision-records/{original['id']}/archive")
    assert blocked.status_code == 409
    assert get_record(client, original["id"])["archived"] is False

    decide(client, replacement["id"], outcome)
    archived = archive(client, original["id"])
    assert archived["archived"] is True
    assert archived["status"] == ("Superseded" if outcome == "Accepted" else "Accepted")


def test_tc_012_05_abandoned_replacement_stays_abandoned_and_immutable(
    client: TestClient,
) -> None:
    """Archive/restore cannot reactivate or make an Abandoned Draft mutable."""
    original = create_accepted(client, "Abandoned replacement")
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    abandoned_response = client.post(
        f"/api/decision-records/{replacement['id']}/abandon"
    )
    assert abandoned_response.status_code == 200
    abandoned = abandoned_response.json()

    archive(client, replacement["id"])
    select(client, ADMINISTRATOR)
    restored_response = client.post(
        f"/api/decision-records/{replacement['id']}/restore"
    )
    assert restored_response.status_code == 200
    restored = restored_response.json()
    assert restored == abandoned
    assert restored["status"] == "Draft"
    assert restored["abandoned"] is True
    assert restored["replaces_record_id"] == original["id"]

    for actor in (AUTHOR, APPROVER, ADMINISTRATOR):
        select(client, actor)
        before = get_record(client, replacement["id"])
        assert (
            client.put(
                f"/api/decision-records/{replacement['id']}",
                json={"title": "Attempted reactivation"},
            ).status_code
            in (403, 409)
        )
        assert client.post(
            f"/api/decision-records/{replacement['id']}/submit"
        ).status_code in (403, 409)
        assert get_record(client, replacement["id"]) == before


def test_tc_013_01_and_02_records_have_no_deletion_path_and_remain_restorable(
    client: TestClient,
) -> None:
    """Archived and Abandoned conditions remain retained for every role."""
    archived = archive(client, create_draft(client, "Deletion denial archived")["id"])
    original = create_accepted(client, "Deletion denial original")
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    abandoned = client.post(
        f"/api/decision-records/{replacement['id']}/abandon"
    ).json()

    route_methods = {
        method
        for route in client.app.routes
        if getattr(route, "path", None) == "/api/decision-records/{record_id}"
        for method in getattr(route, "methods", set())
    }
    assert "DELETE" not in route_methods

    for actor in MOCK_IDENTITIES:
        select(client, actor.id)
        for record in (archived, abandoned):
            response = client.delete(f"/api/decision-records/{record['id']}")
            assert response.status_code == 405
            assert get_record(client, record["id"]) == record

    select(client, ADMINISTRATOR)
    restored = client.post(f"/api/decision-records/{archived['id']}/restore")
    assert restored.status_code == 200
    assert restored.json()["id"] == archived["id"]
    assert restored.json()["archived"] is False


def test_tc_015_01_and_03_archive_audit_is_attributed_immutable_and_retained(
    client: TestClient,
) -> None:
    """Archive/restore events and archived records have no expiry/deletion path."""
    record = create_draft(client, "Audit and retention")
    archived = archive(client, record["id"])
    select(client, ADMINISTRATOR)
    restored = client.post(f"/api/decision-records/{record['id']}/restore")
    assert restored.status_code == 200

    events = client.get(
        f"/api/decision-records/{record['id']}/audit-events"
    ).json()["events"]
    assert [event["event_type"] for event in events] == [
        "record_archived",
        "record_restored",
    ]
    assert [event["changes"][0] for event in events] == [
        {"field": "archived", "before": False, "after": True},
        {"field": "archived", "before": True, "after": False},
    ]
    assert all(event["actor"]["id"] == ADMINISTRATOR for event in events)
    assert all(event["occurred_at"] for event in events)
    assert "expires_at" not in archived
    assert all("expires_at" not in event for event in events)

    for event in events:
        path = f"/api/audit-events/{event['id']}"
        assert client.put(path, json={"event_type": "changed"}).status_code == 405
        assert client.delete(path).status_code == 405
        assert client.get(path).json() == event
        assert client.get(path).json() == event

    assert client.delete(f"/api/decision-records/{record['id']}").status_code == 405
    assert get_record(client, record["id"]) == restored.json()


def test_concurrent_archive_and_restore_commit_one_event_per_transition(
    client: TestClient,
) -> None:
    """Concurrent duplicate requests cannot create duplicate state changes."""
    record = create_draft(client, "Concurrent archive and restore")
    select(client, ADMINISTRATOR)

    def post(action: str) -> int:
        return client.post(
            f"/api/decision-records/{record['id']}/{action}"
        ).status_code

    with ThreadPoolExecutor(max_workers=8) as executor:
        archive_statuses = list(executor.map(lambda _: post("archive"), range(8)))
    assert archive_statuses.count(200) == 1
    assert archive_statuses.count(409) == 7
    assert get_record(client, record["id"])["archived"] is True

    with ThreadPoolExecutor(max_workers=8) as executor:
        restore_statuses = list(executor.map(lambda _: post("restore"), range(8)))
    assert restore_statuses.count(200) == 1
    assert restore_statuses.count(409) == 7
    assert get_record(client, record["id"]) == record

    events = client.get(
        f"/api/decision-records/{record['id']}/audit-events"
    ).json()["events"]
    assert [event["event_type"] for event in events] == [
        "record_archived",
        "record_restored",
    ]
