"""Developer-owned tests for STORY-010 tag registry and API behavior."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.main import create_app
from app.tags import DuplicateTagError, TagStore


@pytest.fixture
def client() -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app()) as test_client:
        yield test_client
    designated_approver_ids.clear()


def select_team_member(client: TestClient) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": "maya-member"},
    )
    assert response.status_code == 200


def create_record(client: TestClient) -> dict[str, object]:
    select_team_member(client)
    response = client.post(
        "/api/decision-records",
        json={
            "title": "Decision tagged for discovery",
            "context": "The team needs a retained decision.",
            "decision": "Keep its existing tag associations intact.",
            "rationale": "Failed edits must not partially mutate a record.",
            "alternatives_considered": "Apply invalid tags before validation.",
            "consequences": "The record remains consistent.",
            "owner_id": "maya-member",
            "decision_date": "2026-09-30",
            "tags": ["architecture"],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_created_tag_is_available_for_association() -> None:
    store = TagStore()

    created = store.create("architecture")

    assert created == "architecture"
    assert store.list() == ["architecture"]


def test_tag_names_are_trimmed_and_listed_in_sorted_order() -> None:
    store = TagStore()

    store.create(" governance ")
    store.create("architecture")

    assert store.list() == ["architecture", "governance"]


def test_exact_duplicate_tag_creation_is_rejected() -> None:
    store = TagStore()
    store.create("architecture")

    with pytest.raises(DuplicateTagError):
        store.create("architecture")

    assert store.list() == ["architecture"]


def test_blank_tag_names_are_rejected() -> None:
    store = TagStore()

    with pytest.raises(ValueError, match="must not be blank"):
        store.create("  ")

    assert store.list() == []


def test_associated_record_tags_are_registered_idempotently() -> None:
    store = TagStore()

    store.ensure(["architecture", "governance"])
    store.ensure(["governance", "testing"])

    assert store.list() == ["architecture", "governance", "testing"]


def test_tag_creation_requires_a_selected_mock_identity(
    client: TestClient,
) -> None:
    response = client.post("/api/tags", json={"name": "architecture"})

    assert response.status_code == 400
    assert client.get("/api/tags").status_code == 400


def test_tag_creation_rejects_blank_names(client: TestClient) -> None:
    select_team_member(client)

    response = client.post("/api/tags", json={"name": "  "})

    assert response.status_code == 422
    assert client.get("/api/tags").json()["tags"] == []


def test_tag_creation_rejects_an_exact_duplicate(client: TestClient) -> None:
    select_team_member(client)
    assert client.post("/api/tags", json={"name": "architecture"}).status_code == 201

    response = client.post("/api/tags", json={"name": "architecture"})

    assert response.status_code == 409
    assert client.get("/api/tags").json()["tags"] == ["architecture"]


def test_blank_tag_update_does_not_mutate_a_draft(client: TestClient) -> None:
    record = create_record(client)

    response = client.put(
        f"/api/decision-records/{record['id']}",
        json={"tags": ["   "]},
    )

    assert response.status_code == 422
    retained = client.get(f"/api/decision-records/{record['id']}").json()
    assert retained["status"] == "Draft"
    assert retained["tags"] == ["architecture"]


def test_blank_tag_update_does_not_restart_a_proposed_record_or_audit_it(
    client: TestClient,
) -> None:
    record = create_record(client)
    designated_approver_ids.add("arun-approver")
    submitted = client.post(f"/api/decision-records/{record['id']}/submit")
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "Proposed"

    response = client.put(
        f"/api/decision-records/{record['id']}",
        json={"tags": ["   "]},
    )

    assert response.status_code == 422
    retained = client.get(f"/api/decision-records/{record['id']}").json()
    assert retained["status"] == "Proposed"
    assert retained["tags"] == ["architecture"]
    audit_events = client.get(
        f"/api/decision-records/{record['id']}/audit-events"
    )
    assert audit_events.status_code == 200
    assert audit_events.json()["events"] == []
