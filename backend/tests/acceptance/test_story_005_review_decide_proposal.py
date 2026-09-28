"""Validation-Agent-owned acceptance tests for STORY-005 (TS-005).

Expected behavior is taken from the approved Requirement Definition and
TEST-001, not from implementation choices.
"""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.identities import MOCK_IDENTITIES
from app.main import create_app

AUTHOR = "maya-member"
APPROVER = "arun-approver"
SECOND_APPROVER = "lee-admin-approver"


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        select_identity(test_client, AUTHOR)
        yield test_client
    designated_approver_ids.clear()


def select_identity(client: TestClient, identity_id: str) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": identity_id},
    )
    assert response.status_code == 200


def complete_record() -> dict[str, object]:
    return {
        "title": "Adopt an explicit persistence boundary",
        "context": "Persistence and transport concerns are currently mixed.",
        "decision": "Introduce a dedicated persistence module.",
        "rationale": "A single responsibility keeps future changes isolated.",
        "alternatives_considered": "Keep one module and accept the coupling.",
        "consequences": "Two focused modules must be maintained.",
        "owner_id": "maya-member",
        "decision_date": "2026-09-28",
        "tags": ["architecture", "backend"],
    }


def create_proposed(client: TestClient) -> dict[str, object]:
    created = client.post("/api/decision-records", json=complete_record())
    assert created.status_code == 201
    designate(client, APPROVER)
    proposed = client.post(
        f"/api/decision-records/{created.json()['id']}/submit"
    )
    assert proposed.status_code == 200
    assert proposed.json()["status"] == "Proposed"
    return proposed.json()


def designate(client: TestClient, identity_id: str) -> None:
    with TestClient(client.app) as administrator:
        select_identity(administrator, "zoe-admin")
        response = administrator.post(
            "/api/approvers",
            json={"identity_id": identity_id},
        )
    assert response.status_code == 200


@pytest.mark.parametrize("outcome", ["Accepted", "Rejected"])
def test_tc_005_01_only_designated_approver_completes_each_outcome(
    client: TestClient,
    outcome: str,
) -> None:
    """TC-005-01: designated actors succeed; non-approvers cannot decide."""
    proposed = create_proposed(client)

    denied = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": outcome},
    )
    assert denied.status_code == 403
    assert client.get(f"/api/decision-records/{proposed['id']}").json() == proposed

    select_identity(client, APPROVER)
    decided = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": outcome},
    )
    assert decided.status_code == 200
    assert decided.json()["status"] == outcome


@pytest.mark.parametrize("outcome", ["Accepted", "Rejected"])
def test_tc_005_01_designated_author_may_decide_own_proposal(
    client: TestClient,
    outcome: str,
) -> None:
    """TC-005-01 / AC-007: designated authors retain decision authority."""
    proposed = create_proposed(client)
    designate(client, AUTHOR)

    decided = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": outcome},
    )

    assert decided.status_code == 200
    assert decided.json()["status"] == outcome


def test_tc_005_02_author_edit_restarts_review_until_resubmission(
    client: TestClient,
) -> None:
    """TC-005-02: edit resets Proposed to Draft; a new submission is required."""
    proposed = create_proposed(client)
    designate(client, APPROVER)

    edited = client.put(
        f"/api/decision-records/{proposed['id']}",
        json={"title": "Revised persistence boundary"},
    )

    assert edited.status_code == 200
    assert edited.json()["status"] == "Draft"
    assert edited.json()["title"] == "Revised persistence boundary"

    select_identity(client, APPROVER)
    premature_decision = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert premature_decision.status_code == 409
    assert client.get(f"/api/decision-records/{proposed['id']}").json()["status"] == (
        "Draft"
    )

    select_identity(client, AUTHOR)
    resubmitted = client.post(
        f"/api/decision-records/{proposed['id']}/submit"
    )
    assert resubmitted.status_code == 200
    assert resubmitted.json()["status"] == "Proposed"

    select_identity(client, APPROVER)
    decided = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert decided.status_code == 200
    assert decided.json()["status"] == "Accepted"

    events = client.get(
        f"/api/decision-records/{proposed['id']}/audit-events"
    ).json()["events"]
    restart_events = [
        event
        for event in events
        if {
            "field": "status",
            "before": "Proposed",
            "after": "Draft",
        }
        in event["changes"]
    ]
    assert len(restart_events) == 1
    assert restart_events[0]["actor"]["id"] == AUTHOR
    assert {
        "field": "title",
        "before": complete_record()["title"],
        "after": "Revised persistence boundary",
    } in restart_events[0]["changes"]


