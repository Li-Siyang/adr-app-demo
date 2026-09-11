"""Test-Agent-owned acceptance tests for STORY-003 (TS-003).

Expected behavior is derived from the approved Requirement Definition and
TEST-001 Test Design, not from the implementation.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

AUTHOR = "maya-member"
DISTINCT_OWNER = "arun-approver"

REQUIRED_FIELDS = (
    "title",
    "context",
    "decision",
    "rationale",
    "alternatives_considered",
    "consequences",
    "owner_id",
    "decision_date",
    "tags",
)

PROHIBITED_DATA_PHRASES = (
    "demo or synthetic data",
    "real internal confidential",
    "regulated personal information",
    "health information",
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        assert (
            test_client.post(
                "/api/mock-session", json={"identity_id": AUTHOR}
            ).status_code
            == 200
        )
        yield test_client


def complete_draft() -> dict[str, object]:
    return {
        "title": "Adopt an explicit persistence boundary",
        "context": "Persistence and transport concerns are currently mixed.",
        "decision": "Introduce a dedicated persistence module.",
        "rationale": "A single responsibility keeps future change isolated.",
        "alternatives_considered": "Keep one module and accept the coupling.",
        "consequences": "Two focused modules must be maintained.",
        "owner_id": DISTINCT_OWNER,
        "decision_date": "2026-09-11",
        "tags": ["architecture", "backend"],
    }


def stored_records(client: TestClient) -> list[dict[str, object]]:
    response = client.get("/api/decision-records")
    assert response.status_code == 200
    return response.json()["records"]


def normalized_text(value: str) -> str:
    return " ".join(value.split()).lower()


def test_tc_003_01_draft_retains_all_required_content(client: TestClient) -> None:
    """TC-003-01 / AC-002: a complete Draft is retained with all approved content."""
    payload = complete_draft()

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 201
    record = response.json()
    assert record["status"] == "Draft"
    for field in (
        "title",
        "context",
        "decision",
        "rationale",
        "alternatives_considered",
        "consequences",
    ):
        assert record[field] == payload[field]
    assert record["decision_date"] == payload["decision_date"]
    assert record["tags"] == payload["tags"]

    persisted = stored_records(client)
    assert len(persisted) == 1
    assert persisted[0]["id"] == record["id"]


def test_tc_003_01_author_and_owner_are_separate_attributes(
    client: TestClient,
) -> None:
    """TC-003-01 / CR-FR-006A: author attribution is distinct from ownership."""
    response = client.post("/api/decision-records", json=complete_draft())

    record = response.json()
    assert record["author"]["id"] == AUTHOR
    assert record["owner"]["id"] == DISTINCT_OWNER
    assert record["author"]["id"] != record["owner"]["id"]
    assert record["author"]["is_mock"] is True
    assert record["owner"]["is_mock"] is True


def test_tc_003_01_draft_is_attributed_to_the_selected_mock_identity() -> None:
    """TC-003-01 / AC-002: the selected Mock identity becomes the author."""
    with TestClient(create_app()) as client:
        client.post("/api/mock-session", json={"identity_id": DISTINCT_OWNER})
        record = client.post("/api/decision-records", json=complete_draft()).json()

    assert record["author"]["id"] == DISTINCT_OWNER


@pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
def test_tc_003_02_each_missing_required_field_is_identified(
    client: TestClient, missing_field: str
) -> None:
    """TC-003-02 / AC-004: an incomplete Draft is rejected and the gap is named."""
    payload = complete_draft()
    del payload[missing_field]

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    reported = {
        field
        for item in response.json()["detail"]
        for field in item.get("loc", [])
        if isinstance(field, str)
    }
    assert missing_field in reported
    assert stored_records(client) == []


def test_tc_003_02_every_missing_required_field_is_reported_together(
    client: TestClient,
) -> None:
    """TC-003-02 / AC-004: multiple omissions are all identified in one attempt."""
    payload = complete_draft()
    omitted = ("title", "rationale", "consequences", "tags")
    for field in omitted:
        del payload[field]

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    reported = {
        field
        for item in response.json()["detail"]
        for field in item.get("loc", [])
        if isinstance(field, str)
    }
    assert set(omitted).issubset(reported)
    assert stored_records(client) == []


@pytest.mark.parametrize("blank_field", ("title", "context", "decision", "rationale"))
def test_tc_003_02_blank_required_content_is_rejected(
    client: TestClient, blank_field: str
) -> None:
    """TC-003-02 / CR-FR-004: whitespace does not satisfy a required field."""
    payload = complete_draft()
    payload[blank_field] = "   "

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    assert stored_records(client) == []


def test_tc_003_02_draft_requires_at_least_one_tag(client: TestClient) -> None:
    """TC-003-02 / CR-FR-005: at least one tag is required boundary content."""
    payload = complete_draft()
    payload["tags"] = []

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    assert stored_records(client) == []


def test_tc_003_02_single_tag_boundary_is_accepted(client: TestClient) -> None:
    """TC-003-02 / CR-FR-005: exactly one tag satisfies the minimum boundary."""
    payload = complete_draft()
    payload["tags"] = ["architecture"]

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 201
    assert response.json()["tags"] == ["architecture"]


@pytest.mark.parametrize("phrase", PROHIBITED_DATA_PHRASES)
def test_tc_003_03_creation_screen_states_the_data_boundary(
    client: TestClient, phrase: str
) -> None:
    """TC-003-03 / AC-037: the creation screen carries the complete notice."""
    response = client.get("/app")

    assert response.status_code == 200
    assert phrase in normalized_text(response.text)


@pytest.mark.parametrize("phrase", PROHIBITED_DATA_PHRASES)
def test_tc_003_03_entry_screen_states_the_data_boundary(
    client: TestClient, phrase: str
) -> None:
    """TC-003-03 / AC-037: the entry screen carries the complete notice."""
    response = client.get("/")

    assert response.status_code == 200
    assert phrase in normalized_text(response.text)


def test_tc_003_03_retained_draft_carries_the_data_boundary_notice(
    client: TestClient,
) -> None:
    """TC-003-03 / CR-BR-010: the retained record repeats the approved notice."""
    record = client.post("/api/decision-records", json=complete_draft()).json()

    notice = normalized_text(record["data_classification_notice"])
    for phrase in PROHIBITED_DATA_PHRASES:
        assert phrase in notice


def test_draft_creation_requires_a_selected_mock_identity() -> None:
    """CR-FR-003: authorship cannot be established without an actor."""
    with TestClient(create_app()) as client:
        response = client.post("/api/decision-records", json=complete_draft())

        assert response.status_code == 400
        assert stored_records(client) == []


def test_unknown_owner_is_rejected_without_retaining_a_draft(
    client: TestClient,
) -> None:
    """CR-FR-006A: ownership must reference a configured Mock identity."""
    payload = complete_draft()
    payload["owner_id"] = "not-configured"

    response = client.post("/api/decision-records", json=payload)

    assert response.status_code == 422
    assert stored_records(client) == []


def test_records_do_not_leak_across_application_instances() -> None:
    """CR-FR-003: a new application instance starts without retained Drafts."""
    with TestClient(create_app()) as first:
        first.post("/api/mock-session", json={"identity_id": AUTHOR})
        assert (
            first.post("/api/decision-records", json=complete_draft()).status_code == 201
        )

    with TestClient(create_app()) as second:
        assert stored_records(second) == []
