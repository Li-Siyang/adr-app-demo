from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        test_client.post("/api/mock-session", json={"identity_id": "maya-member"})
        yield test_client


def complete_payload() -> dict[str, object]:
    return {
        "title": "Adopt the service boundary",
        "context": "The current module has multiple responsibilities.",
        "decision": "Split the persistence boundary from the API.",
        "rationale": "The boundary keeps future changes isolated.",
        "alternatives_considered": "Keep the existing module unchanged.",
        "consequences": "There are two focused modules to maintain.",
        "owner_id": "maya-member",
        "decision_date": "2026-09-11",
        "tags": ["architecture", "backend"],
    }


def test_creates_complete_draft_with_author_owner_tags_and_notice(
    client: TestClient,
) -> None:
    response = client.post("/api/decision-records", json=complete_payload())

    assert response.status_code == 201
    record = response.json()
    assert record["status"] == "Draft"
    assert record["author"]["id"] == "maya-member"
    assert record["owner"]["id"] == "maya-member"
    assert record["tags"] == ["architecture", "backend"]
    assert "demo or synthetic data" in record["data_classification_notice"].lower()

    listed = client.get("/api/decision-records")
    assert listed.json()["records"][0]["id"] == record["id"]


@pytest.mark.parametrize(
    "missing_field",
    [
        "title",
        "context",
        "decision",
        "rationale",
        "alternatives_considered",
        "consequences",
        "owner_id",
        "decision_date",
        "tags",
    ],
)
def test_rejects_draft_without_each_required_field(
    client: TestClient, missing_field: str
) -> None:
    payload = complete_payload()
    del payload[missing_field]

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    assert client.get("/api/decision-records").json() == {"records": []}


def test_requires_selected_identity_to_create_draft() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/decision-records", json=complete_payload())

    assert response.status_code == 400
    assert response.json()["detail"] == "Choose a Mock identity before continuing."


def test_rejects_unknown_owner_without_creating_draft(client: TestClient) -> None:
    payload = complete_payload()
    payload["owner_id"] = "not-configured"

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    assert "owner does not exist" in response.json()["detail"]
    assert client.get("/api/decision-records").json() == {"records": []}


def test_requires_at_least_one_non_blank_unique_tag(client: TestClient) -> None:
    payload = complete_payload()
    payload["tags"] = ["architecture", " "]

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    assert client.get("/api/decision-records").json() == {"records": []}


def test_retrieves_created_draft_by_id(client: TestClient) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()

    response = client.get(f"/api/decision-records/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_unknown_decision_record_returns_not_found(client: TestClient) -> None:
    response = client.get("/api/decision-records/not-configured")

    assert response.status_code == 404
    assert response.json()["detail"] == "The decision record does not exist."


def test_rejects_duplicate_tags_without_creating_draft(client: TestClient) -> None:
    payload = complete_payload()
    payload["tags"] = ["architecture", "architecture"]

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    assert client.get("/api/decision-records").json() == {"records": []}
