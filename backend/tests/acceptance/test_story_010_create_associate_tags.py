"""Validation-Agent acceptance tests for STORY-010 (TS-010).

Expected behavior comes from the approved Requirement Definition and TEST-001,
not from the implementation.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

TEAM_MEMBER = "maya-member"


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        selected = test_client.post(
            "/api/mock-session",
            json={"identity_id": TEAM_MEMBER},
        )
        assert selected.status_code == 200
        yield test_client


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
