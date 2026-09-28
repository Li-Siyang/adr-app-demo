"""Test-Agent-owned acceptance tests for STORY-004 (TS-004).

Expected behavior is derived from the approved Requirement Definition and
TEST-001 Test Design, not from the implementation.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.identities import MOCK_IDENTITIES
from app.main import create_app

AUTHOR = "maya-member"
OTHER_USER = "arun-approver"


@pytest.fixture
def client() -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app()) as test_client:
        select_identity(test_client, AUTHOR)
        yield test_client
    designated_approver_ids.clear()


def select_identity(client: TestClient, identity_id: str) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": identity_id},
    )
    assert response.status_code == 200


def complete_draft() -> dict[str, object]:
    return {
        "title": "Adopt an explicit persistence boundary",
        "context": "Persistence and transport concerns are currently mixed.",
        "decision": "Introduce a dedicated persistence module.",
        "rationale": "A single responsibility keeps future change isolated.",
        "alternatives_considered": "Keep one module and accept the coupling.",
        "consequences": "Two focused modules must be maintained.",
        "owner_id": OTHER_USER,
        "decision_date": "2026-09-11",
        "tags": ["architecture", "backend"],
    }


def create_draft(client: TestClient) -> dict[str, object]:
    response = client.post("/api/decision-records", json=complete_draft())
    assert response.status_code == 201
    return response.json()


def retained_record(client: TestClient, record_id: str) -> dict[str, object]:
    response = client.get(f"/api/decision-records/{record_id}")
    assert response.status_code == 200
    return response.json()


def test_tc_004_01_author_edits_and_retains_an_ordinary_draft(
    client: TestClient,
) -> None:
    """TC-004-01: author content edits persist without changing Draft status."""
    draft = create_draft(client)

    response = client.put(
        f"/api/decision-records/{draft['id']}",
        json={
            "title": "Adopt a dedicated persistence boundary",
            "rationale": "It isolates persistence changes from transport.",
            "tags": ["architecture"],
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Draft"
    retained = retained_record(client, str(draft["id"]))
    assert retained["title"] == "Adopt a dedicated persistence boundary"
    assert retained["rationale"] == (
        "It isolates persistence changes from transport."
    )
    assert retained["tags"] == ["architecture"]


def test_tc_004_02_non_author_edit_is_denied_without_change(
    client: TestClient,
) -> None:
    """TC-004-02: another Mock identity cannot alter the author's Draft."""
    draft = create_draft(client)
    select_identity(client, OTHER_USER)

    response = client.put(
        f"/api/decision-records/{draft['id']}",
        json={"title": "Unauthorized replacement title"},
    )

    assert response.status_code == 403
    retained = retained_record(client, str(draft["id"]))
    assert retained == draft


def test_tc_004_03_complete_draft_with_approver_becomes_proposed(
    client: TestClient,
) -> None:
    """TC-004-03 / AC-005: valid author submission performs Draft to Proposed."""
    draft = create_draft(client)
    designated_approver_ids.add(OTHER_USER)

    page = client.get("/app")
    script = client.get("/static/app.js")
    response = client.post(f"/api/decision-records/{draft['id']}/submit")

    assert page.status_code == 200
    assert script.status_code == 200
    assert "Submit Draft" in script.text
    assert "/submit" in script.text
    assert response.status_code == 200
    assert response.json()["status"] == "Proposed"
    assert retained_record(client, str(draft["id"]))["status"] == "Proposed"


def test_tc_004_04_submission_reports_all_gaps_and_approver_action(
    client: TestClient,
) -> None:
    """TC-004-04 / AC-004, AC-024: all gaps are actionable and state is stable."""
    draft = create_draft(client)
    changed = client.put(
        f"/api/decision-records/{draft['id']}",
        json={
            "title": " ",
            "context": "",
            "rationale": "   ",
            "tags": [],
        },
    )
    assert changed.status_code == 200

    response = client.post(f"/api/decision-records/{draft['id']}/submit")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert set(detail["missing_fields"]) == {
        "title",
        "context",
        "rationale",
        "tags",
    }
    assert "at least one designated approver" in detail["approver"].lower()
    assert retained_record(client, str(draft["id"]))["status"] == "Draft"


@pytest.mark.parametrize("actor_id", [identity.id for identity in MOCK_IDENTITIES])
def test_tc_004_05_every_role_is_denied_on_an_abandoned_draft(
    client: TestClient,
    actor_id: str,
) -> None:
    """TC-004-05 / AC-047: Abandoned content and lifecycle remain immutable."""
    draft = create_draft(client)
    record_id = str(draft["id"])
    stored = client.app.state.record_store.get(record_id)
    assert stored is not None
    stored.abandoned = True
    before = retained_record(client, record_id)
    designated_approver_ids.add(OTHER_USER)
    select_identity(client, actor_id)

    edit = client.put(
        f"/api/decision-records/{record_id}",
        json={"title": "Forbidden abandoned edit"},
    )
    submit = client.post(f"/api/decision-records/{record_id}/submit")

    assert edit.status_code == 409
    assert submit.status_code == 409
    assert retained_record(client, record_id) == before
    assert before["status"] == "Draft"
    assert before["abandoned"] is True
