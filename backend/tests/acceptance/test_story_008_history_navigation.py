"""Independent acceptance coverage for STORY-008, TS-008.

Expected behavior comes from the approved Requirement Definition and TEST-001,
not from the implementation or its unit tests.
"""

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.main import create_app

ADMINISTRATOR = "zoe-admin"
AUTHOR = "maya-member"
APPROVER = "arun-approver"
RECORD_FIELDS = {
    "title": "Retain attributed decision history",
    "context": "Version relationships must remain traceable.",
    "decision": "Keep every version and its changes.",
    "rationale": "Readers need reliable historical evidence.",
    "alternatives_considered": "Overwrite earlier decision values.",
    "consequences": "History and replacement links remain navigable.",
    "owner_id": AUTHOR,
    "decision_date": "2026-09-30",
    "tags": ["history"],
}


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        select(test_client, AUTHOR)
        yield test_client
    designated_approver_ids.clear()


def select(client: TestClient, identity_id: str) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": identity_id},
    )
    assert response.status_code == 200


def designate_approver(client: TestClient) -> None:
    select(client, ADMINISTRATOR)
    response = client.post("/api/approvers", json={"identity_id": APPROVER})
    assert response.status_code == 200


def create_draft(client: TestClient) -> dict:
    select(client, AUTHOR)
    response = client.post("/api/decision-records", json=RECORD_FIELDS)
    assert response.status_code == 201
    return response.json()


