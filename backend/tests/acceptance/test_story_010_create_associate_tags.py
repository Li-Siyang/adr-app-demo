"""Validation-Agent acceptance tests for STORY-010 (TS-010).

Expected behavior comes from the approved Requirement Definition and TEST-001,
not from the implementation.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.main import create_app

TEAM_MEMBER = "maya-member"


@pytest.fixture
def client() -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app()) as test_client:
        selected = test_client.post(
            "/api/mock-session",
            json={"identity_id": TEAM_MEMBER},
        )
        assert selected.status_code == 200
        yield test_client
    designated_approver_ids.clear()


def record_payload(tags: list[str]) -> dict[str, object]:
    return {
        "title": "Decision with selected tags",
        "context": "The team needs to retain and discover a decision.",
        "decision": "Associate the selected tags with the record.",
        "rationale": "Tags make the record discoverable.",
        "alternatives_considered": "Leave the record untagged.",
        "consequences": "The record is discoverable by each selected tag.",
        "owner_id": TEAM_MEMBER,
        "decision_date": "2026-09-30",
        "tags": tags,
    }


def test_tc_010_01_created_tag_is_available_and_retained_on_record(
    client: TestClient,
) -> None:
    """TC-010-01 / CR-FR-025 / AC-029."""
    tag_name = "story-010-discovery"

    created_tag = client.post("/api/tags", json={"name": tag_name})

    assert created_tag.status_code == 201
    assert created_tag.json()["name"] == tag_name
    available_tags = client.get("/api/tags")
    assert available_tags.status_code == 200
    assert tag_name in available_tags.json()["tags"]

    created_record = client.post(
        "/api/decision-records",
        json=record_payload([tag_name]),
    )
    assert created_record.status_code == 201
    record_id = created_record.json()["id"]

    retrieved_record = client.get(f"/api/decision-records/{record_id}")
    assert retrieved_record.status_code == 200
    assert retrieved_record.json()["tags"] == [tag_name]


def test_tc_010_02_multiple_selected_tags_are_retained_and_discoverable(
    client: TestClient,
) -> None:
    """TC-010-02 / CR-FR-005, CR-FR-025 / AC-029."""
    selected_tags = ["story-010-governance", "story-010-architecture"]
    for tag_name in selected_tags:
        response = client.post("/api/tags", json={"name": tag_name})
        assert response.status_code == 201

    created_record = client.post(
        "/api/decision-records",
        json=record_payload(selected_tags),
    )
    assert created_record.status_code == 201
    record_id = created_record.json()["id"]

    retrieved_record = client.get(f"/api/decision-records/{record_id}")
    assert retrieved_record.status_code == 200
    assert set(retrieved_record.json()["tags"]) == set(selected_tags)

    for tag_name in selected_tags:
        matching_records = client.get(
            "/api/decision-records",
            params={"tag": tag_name},
        )
        assert matching_records.status_code == 200
        assert [record["id"] for record in matching_records.json()["records"]] == [
            record_id
        ]


def test_tag_endpoints_reject_missing_identity_blank_name_and_duplicate(
    client: TestClient,
) -> None:
    """Review regression: tag API errors are explicit and leave tag state unchanged."""
    unauthenticated = TestClient(client.app)
    assert unauthenticated.post(
        "/api/tags",
        json={"name": "review-validation"},
    ).status_code == 400

    blank = client.post("/api/tags", json={"name": "  "})
    assert blank.status_code == 422
    assert "review-validation" not in client.get("/api/tags").json()["tags"]

    created = client.post("/api/tags", json={"name": "review-validation"})
    assert created.status_code == 201
    duplicate = client.post("/api/tags", json={"name": "review-validation"})
    assert duplicate.status_code == 409
    assert client.get("/api/tags").json()["tags"] == ["review-validation"]


def test_blank_tag_update_is_atomic_for_draft_and_proposed_records(
    client: TestClient,
) -> None:
    """Review regression: invalid tag edits do not mutate records or audit history."""
    created = client.post(
        "/api/decision-records",
        json=record_payload(["review-validation"]),
    )
    assert created.status_code == 201
    record_id = created.json()["id"]

    invalid_draft_update = client.put(
        f"/api/decision-records/{record_id}",
        json={"tags": ["   "]},
    )
    assert invalid_draft_update.status_code == 422
    retained_draft = client.get(f"/api/decision-records/{record_id}").json()
    assert retained_draft["status"] == "Draft"
    assert retained_draft["tags"] == ["review-validation"]

    designated_approver_ids.add("arun-approver")
    submitted = client.post(f"/api/decision-records/{record_id}/submit")
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "Proposed"
    invalid_proposed_update = client.put(
        f"/api/decision-records/{record_id}",
        json={"tags": ["   "]},
    )
    assert invalid_proposed_update.status_code == 422

    retained_proposal = client.get(f"/api/decision-records/{record_id}").json()
    assert retained_proposal["status"] == "Proposed"
    assert retained_proposal["tags"] == ["review-validation"]
    audit_events = client.get(
        f"/api/decision-records/{record_id}/audit-events"
    )
    assert audit_events.status_code == 200
    assert audit_events.json()["events"] == []
