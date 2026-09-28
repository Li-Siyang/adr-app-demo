from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from threading import Event

import pytest
import httpx
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.identities import MOCK_IDENTITIES, MockIdentity
from app.main import create_app
from app.records import (
    DecisionRecord,
    DecisionRecordCreate,
    DecisionRecordStore,
    DecisionRecordUpdate,
    RecordActionError,
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app()) as test_client:
        test_client.post("/api/mock-session", json={"identity_id": "maya-member"})
        yield test_client
    designated_approver_ids.clear()


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


def test_author_edits_draft_and_retains_draft_status(client: TestClient) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()
    payload = complete_payload()
    del payload["owner_id"]
    payload["title"] = "Adopt a revised service boundary"
    payload["tags"] = ["architecture"]

    response = client.put(
        f"/api/decision-records/{created['id']}",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["title"] == payload["title"]
    assert response.json()["tags"] == ["architecture"]
    assert response.json()["status"] == "Draft"
    assert client.get(f"/api/decision-records/{created['id']}").json() == response.json()


def test_non_author_cannot_edit_draft(client: TestClient) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})

    response = client.put(
        f"/api/decision-records/{created['id']}",
        json={"title": "Unauthorized change"},
    )

    assert response.status_code == 403
    retained = client.get(f"/api/decision-records/{created['id']}").json()
    assert retained["title"] == created["title"]
    assert retained["status"] == "Draft"


def test_complete_authored_draft_with_approver_becomes_proposed(
    client: TestClient,
) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()
    designated_approver_ids.add("arun-approver")

    response = client.post(f"/api/decision-records/{created['id']}/submit")

    assert response.status_code == 200
    assert response.json()["status"] == "Proposed"
    assert (
        client.get(f"/api/decision-records/{created['id']}").json()["status"]
        == "Proposed"
    )


def test_submission_reports_every_missing_field_and_required_approver(
    client: TestClient,
) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()
    edited = client.put(
        f"/api/decision-records/{created['id']}",
        json={"title": " ", "rationale": "", "tags": []},
    )
    assert edited.status_code == 200

    response = client.post(f"/api/decision-records/{created['id']}/submit")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert set(detail["missing_fields"]) == {"title", "rationale", "tags"}
    assert "at least one designated approver" in detail["approver"].lower()
    assert client.get(f"/api/decision-records/{created['id']}").json()["status"] == (
        "Draft"
    )


def test_non_author_cannot_submit_draft(client: TestClient) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()
    designated_approver_ids.add("arun-approver")
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})

    response = client.post(f"/api/decision-records/{created['id']}/submit")

    assert response.status_code == 403
    assert client.get(f"/api/decision-records/{created['id']}").json()["status"] == (
        "Draft"
    )


@pytest.mark.parametrize("actor", MOCK_IDENTITIES)
def test_abandoned_replacement_draft_cannot_be_edited_or_submitted(
    actor: MockIdentity,
) -> None:
    store = DecisionRecordStore()
    author = MOCK_IDENTITIES[0]
    record = store.create(DecisionRecordCreate(**complete_payload()), author)
    record.abandoned = True

    with pytest.raises(RecordActionError, match="Abandoned"):
        store.update(record.id, DecisionRecordUpdate(title="Changed"), actor)
    with pytest.raises(RecordActionError, match="Abandoned"):
        store.submit(
            record.id,
            actor,
            has_designated_approver=True,
        )

    retained = store.get(record.id)
    assert retained is not None
    assert retained.title == complete_payload()["title"]
    assert retained.status == "Draft"
    assert retained.abandoned is True


@pytest.mark.parametrize("field", ("title", "decision_date", "tags"))
def test_edit_rejects_explicit_null_required_fields(
    client: TestClient,
    field: str,
) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()

    response = client.put(
        f"/api/decision-records/{created['id']}",
        json={field: None},
    )

    assert response.status_code == 422
    assert client.get(f"/api/decision-records/{created['id']}").json() == created


def test_draft_edit_cannot_transfer_ownership(client: TestClient) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()

    response = client.put(
        f"/api/decision-records/{created['id']}",
        json={"owner_id": "arun-approver"},
    )

    assert response.status_code == 422
    retained = client.get(f"/api/decision-records/{created['id']}").json()
    assert retained["owner"] == created["owner"]


def test_submitted_record_cannot_be_edited_or_submitted_again(
    client: TestClient,
) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()
    designated_approver_ids.add("arun-approver")
    assert (
        client.post(f"/api/decision-records/{created['id']}/submit").status_code
        == 200
    )

    edit = client.put(
        f"/api/decision-records/{created['id']}",
        json={"title": "Changed after submission"},
    )
    resubmit = client.post(f"/api/decision-records/{created['id']}/submit")

    assert edit.status_code == 409
    assert resubmit.status_code == 409


def test_submission_and_approver_removal_are_serialized(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A designation change cannot interleave with an in-flight submission."""
    created = client.post("/api/decision-records", json=complete_payload()).json()
    designated_approver_ids.add("arun-approver")

    entered_critical_section = Event()
    release_submission = Event()
    original_submit = DecisionRecordStore.submit

    def synchronized_submit(
        self: DecisionRecordStore,
        *args: object,
        **kwargs: object,
    ) -> DecisionRecord:
        # The endpoint holds governance_lock when the store submit runs.
        entered_critical_section.set()
        assert release_submission.wait(timeout=2)
        return original_submit(self, *args, **kwargs)

    monkeypatch.setattr(DecisionRecordStore, "submit", synchronized_submit)

    admin = TestClient(client.app)
    admin.post("/api/mock-session", json={"identity_id": "zoe-admin"})

    with ThreadPoolExecutor(max_workers=2) as executor:
        submission = executor.submit(
            lambda: client.post(f"/api/decision-records/{created['id']}/submit")
        )
        assert entered_critical_section.wait(timeout=2)

        removal = executor.submit(
            lambda: admin.delete("/api/approvers/arun-approver")
        )
        with pytest.raises(FutureTimeoutError):
            removal.result(timeout=0.3)

        release_submission.set()
        submitted: httpx.Response = submission.result(timeout=2)
        removed: httpx.Response = removal.result(timeout=2)

    assert submitted.status_code == 200
    assert submitted.json()["status"] == "Proposed"
    assert removed.status_code == 200
    assert removed.json() == {"approvers": []}
    assert client.get(f"/api/decision-records/{created['id']}").json()["status"] == (
        "Proposed"
    )