def create_accepted(client: TestClient) -> dict:
    designate_approver(client)
    draft = create_draft(client)
    response = client.post(f"/api/decision-records/{draft['id']}/submit")
    assert response.status_code == 200
    select(client, APPROVER)
    response = client.post(
        f"/api/decision-records/{draft['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert response.status_code == 200
    return response.json()


def create_replacement(client: TestClient, original_id: str) -> dict:
    select(client, ADMINISTRATOR)
    response = client.post(
        f"/api/decision-records/{original_id}/replacements"
    )
    assert response.status_code == 201
    return response.json()


def decide_replacement(
    client: TestClient,
    replacement: dict,
    outcome: str,
) -> dict:
    designate_approver(client)
    response = client.post(
        f"/api/decision-records/{replacement['id']}/submit"
    )
    assert response.status_code == 200
    select(client, APPROVER)
    response = client.post(
        f"/api/decision-records/{replacement['id']}/decision",
        json={"outcome": outcome},
    )
    assert response.status_code == 200
    return response.json()


def get_record(client: TestClient, record_id: str) -> dict:
    response = client.get(f"/api/decision-records/{record_id}")
    assert response.status_code == 200
    return response.json()


def history(client: TestClient, record_id: str) -> list[dict]:
    response = client.get(
        f"/api/decision-records/{record_id}/audit-events"
    )
    assert response.status_code == 200
    return response.json()["events"]


def test_tc_008_01_accepted_and_superseded_versions_remain_bidirectionally_linked(
    client: TestClient,
) -> None:
    """TC-008-01 / AC-012: related accepted versions resolve both ways."""
    original = create_accepted(client)
    replacement = create_replacement(client, original["id"])
    accepted = decide_replacement(client, replacement, "Accepted")

    superseded = get_record(client, original["id"])
    retained_replacement = get_record(client, accepted["id"])

    assert superseded["status"] == "Superseded"
    assert superseded["replacement_record_ids"] == [accepted["id"]]
    assert retained_replacement["status"] == "Accepted"
    assert retained_replacement["replaces_record_id"] == original["id"]
    assert get_record(client, superseded["replacement_record_ids"][0]) == (
        retained_replacement
    )
    assert get_record(client, retained_replacement["replaces_record_id"]) == (
        superseded
    )


def test_tc_008_02_abandoned_replacement_link_is_retained_in_both_directions(
    client: TestClient,
) -> None:
    """TC-008-02 / AC-046: both retained records remain reachable."""
    original = create_accepted(client)
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    abandoned_response = client.post(
        f"/api/decision-records/{replacement['id']}/abandon"
    )
    assert abandoned_response.status_code == 200

    abandoned = get_record(client, replacement["id"])
    retained_original = get_record(client, original["id"])

    assert abandoned["status"] == "Draft"
    assert abandoned["abandoned"] is True
    assert abandoned["replaces_record_id"] == original["id"]
    assert retained_original["status"] == "Accepted"
    assert retained_original["replacement_record_ids"] == [abandoned["id"]]
    assert get_record(client, retained_original["replacement_record_ids"][0]) == (
        abandoned
    )
    assert get_record(client, abandoned["replaces_record_id"]) == retained_original


def test_tc_008_03_history_shows_change_actor_time_and_has_no_mutation_path(
    client: TestClient,
) -> None:
    """TC-008-03 / AC-013: history is attributed, timestamped, and immutable."""
    draft = create_draft(client)
    select(client, AUTHOR)
    update = client.put(
        f"/api/decision-records/{draft['id']}",
        json={"title": "A known attributed title change"},
    )
    assert update.status_code == 200

    events = history(client, draft["id"])
    matching = [
        event
        for event in events
        if any(
            change["field"] == "title"
            and change["before"] == RECORD_FIELDS["title"]
            and change["after"] == "A known attributed title change"
            for change in event["changes"]
        )
    ]
    assert len(matching) == 1
    event = matching[0]
    assert event["actor"]["id"] == AUTHOR
    assert event["actor"]["display_name"]
    assert datetime.fromisoformat(event["occurred_at"]).tzinfo is not None

    snapshot = client.get(
        f"/api/decision-records/{draft['id']}/audit-events"
    ).json()["events"]
    assert client.put(
        f"/api/audit-events/{event['id']}",
        json={"subject_id": "tampered"},
    ).status_code == 405
    assert client.delete(f"/api/audit-events/{event['id']}").status_code == 405
    assert history(client, draft["id"]) == snapshot
    assert client.get(f"/api/audit-events/{event['id']}").json() == event


def test_tc_008_04_terminal_records_and_multiversion_history_stay_intact(
    client: TestClient,
) -> None:
    """TC-008-04 / AC-038, AC-047: terminal states deny edits; chain stays sound."""
    first = create_accepted(client)
    first_replacement = create_replacement(client, first["id"])
    second = decide_replacement(client, first_replacement, "Accepted")
    rejected_replacement = create_replacement(client, second["id"])
    rejected = decide_replacement(client, rejected_replacement, "Rejected")
    accepted_replacement = create_replacement(client, second["id"])
    third = decide_replacement(client, accepted_replacement, "Accepted")
    abandoned_replacement = create_replacement(client, third["id"])
    select(client, ADMINISTRATOR)
    abandoned_response = client.post(
        f"/api/decision-records/{abandoned_replacement['id']}/abandon"
    )
    assert abandoned_response.status_code == 200

    records = [
        get_record(client, record_id)
        for record_id in (
            first["id"],
            second["id"],
            rejected["id"],
            third["id"],
            abandoned_replacement["id"],
        )
    ]
    immutable_before = {record["id"]: record for record in records}
    histories_before = {record["id"]: history(client, record["id"]) for record in records}

    for identity_id in (AUTHOR, APPROVER, ADMINISTRATOR):
        select(client, identity_id)
        for record in records:
            record_url = f"/api/decision-records/{record['id']}"
            assert client.put(
                record_url,
                json={"title": "Attempt to change a terminal record"},
            ).status_code in (403, 409)
            assert client.put(record_url, json={"status": "Draft"}).status_code == 422
            for version_field in (
                "abandoned",
                "approver_ids",
                "replacement_record_ids",
                "version_content",
            ):
                assert client.put(
                    record_url,
                    json={version_field: False if version_field == "abandoned" else []},
                ).status_code == 422
            assert client.post(
                f"{record_url}/owner",
                json={"owner_id": ADMINISTRATOR},
            ).status_code == 409
            assert client.post(f"{record_url}/submit").status_code == 409
            assert client.post(
                f"{record_url}/decision",
                json={"outcome": "Rejected"},
            ).status_code in (403, 409)
            if record["replaces_record_id"]:
                assert client.post(f"{record_url}/abandon").status_code in (
                    403,
                    409,
                )
            assert client.delete(record_url).status_code == 405
            assert get_record(client, record["id"]) == immutable_before[record["id"]]

    assert get_record(client, first["id"])["replacement_record_ids"] == [
        second["id"]
    ]
    assert get_record(client, second["id"])["replacement_record_ids"] == [
        rejected["id"],
        third["id"],
    ]
    assert get_record(client, rejected["id"])["replaces_record_id"] == second["id"]
    assert get_record(client, third["id"])["replacement_record_ids"] == [
        abandoned_replacement["id"]
    ]
    assert get_record(client, abandoned_replacement["id"])["replaces_record_id"] == (
        third["id"]
    )

    for _ in range(3):
        for record in records:
            assert get_record(client, record["id"]) == immutable_before[record["id"]]
            assert history(client, record["id"]) == histories_before[record["id"]]

    assert len({record["id"] for record in records}) == len(records)
