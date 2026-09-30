"""Independent acceptance coverage for STORY-007, TS-007.

Expected behavior comes from the approved Requirement Definition and TEST-001,
not from the implementation or its unit tests.
"""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import httpx
import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.identities import MOCK_IDENTITIES
from app.main import create_app

ADMINISTRATOR = "zoe-admin"
AUTHOR = "maya-member"
APPROVER = "arun-approver"
OTHER_APPROVER = "lee-admin-approver"
RECORD_FIELDS = {
    "title": "Adopt the isolated persistence boundary",
    "context": "Persistence and transport concerns are coupled.",
    "decision": "Use a dedicated persistence boundary.",
    "rationale": "A single-purpose module isolates storage changes.",
    "alternatives_considered": "Keep the current shared module.",
    "consequences": "The application will have separate focused modules.",
    "owner_id": AUTHOR,
    "decision_date": "2026-09-29",
    "tags": ["architecture", "backend"],
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


def designate(client: TestClient, identity_id: str = APPROVER) -> None:
    select(client, ADMINISTRATOR)
    response = client.post("/api/approvers", json={"identity_id": identity_id})
    assert response.status_code == 200


def create_draft(client: TestClient) -> dict:
    select(client, AUTHOR)
    response = client.post("/api/decision-records", json=RECORD_FIELDS)
    assert response.status_code == 201
    return response.json()


def create_proposed(client: TestClient) -> dict:
    designate(client)
    draft = create_draft(client)
    response = client.post(f"/api/decision-records/{draft['id']}/submit")
    assert response.status_code == 200
    assert response.json()["status"] == "Proposed"
    return response.json()


def decide(client: TestClient, record_id: str, outcome: str) -> dict:
    select(client, APPROVER)
    response = client.post(
        f"/api/decision-records/{record_id}/decision",
        json={"outcome": outcome},
    )
    assert response.status_code == 200
    return response.json()


def create_accepted(client: TestClient) -> dict:
    proposed = create_proposed(client)
    return decide(client, proposed["id"], "Accepted")


def create_replacement(client: TestClient, original_id: str) -> dict:
    select(client, ADMINISTRATOR)
    response = client.post(
        f"/api/decision-records/{original_id}/replacements"
    )
    assert response.status_code == 201
    return response.json()


def get_record(client: TestClient, record_id: str) -> dict:
    response = client.get(f"/api/decision-records/{record_id}")
    assert response.status_code == 200
    return response.json()


def audit_events(client: TestClient, record_id: str) -> list[dict]:
    response = client.get(
        f"/api/decision-records/{record_id}/audit-events"
    )
    assert response.status_code == 200
    return response.json()["events"]


def test_tc_007_01_accepted_record_rejects_direct_edit_for_every_identity(
    client: TestClient,
) -> None:
    """TC-007-01 / AC-009: Accepted decision content cannot be edited directly."""
    accepted = create_accepted(client)

    for identity in MOCK_IDENTITIES:
        select(client, identity.id)
        response = client.put(
            f"/api/decision-records/{accepted['id']}",
            json={"title": "Directly edited Accepted decision"},
        )
        assert response.status_code in (403, 409)
        assert get_record(client, accepted["id"]) == accepted


def test_tc_007_02_administrator_creates_one_linked_active_replacement(
    client: TestClient,
) -> None:
    """TC-007-02 / AC-010: replacement starts as linked Draft immediately."""
    original = create_accepted(client)

    replacement = create_replacement(client, original["id"])

    assert replacement["status"] == "Draft"
    assert replacement["abandoned"] is False
    assert replacement["replaces_record_id"] == original["id"]
    assert replacement["title"] == original["title"]
    assert replacement["context"] == original["context"]
    assert replacement["decision"] == original["decision"]
    assert replacement["rationale"] == original["rationale"]
    assert replacement["alternatives_considered"] == original[
        "alternatives_considered"
    ]
    assert replacement["consequences"] == original["consequences"]
    assert replacement["owner"] == original["owner"]
    retained_original = get_record(client, original["id"])
    assert retained_original["status"] == "Accepted"
    assert retained_original["replacement_record_ids"] == [replacement["id"]]
    assert get_record(client, replacement["id"]) == replacement


def test_tc_007_03_nonadministrator_and_second_active_replacement_are_denied(
    client: TestClient,
) -> None:
    """TC-007-03 / AC-003, AC-025: role and single-active limit are enforced."""
    first_original = create_accepted(client)
    select(client, AUTHOR)
    unauthorized = client.post(
        f"/api/decision-records/{first_original['id']}/replacements"
    )
    assert unauthorized.status_code == 403
    assert get_record(client, first_original["id"]) == first_original

    replacement = create_replacement(client, first_original["id"])
    before_records = client.get("/api/decision-records").json()["records"]
    select(client, ADMINISTRATOR)
    duplicate = client.post(
        f"/api/decision-records/{first_original['id']}/replacements"
    )
    assert duplicate.status_code == 409
    assert client.get("/api/decision-records").json()["records"] == before_records
    assert get_record(client, replacement["id"])["status"] == "Draft"


def test_tc_007_04_acceptance_atomically_supersedes_and_keeps_version_links(
    client: TestClient,
) -> None:
    """TC-007-04 / AC-011, AC-039: both lifecycle changes and links are retained."""
    original = create_accepted(client)
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    proposed = client.post(
        f"/api/decision-records/{replacement['id']}/submit"
    )
    assert proposed.status_code == 200
    accepted = decide(client, replacement["id"], "Accepted")

    superseded = get_record(client, original["id"])
    assert accepted["status"] == "Accepted"
    assert accepted["replaces_record_id"] == original["id"]
    assert superseded["status"] == "Superseded"
    assert superseded["replacement_record_ids"] == [replacement["id"]]
    assert get_record(client, accepted["id"]) == accepted
    event = next(
        event
        for event in audit_events(client, accepted["id"])
        if any(
            change["field"] == f"related_record.{original['id']}.status"
            for change in event["changes"]
        )
    )
    assert event["actor"]["id"] == APPROVER
    assert {
        "field": "status",
        "before": "Proposed",
        "after": "Accepted",
    } in event["changes"]
    assert {
        "field": f"related_record.{original['id']}.status",
        "before": "Accepted",
        "after": "Superseded",
    } in event["changes"]


def test_tc_007_05_rejection_ends_active_interval_and_permits_next_version(
    client: TestClient,
) -> None:
    """TC-007-05 / AC-039: a Rejected replacement does not block another."""
    original = create_accepted(client)
    rejected_draft = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    proposed = client.post(
        f"/api/decision-records/{rejected_draft['id']}/submit"
    )
    assert proposed.status_code == 200
    rejected = decide(client, rejected_draft["id"], "Rejected")

    next_replacement = create_replacement(client, original["id"])

    assert rejected["status"] == "Rejected"
    assert get_record(client, original["id"])["status"] == "Accepted"
    assert next_replacement["status"] == "Draft"
    assert get_record(client, original["id"])["replacement_record_ids"] == [
        rejected_draft["id"],
        next_replacement["id"],
    ]


def test_tc_007_06_abandonment_retains_audits_links_and_allows_new_version(
    client: TestClient,
) -> None:
    """TC-007-06 / AC-046: Abandoned Draft and original remain navigable."""
    original = create_accepted(client)
    abandoned_draft = create_replacement(client, original["id"])

    select(client, ADMINISTRATOR)
    abandoned_response = client.post(
        f"/api/decision-records/{abandoned_draft['id']}/abandon"
    )
    assert abandoned_response.status_code == 200
    abandoned = abandoned_response.json()
    retained_original = get_record(client, original["id"])
    assert abandoned["status"] == "Draft"
    assert abandoned["abandoned"] is True
    assert abandoned["replaces_record_id"] == original["id"]
    assert retained_original["status"] == "Accepted"
    assert retained_original["replacement_record_ids"] == [abandoned["id"]]
    abandonment = next(
        event
        for event in audit_events(client, abandoned["id"])
        if event["event_type"] == "replacement_draft_abandoned"
    )
    assert abandonment["actor"]["id"] == ADMINISTRATOR
    assert abandonment["occurred_at"]
    assert abandonment["changes"] == [
        {"field": "abandoned", "before": False, "after": True}
    ]

    select(client, ADMINISTRATOR)
    next_replacement = create_replacement(client, original["id"])
    retained_original = get_record(client, original["id"])
    assert retained_original["replacement_record_ids"] == [
        abandoned["id"],
        next_replacement["id"],
    ]

    page = client.get("/app")
    script = client.get("/static/app.js")
    assert page.status_code == 200
    assert script.status_code == 200
    assert f"record-card-${{original.id}}" in script.text
    assert f"record-card-${{replacement.id}}" in script.text
    assert "Version of:" in script.text
    assert "Replacement:" in script.text
    assert "/abandon" in script.text


def test_tc_007_07_only_active_replacement_drafts_can_be_abandoned(
    client: TestClient,
) -> None:
    """TC-007-07 / AC-003, AC-047: invalid role and target combinations fail."""
    ordinary_draft = create_draft(client)
    active_original = create_accepted(client)
    active_replacement = create_replacement(client, active_original["id"])
    proposed_original = create_accepted(client)
    proposed_replacement = create_replacement(client, proposed_original["id"])
    select(client, ADMINISTRATOR)
    assert client.post(
        f"/api/decision-records/{proposed_replacement['id']}/submit"
    ).status_code == 200
    rejected_original = create_accepted(client)
    rejected_replacement = create_replacement(client, rejected_original["id"])
    select(client, ADMINISTRATOR)
    assert client.post(
        f"/api/decision-records/{rejected_replacement['id']}/submit"
    ).status_code == 200
    rejected = decide(client, rejected_replacement["id"], "Rejected")
    superseded_original = create_accepted(client)
    accepted_replacement = create_replacement(client, superseded_original["id"])
    select(client, ADMINISTRATOR)
    assert client.post(
        f"/api/decision-records/{accepted_replacement['id']}/submit"
    ).status_code == 200
    accepted = decide(client, accepted_replacement["id"], "Accepted")
    superseded = get_record(client, superseded_original["id"])
    assert superseded["status"] == "Superseded"

    select(client, AUTHOR)
    before_active = get_record(client, active_replacement["id"])
    denied = client.post(
        f"/api/decision-records/{active_replacement['id']}/abandon"
    )
    assert denied.status_code == 403
    assert get_record(client, active_replacement["id"]) == before_active

    invalid_targets = (
        ordinary_draft,
        proposed_replacement,
        accepted,
        rejected,
        superseded,
    )
    select(client, ADMINISTRATOR)
    for target in invalid_targets:
        before = get_record(client, target["id"])
        response = client.post(
            f"/api/decision-records/{target['id']}/abandon"
        )
        assert response.status_code == 409
        assert get_record(client, target["id"]) == before


def test_tc_007_08_abandoned_replacement_cannot_be_mutated_removed_or_reactivated(
    client: TestClient,
) -> None:
    """TC-007-08 / AC-047: abandoned replacement stays immutable and retained."""
    original = create_accepted(client)
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    abandoned_response = client.post(
        f"/api/decision-records/{replacement['id']}/abandon"
    )
    assert abandoned_response.status_code == 200
    abandoned = abandoned_response.json()
    for identity in MOCK_IDENTITIES:
        designate(client, identity.id)

    for identity in MOCK_IDENTITIES:
        select(client, identity.id)
        mutation_attempts = (
            client.put(
                f"/api/decision-records/{replacement['id']}",
                json={"title": "Changed abandoned content"},
            ),
            client.put(
                f"/api/decision-records/{replacement['id']}",
                json={"status": "Proposed"},
            ),
            client.post(
                f"/api/decision-records/{replacement['id']}/owner",
                json={"owner_id": OTHER_APPROVER},
            ),
            client.put(
                f"/api/decision-records/{replacement['id']}",
                json={"approver_ids": [identity.id]},
            ),
            client.put(
                f"/api/decision-records/{replacement['id']}",
                json={"version_content": "Changed version"},
            ),
            client.put(
                f"/api/decision-records/{replacement['id']}",
                json={"abandoned": False},
            ),
            client.post(
                f"/api/decision-records/{replacement['id']}/submit"
            ),
            client.post(
                f"/api/decision-records/{replacement['id']}/abandon"
            ),
            client.post(
                f"/api/decision-records/{replacement['id']}/decision",
                json={"outcome": "Accepted"},
            ),
            client.delete(f"/api/decision-records/{replacement['id']}"),
        )
        assert all(not response.is_success for response in mutation_attempts)
        assert get_record(client, replacement["id"]) == abandoned

    records = client.get("/api/decision-records").json()["records"]
    assert any(record["id"] == replacement["id"] for record in records)
    assert get_record(client, original["id"])["status"] == "Accepted"


def test_tc_004_05_abandoned_replacement_cannot_be_edited_or_submitted(
    client: TestClient,
) -> None:
    """Deferred TC-004-05: STORY-007 supplies the abandoned-Draft fixture."""
    original = create_accepted(client)
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    abandoned = client.post(
        f"/api/decision-records/{replacement['id']}/abandon"
    )
    assert abandoned.status_code == 200
    before = abandoned.json()

    for identity in MOCK_IDENTITIES:
        select(client, identity.id)
        edit = client.put(
            f"/api/decision-records/{replacement['id']}",
            json={"title": "Edit abandoned replacement"},
        )
        submit = client.post(
            f"/api/decision-records/{replacement['id']}/submit"
        )
        assert edit.status_code in (403, 409)
        assert submit.status_code in (403, 409)
        assert get_record(client, replacement["id"]) == before


def test_tc_005_03_superseded_original_is_immutable_for_all_identities(
    client: TestClient,
) -> None:
    """Deferred TC-005-03: replacement acceptance produces Superseded."""
    original = create_accepted(client)
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    assert client.post(
        f"/api/decision-records/{replacement['id']}/submit"
    ).status_code == 200
    decide(client, replacement["id"], "Accepted")
    superseded = get_record(client, original["id"])

    for identity in MOCK_IDENTITIES:
        select(client, identity.id)
        content = client.put(
            f"/api/decision-records/{original['id']}",
            json={"title": "Change superseded record"},
        )
        lifecycle = client.put(
            f"/api/decision-records/{original['id']}",
            json={"status": "Draft"},
        )
        version = client.put(
            f"/api/decision-records/{original['id']}",
            json={"replacement_record_ids": []},
        )
        submit = client.post(
            f"/api/decision-records/{original['id']}/submit"
        )
        assert content.status_code in (403, 409)
        assert lifecycle.status_code == 422
        assert version.status_code == 422
        assert submit.status_code == 409
        assert get_record(client, original["id"]) == superseded


def test_tc_006_02_abandoned_replacement_refuses_ownership_transfer(
    client: TestClient,
) -> None:
    """Deferred TC-006-02: ownership cannot change after abandonment."""
    original = create_accepted(client)
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    abandoned = client.post(
        f"/api/decision-records/{replacement['id']}/abandon"
    )
    assert abandoned.status_code == 200
    before = abandoned.json()
    before_events = audit_events(client, replacement["id"])

    for identity in MOCK_IDENTITIES:
        select(client, identity.id)
        response = client.post(
            f"/api/decision-records/{replacement['id']}/owner",
            json={"owner_id": OTHER_APPROVER},
        )
        assert response.status_code == 409
        assert get_record(client, replacement["id"]) == before
        assert audit_events(client, replacement["id"]) == before_events


def test_replacement_acceptance_race_commits_one_outcome_and_one_supersession(
    client: TestClient,
) -> None:
    """TS-007 regression: concurrent Accept/Reject cannot split version state."""
    original = create_accepted(client)
    replacement = create_replacement(client, original["id"])
    select(client, ADMINISTRATOR)
    proposed = client.post(
        f"/api/decision-records/{replacement['id']}/submit"
    )
    assert proposed.status_code == 200
    designate(client, OTHER_APPROVER)
    barrier = Barrier(2)

    def decide_as(identity: str, outcome: str) -> httpx.Response:
        with TestClient(client.app) as actor:
            select(actor, identity)
            barrier.wait(timeout=5)
            return actor.post(
                f"/api/decision-records/{replacement['id']}/decision",
                json={"outcome": outcome},
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        accepted = executor.submit(decide_as, APPROVER, "Accepted")
        rejected = executor.submit(decide_as, OTHER_APPROVER, "Rejected")
        responses = [accepted.result(timeout=10), rejected.result(timeout=10)]

    assert sorted(response.status_code for response in responses) == [200, 409]
    final_replacement = get_record(client, replacement["id"])
    final_original = get_record(client, original["id"])
    assert final_replacement["status"] in ("Accepted", "Rejected")
    assert final_original["status"] == (
        "Superseded"
        if final_replacement["status"] == "Accepted"
        else "Accepted"
    )
