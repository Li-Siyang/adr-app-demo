from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.records import DecisionRecordCreate, DecisionRecordStore
from app.identities import MOCK_IDENTITIES


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


def test_filters_decision_records_by_one_exact_tag(client: TestClient) -> None:
    exact_match = complete_payload()
    exact_match["title"] = "Exact architecture record"
    exact_match["tags"] = ["architecture", "backend"]
    partial_match = complete_payload()
    partial_match["title"] = "Longer tag record"
    partial_match["tags"] = ["architecture-review"]
    unrelated = complete_payload()
    unrelated["title"] = "Unrelated record"
    unrelated["tags"] = ["frontend"]
    for payload in (exact_match, partial_match, unrelated):
        assert client.post("/api/decision-records", json=payload).status_code == 201

    response = client.get(
        "/api/decision-records",
        params={"tag": "architecture"},
    )

    assert response.status_code == 200
    records = response.json()["records"]
    assert [record["title"] for record in records] == ["Exact architecture record"]


def test_record_store_supports_concurrent_create_and_list() -> None:
    store = DecisionRecordStore()
    payload = DecisionRecordCreate(**complete_payload())
    author = MOCK_IDENTITIES[0]

    def create_record() -> None:
        store.create(payload, author)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(create_record) for _ in range(20)]
        for future in futures:
            future.result()
        listed = store.list()

    assert len(listed) == 20
