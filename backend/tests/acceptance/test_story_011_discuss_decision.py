"""Validation-Agent-owned acceptance coverage for STORY-011.

Expected behavior comes from Requirement Definition 1.3 and TEST-001 2.1,
not from the implementation or its developer-owned tests.
"""

from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

AUTHOR = "maya-member"
OTHER_TEAM_MEMBER = "arun-approver"


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        select(test_client, AUTHOR)
        yield test_client


def select(client: TestClient, identity_id: str) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": identity_id},
    )
    assert response.status_code == 200


def create_record(client: TestClient) -> dict:
    response = client.post(
        "/api/decision-records",
        json={
            "title": "Validate decision discussion",
            "context": "The decision needs retained discussion.",
            "decision": "Support top-level comments.",
            "rationale": "Mock attribution preserves context.",
            "alternatives_considered": "Keep discussion elsewhere.",
            "consequences": "Comments remain on the decision record.",
            "owner_id": AUTHOR,
            "decision_date": "2026-10-01",
            "tags": ["story-011-validation"],
        },
    )
    assert response.status_code == 201
    return response.json()


def add_comment(client: TestClient, record_id: str, content: str) -> dict:
    response = client.post(
        f"/api/decision-records/{record_id}/comments",
        json={"content": content},
    )
    assert response.status_code == 201
    return response.json()


def get_record(client: TestClient, record_id: str) -> dict:
    response = client.get(f"/api/decision-records/{record_id}")
    assert response.status_code == 200
    return response.json()


def comment_audit_events(client: TestClient, record_id: str) -> list[dict]:
    response = client.get(f"/api/decision-records/{record_id}/audit-events")
    assert response.status_code == 200
    return [
        event
        for event in response.json()["events"]
        if event["event_type"] == "comment_deleted"
    ]


def test_tc_011_01_adds_visible_attributed_top_level_comment(
    client: TestClient,
) -> None:
    record = create_record(client)

    comment = add_comment(
        client,
        record["id"],
        "Retain this decision context.",
    )
    retrieved = get_record(client, record["id"])

    assert retrieved["comments"] == [comment]
    assert comment["content"] == "Retain this decision context."
    assert comment["author"]["id"] == AUTHOR
    assert comment["author"]["display_name"] == "Maya Member"
    assert comment["deleted"] is False
    assert "parent_id" not in comment
    assert "replies" not in comment


def test_tc_011_02_author_soft_deletion_retains_attributed_audit_evidence(
    client: TestClient,
) -> None:
    record = create_record(client)
    comment = add_comment(client, record["id"], "Delete my own comment.")

    response = client.delete(
        f"/api/decision-records/{record['id']}/comments/{comment['id']}"
    )

    assert response.status_code == 200
    assert response.json()["content"] == "[deleted]"
    assert response.json()["deleted"] is True
    retained = get_record(client, record["id"])["comments"]
    assert len(retained) == 1
    assert retained[0]["id"] == comment["id"]
    assert retained[0]["content"] == "[deleted]"
    assert retained[0]["author"]["id"] == AUTHOR

    events = comment_audit_events(client, record["id"])
    assert len(events) == 1
    assert events[0]["actor"]["id"] == AUTHOR
    assert events[0]["subject_id"] == record["id"]
    assert events[0]["occurred_at"]
    assert events[0]["changes"] == [
        {
            "field": f"comment.{comment['id']}.content",
            "before": "Delete my own comment.",
            "after": "[deleted]",
        },
        {
            "field": f"comment.{comment['id']}.deleted",
            "before": False,
            "after": True,
        },
    ]
    assert client.get(f"/api/audit-events/{events[0]['id']}").json() == events[0]


def test_tc_011_03_non_author_deletion_is_denied_without_change(
    client: TestClient,
) -> None:
    record = create_record(client)
    comment = add_comment(client, record["id"], "Only I may delete this.")
    select(client, OTHER_TEAM_MEMBER)

    response = client.delete(
        f"/api/decision-records/{record['id']}/comments/{comment['id']}"
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only the comment author may delete it."
    assert get_record(client, record["id"])["comments"] == [comment]
    assert comment_audit_events(client, record["id"]) == []


def test_tc_011_04_concurrent_deletion_preserves_one_attributed_tombstone(
    client: TestClient,
) -> None:
    record = create_record(client)
    comment = add_comment(client, record["id"], "Delete concurrently.")
    path = f"/api/decision-records/{record['id']}/comments/{comment['id']}"

    with ThreadPoolExecutor(max_workers=8) as executor:
        responses = list(executor.map(lambda _: client.delete(path), range(16)))

    assert sum(response.status_code == 200 for response in responses) == 1
    assert sum(response.status_code == 409 for response in responses) == 15
    retained = get_record(client, record["id"])["comments"]
    assert len(retained) == 1
    assert retained[0]["id"] == comment["id"]
    assert retained[0]["content"] == "[deleted]"
    assert retained[0]["deleted"] is True

    events = comment_audit_events(client, record["id"])
    assert len(events) == 1
    assert events[0]["actor"]["id"] == AUTHOR
    assert events[0]["changes"][0]["before"] == "Delete concurrently."
    assert events[0]["changes"][0]["after"] == "[deleted]"
