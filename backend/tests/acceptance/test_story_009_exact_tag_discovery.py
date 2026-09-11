"""Test-Agent-owned acceptance tests for STORY-009 (TS-009).

Expected behavior is derived from the approved Requirement Definition and
TEST-001 Test Design, not from the implementation.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

ACTOR = "maya-member"
TARGET_TAG = "architecture"


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        assert (
            test_client.post(
                "/api/mock-session",
                json={"identity_id": ACTOR},
            ).status_code
            == 200
        )
        yield test_client


def record_payload(title: str, tags: list[str]) -> dict[str, object]:
    return {
        "title": title,
        "context": "The team needs a discoverable decision.",
        "decision": "Retain the decision with searchable tags.",
        "rationale": "Exact tags make discovery predictable.",
        "alternatives_considered": "Use free-text partial matching.",
        "consequences": "Users select one exact tag.",
        "owner_id": ACTOR,
        "decision_date": "2026-09-11",
        "tags": tags,
    }


def create_record(
    client: TestClient,
    title: str,
    tags: list[str],
) -> dict[str, object]:
    response = client.post(
        "/api/decision-records",
        json=record_payload(title, tags),
    )
    assert response.status_code == 201
    return response.json()


def set_lifecycle_status(
    client: TestClient,
    record_id: str,
    lifecycle_status: str,
) -> None:
    record = client.app.state.record_store.get(record_id)
    assert record is not None
    record.status = lifecycle_status


def filter_by_tag(client: TestClient, tag: str) -> list[dict[str, object]]:
    response = client.get("/api/decision-records", params={"tag": tag})
    assert response.status_code == 200
    return response.json()["records"]


def test_tc_009_01_returns_matching_current_and_historical_records(
    client: TestClient,
) -> None:
    """TC-009-01 / AC-015: lifecycle state does not hide exact-tag matches."""
    expected_statuses = (
        "Draft",
        "Proposed",
        "Accepted",
        "Rejected",
        "Superseded",
    )
    expected_ids = set()
    for lifecycle_status in expected_statuses:
        record = create_record(
            client,
            f"{lifecycle_status} architecture decision",
            [TARGET_TAG],
        )
        expected_ids.add(record["id"])
        set_lifecycle_status(client, record["id"], lifecycle_status)

    records = filter_by_tag(client, TARGET_TAG)

    assert {record["id"] for record in records} == expected_ids
    assert {record["status"] for record in records} == set(expected_statuses)


@pytest.mark.skip(
    reason=(
        "BLOCKED PLANNING_GAP: the record model and API do not yet support "
        "the archived precondition assigned to STORY-012"
    )
)
def test_tc_009_01_returns_matching_archived_records() -> None:
    """TC-009-01 / AC-015: archived exact-tag matches remain discoverable."""


def test_tc_009_02_returns_only_records_with_the_complete_selected_tag(
    client: TestClient,
) -> None:
    """TC-009-02 / AC-015: containing text is not an exact tag match."""
    exact = create_record(
        client,
        "Exact match",
        [TARGET_TAG, "backend"],
    )
    create_record(client, "Longer tag", ["architecture-review"])
    create_record(client, "Shorter tag", ["arch"])
    create_record(client, "Unrelated tag", ["frontend"])

    records = filter_by_tag(client, TARGET_TAG)

    assert [record["id"] for record in records] == [exact["id"]]
    assert records[0]["tags"] == [TARGET_TAG, "backend"]


def test_related_story_003_tags_are_retained_for_discovery(
    client: TestClient,
) -> None:
    """CR-FR-005: every associated tag remains available to exact discovery."""
    record = create_record(
        client,
        "Multiple tag decision",
        [TARGET_TAG, "backend", "governance"],
    )

    for tag in record["tags"]:
        assert [item["id"] for item in filter_by_tag(client, tag)] == [record["id"]]


def test_unknown_exact_tag_returns_an_empty_collection(
    client: TestClient,
) -> None:
    """CR-FR-015: no records are returned when no assigned tag is exact."""
    create_record(client, "Known tag decision", [TARGET_TAG])

    assert filter_by_tag(client, "not-assigned") == []