@pytest.mark.parametrize("terminal_status", ["Rejected", "Superseded"])
def test_tc_005_03_rejected_and_superseded_records_are_immutable(
    client: TestClient,
    terminal_status: str,
) -> None:
    """TC-005-03: terminal records reject content and lifecycle mutations.

    STORY-007 does not yet provide supersession, so Superseded is a controlled
    precondition fixture corresponding to the approved Test Design.
    """
    proposed = create_proposed(client)
    if terminal_status == "Rejected":
        designate(client, APPROVER)
        select_identity(client, APPROVER)
        response = client.post(
            f"/api/decision-records/{proposed['id']}/decision",
            json={"outcome": "Rejected"},
        )
        assert response.status_code == 200
        terminal = response.json()
    else:
        record_store = client.app.state.record_store
        record = record_store.get(str(proposed["id"]))
        assert record is not None
        terminal_record = record.model_copy(update={"status": "Superseded"})
        with record_store._lock:
            record_store._records[record.id] = terminal_record
        terminal = client.get(f"/api/decision-records/{proposed['id']}").json()

    for identity in MOCK_IDENTITIES:
        designate(client, identity.id)

    for identity in MOCK_IDENTITIES:
        select_identity(client, identity.id)
        content_edit = client.put(
            f"/api/decision-records/{proposed['id']}",
            json={"title": "Unauthorized terminal mutation"},
        )
        lifecycle_edit = client.put(
            f"/api/decision-records/{proposed['id']}",
            json={"status": "Draft"},
        )
        version_edit = client.put(
            f"/api/decision-records/{proposed['id']}",
            json={"version_content": "Unauthorized version mutation"},
        )
        resubmit = client.post(
            f"/api/decision-records/{proposed['id']}/submit"
        )
        alternate_decision = client.post(
            f"/api/decision-records/{proposed['id']}/decision",
            json={"outcome": "Accepted"},
        )

        assert content_edit.status_code == 409
        assert lifecycle_edit.status_code == 422
        assert version_edit.status_code == 422
        assert resubmit.status_code == 409
        assert alternate_decision.status_code == 409
        assert client.get(
            f"/api/decision-records/{proposed['id']}"
        ).json() == terminal


def test_tc_005_04_concurrent_conflicting_decisions_commit_one_outcome(
    client: TestClient,
) -> None:
    """TC-005-04: Accept/Reject races result in one terminal lifecycle outcome."""
    proposed = create_proposed(client)
    designate(client, APPROVER)
    designate(client, SECOND_APPROVER)
    start = Barrier(2)

    def decide(identity_id: str, outcome: str) -> httpx.Response:
        with TestClient(client.app) as actor_client:
            select_identity(actor_client, identity_id)
            start.wait(timeout=5)
            return actor_client.post(
                f"/api/decision-records/{proposed['id']}/decision",
                json={"outcome": outcome},
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        accept = executor.submit(decide, APPROVER, "Accepted")
        reject = executor.submit(decide, SECOND_APPROVER, "Rejected")
        responses = [accept.result(timeout=10), reject.result(timeout=10)]

    assert sorted(response.status_code for response in responses) == [200, 409]
    final = client.get(f"/api/decision-records/{proposed['id']}").json()
    assert final["status"] in ("Accepted", "Rejected")
    events = client.get(
        f"/api/decision-records/{proposed['id']}/audit-events"
    ).json()["events"]
    outcomes = [
        change["after"]
        for event in events
        for change in event["changes"]
        if change["field"] == "status"
        and change["before"] == "Proposed"
        and change["after"] in ("Accepted", "Rejected")
    ]
    assert outcomes == [final["status"]]
