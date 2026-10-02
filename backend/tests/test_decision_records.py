from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from pathlib import Path
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
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
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


@pytest.mark.parametrize(
    ("record_status", "archived", "abandoned"),
    [
        pytest.param("Draft", False, False, id="draft"),
        pytest.param("Proposed", False, False, id="proposed"),
        pytest.param("Accepted", False, False, id="accepted"),
        pytest.param("Rejected", False, False, id="rejected"),
        pytest.param("Superseded", False, False, id="superseded"),
        pytest.param("Draft", False, True, id="abandoned-replacement"),
        pytest.param("Draft", True, False, id="archived"),
        pytest.param("Draft", True, True, id="archived-abandoned-replacement"),
    ],
)
def test_decision_record_delete_attempts_are_rejected_and_retained(
    client: TestClient,
    record_status: str,
    archived: bool,
    abandoned: bool,
) -> None:
    created = client.post("/api/decision-records", json=complete_payload()).json()
    store: DecisionRecordStore = client.app.state.record_store
    record = store.get(created["id"])
    assert record is not None
    if abandoned:
        designated_approver_ids.add("arun-approver")
        original_id = record.id
        assert client.post(
            f"/api/decision-records/{original_id}/submit"
        ).status_code == 200
        client.post("/api/mock-session", json={"identity_id": "arun-approver"})
        assert client.post(
            f"/api/decision-records/{original_id}/decision",
            json={"outcome": "Accepted"},
        ).status_code == 200
        client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
        replacement = client.post(
            f"/api/decision-records/{original_id}/replacements"
        )
        assert replacement.status_code == 201
        record_id = replacement.json()["id"]
        result = client.post(f"/api/decision-records/{record_id}/abandon")
        assert result.status_code == 200
        if archived:
            assert client.post(
                f"/api/decision-records/{record_id}/archive"
            ).status_code == 200
        retained = store.get(record_id)
        assert retained is not None
        assert retained.replaces_record_id == original_id
        original = store.get(original_id)
        assert original is not None
        assert record_id in original.replacement_record_ids
    else:
        retained = record.model_copy(
            update={"status": record_status, "archived": archived}
        )
        store._records[retained.id] = retained
        record_id = retained.id
    path = f"/api/decision-records/{record_id}"
    listed = client.get("/api/decision-records").json()["records"]

    assert client.delete(path).status_code == 405
    assert client.put(path, json={"deleted": True}).status_code == 422

    expected = retained.model_dump(mode="json")
    assert client.get(path).json() == expected
    assert client.get("/api/decision-records").json()["records"] == listed


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


def test_submitted_record_cannot_be_resubmitted_without_an_edit(
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
        json={},
    )
    resubmit = client.post(f"/api/decision-records/{created['id']}/submit")

    assert edit.status_code == 200
    assert edit.json()["status"] == "Proposed"
    assert resubmit.status_code == 409
    assert client.get(f"/api/decision-records/{created['id']}").json()["status"] == (
        "Proposed"
    )


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


def propose_record(client: TestClient) -> dict[str, object]:
    created = client.post("/api/decision-records", json=complete_payload()).json()
    designated_approver_ids.add("arun-approver")
    submitted = client.post(f"/api/decision-records/{created['id']}/submit")
    assert submitted.status_code == 200
    return submitted.json()


def accept_record(client: TestClient) -> dict[str, object]:
    proposed = propose_record(client)
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})
    accepted = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert accepted.status_code == 200
    return accepted.json()


@pytest.mark.parametrize("outcome", ["Accepted", "Rejected"])
def test_designated_approver_can_decide_and_transition_is_audited(
    client: TestClient,
    outcome: str,
) -> None:
    proposed = propose_record(client)
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})

    response = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": outcome},
    )

    assert response.status_code == 200
    assert response.json()["status"] == outcome
    events = client.get(
        f"/api/decision-records/{proposed['id']}/audit-events"
    ).json()["events"]
    lifecycle_event = next(
        event for event in events if event["changes"][0]["field"] == "status"
    )
    assert lifecycle_event["actor"]["id"] == "arun-approver"
    assert lifecycle_event["changes"][0] == {
        "field": "status",
        "before": "Proposed",
        "after": outcome,
    }


@pytest.mark.parametrize("outcome", ["Accepted", "Rejected"])
def test_non_approver_cannot_decide_a_proposal(
    client: TestClient,
    outcome: str,
) -> None:
    proposed = propose_record(client)

    response = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": outcome},
    )

    assert response.status_code == 403
    assert client.get(f"/api/decision-records/{proposed['id']}").json() == proposed


def test_non_author_cannot_edit_a_proposed_record(client: TestClient) -> None:
    proposed = propose_record(client)
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})

    response = client.put(
        f"/api/decision-records/{proposed['id']}",
        json={"title": "Unauthorized proposal edit"},
    )

    assert response.status_code == 403
    assert client.get(f"/api/decision-records/{proposed['id']}").json() == proposed


def test_decision_requires_a_selected_identity_and_supported_outcome(
    client: TestClient,
) -> None:
    proposed = propose_record(client)
    with TestClient(client.app) as anonymous:
        missing_identity = anonymous.post(
            f"/api/decision-records/{proposed['id']}/decision",
            json={"outcome": "Accepted"},
        )
    invalid_outcome = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Pending"},
    )

    assert missing_identity.status_code == 400
    assert invalid_outcome.status_code == 422
    assert client.get(f"/api/decision-records/{proposed['id']}").json() == proposed


@pytest.mark.parametrize("outcome", ["Accepted", "Rejected"])
def test_author_may_decide_their_proposal_when_designated(
    client: TestClient,
    outcome: str,
) -> None:
    proposed = client.post("/api/decision-records", json=complete_payload()).json()
    designated_approver_ids.add("maya-member")
    assert (
        client.post(f"/api/decision-records/{proposed['id']}/submit").status_code
        == 200
    )

    response = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": outcome},
    )

    assert response.status_code == 200
    assert response.json()["status"] == outcome


def test_proposed_author_edit_restarts_review_and_allows_resubmission(
    client: TestClient,
) -> None:
    proposed = propose_record(client)
    response = client.put(
        f"/api/decision-records/{proposed['id']}",
        json={"title": "Revised service boundary"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Revised service boundary"
    assert response.json()["status"] == "Draft"

    client.post("/api/mock-session", json={"identity_id": "arun-approver"})
    blocked_decision = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert blocked_decision.status_code == 409

    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    resubmitted = client.post(f"/api/decision-records/{proposed['id']}/submit")
    assert resubmitted.status_code == 200
    assert resubmitted.json()["status"] == "Proposed"
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})
    accepted = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Accepted"},
    )
    assert accepted.status_code == 200
    events = client.get(
        f"/api/decision-records/{proposed['id']}/audit-events"
    ).json()["events"]
    restart = next(
        event
        for event in events
        if any(
            change == {
                "field": "status",
                "before": "Proposed",
                "after": "Draft",
            }
            for change in event["changes"]
        )
    )
    assert restart["actor"]["id"] == "maya-member"
    assert {
        "field": "title",
        "before": "Adopt the service boundary",
        "after": "Revised service boundary",
    } in restart["changes"]


@pytest.mark.parametrize("terminal_status", ["Rejected", "Superseded"])
def test_terminal_record_is_immutable_for_every_mock_identity(
    client: TestClient,
    terminal_status: str,
) -> None:
    proposed = propose_record(client)
    if terminal_status == "Rejected":
        client.post("/api/mock-session", json={"identity_id": "arun-approver"})
        terminal = client.post(
            f"/api/decision-records/{proposed['id']}/decision",
            json={"outcome": "Rejected"},
        ).json()
    else:
        store = client.app.state.record_store
        record = store.get(str(proposed["id"]))
        assert record is not None
        store._records[record.id] = record.model_copy(update={"status": "Superseded"})
        terminal = client.get(f"/api/decision-records/{proposed['id']}").json()

    for identity in MOCK_IDENTITIES:
        client.post("/api/mock-session", json={"identity_id": identity.id})
        update = client.put(
            f"/api/decision-records/{proposed['id']}",
            json={"title": "Forbidden change"},
        )
        submit = client.post(f"/api/decision-records/{proposed['id']}/submit")
        decide = client.post(
            f"/api/decision-records/{proposed['id']}/decision",
            json={"outcome": "Accepted"},
        )
        assert update.status_code == 409
        assert submit.status_code == 409
        assert decide.status_code in (403, 409)
        assert client.get(f"/api/decision-records/{proposed['id']}").json() == terminal


def test_concurrent_conflicting_decisions_commit_one_outcome(
    client: TestClient,
) -> None:
    proposed = propose_record(client)
    designated_approver_ids.add("lee-admin-approver")

    def decide(identity_id: str, outcome: str) -> httpx.Response:
        with TestClient(client.app) as actor_client:
            actor_client.post(
                "/api/mock-session",
                json={"identity_id": identity_id},
            )
            return actor_client.post(
                f"/api/decision-records/{proposed['id']}/decision",
                json={"outcome": outcome},
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        accepted = executor.submit(decide, "arun-approver", "Accepted")
        rejected = executor.submit(decide, "lee-admin-approver", "Rejected")
        responses = [accepted.result(), rejected.result()]

    assert sorted(response.status_code for response in responses) == [200, 409]
    record = client.get(f"/api/decision-records/{proposed['id']}").json()
    assert record["status"] in ("Accepted", "Rejected")
    assert sum(
        event["changes"][0]["field"] == "status"
        and event["changes"][0]["before"] == "Proposed"
        for event in client.get(
            f"/api/decision-records/{proposed['id']}/audit-events"
        ).json()["events"]
    ) == 1


@pytest.mark.parametrize("action", ["edit", "decision"])
def test_audit_failure_does_not_commit_proposal_transition(
    action: str,
) -> None:
    store = DecisionRecordStore()
    author = MOCK_IDENTITIES[0]
    record = store.create(DecisionRecordCreate(**complete_payload()), author)
    proposed = store.submit(
        record.id,
        author,
        has_designated_approver=True,
    )

    def fail_audit(*_: object) -> None:
        raise OSError("audit store unavailable")

    with pytest.raises(OSError, match="audit store unavailable"):
        if action == "edit":
            store.update(
                record.id,
                DecisionRecordUpdate(title="Edited proposal"),
                author,
                record_change=fail_audit,
            )
        else:
            store.decide(
                record.id,
                "Accepted",
                record_change=fail_audit,
            )

    assert store.get(record.id) == proposed


def accepted_record_in_store() -> tuple[DecisionRecordStore, DecisionRecord]:
    store = DecisionRecordStore()
    author = MOCK_IDENTITIES[0]
    record = store.create(DecisionRecordCreate(**complete_payload()), author)
    proposed = store.submit(
        record.id,
        author,
        has_designated_approver=True,
    )
    accepted = store.decide(
        proposed.id,
        "Accepted",
        record_change=lambda *_: None,
    )
    return store, accepted


@pytest.mark.parametrize("actor", MOCK_IDENTITIES)
def test_accepted_record_cannot_be_edited_by_any_identity(
    client: TestClient,
    actor: MockIdentity,
) -> None:
    accepted = accept_record(client)
    client.post("/api/mock-session", json={"identity_id": actor.id})

    response = client.put(
        f"/api/decision-records/{accepted['id']}",
        json={"title": "Directly edited Accepted record"},
    )

    assert response.status_code == 409
    assert client.get(f"/api/decision-records/{accepted['id']}").json() == accepted


def test_only_administrator_can_create_replacement(client: TestClient) -> None:
    accepted = accept_record(client)

    response = client.post(
        f"/api/decision-records/{accepted['id']}/replacements"
    )

    assert response.status_code == 403
    assert client.get(f"/api/decision-records/{accepted['id']}").json() == accepted
    assert client.get("/api/decision-records").json()["records"] == [accepted]


@pytest.mark.parametrize(
    ("target_status", "outcome"),
    [
        ("Draft", None),
        ("Proposed", None),
        ("Rejected", "Rejected"),
        ("Superseded", None),
    ],
)
def test_replacement_creation_rejects_non_accepted_targets(
    target_status: str,
    outcome: str | None,
) -> None:
    store = DecisionRecordStore()
    author = MOCK_IDENTITIES[0]
    record = store.create(DecisionRecordCreate(**complete_payload()), author)
    if target_status != "Draft":
        proposed = store.submit(
            record.id,
            author,
            has_designated_approver=True,
        )
        if outcome is not None:
            store.decide(
                proposed.id,
                outcome,
                record_change=lambda *_: None,
            )
        if target_status == "Superseded":
            current = store.get(record.id)
            assert current is not None
            store._records[record.id] = current.model_copy(
                update={"status": "Superseded"}
            )

    before = store.get(record.id)
    assert before is not None
    with pytest.raises(RecordActionError, match="Accepted"):
        store.create_replacement(
            record.id,
            MOCK_IDENTITIES[2],
            record_change=lambda _: None,
        )
    assert store.get(record.id) == before


def test_replacement_creation_is_linked_and_allows_only_one_active_version() -> None:
    store, original = accepted_record_in_store()

    def try_create() -> DecisionRecord | None:
        try:
            return store.create_replacement(
                original.id,
                MOCK_IDENTITIES[2],
                record_change=lambda _: None,
            )
        except RecordActionError:
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        replacements = list(executor.map(lambda _: try_create(), range(2)))

    created = [replacement for replacement in replacements if replacement]
    assert len(created) == 1
    replacement = created[0]
    assert replacement.status == "Draft"
    assert replacement.abandoned is False
    assert replacement.replaces_record_id == original.id
    assert replacement.replacement_record_ids == []
    assert replacement.author == MOCK_IDENTITIES[2]
    assert replacement.owner == original.owner
    retained_original = store.get(original.id)
    assert retained_original is not None
    assert retained_original.status == "Accepted"
    assert retained_original.replacement_record_ids == [replacement.id]


def test_rejected_replacement_ends_active_interval_and_allows_another() -> None:
    store, original = accepted_record_in_store()
    replacement = store.create_replacement(
        original.id,
        MOCK_IDENTITIES[2],
        record_change=lambda _: None,
    )
    proposed = store.submit(
        replacement.id,
        replacement.author,
        has_designated_approver=True,
    )
    rejected = store.decide(
        proposed.id,
        "Rejected",
        record_change=lambda *_: None,
    )

    new_replacement = store.create_replacement(
        original.id,
        MOCK_IDENTITIES[2],
        record_change=lambda _: None,
    )

    assert rejected.status == "Rejected"
    assert new_replacement.status == "Draft"
    retained_original = store.get(original.id)
    assert retained_original is not None
    assert retained_original.status == "Accepted"
    assert retained_original.replacement_record_ids == [
        replacement.id,
        new_replacement.id,
    ]


def test_replacement_acceptance_atomically_supersedes_original() -> None:
    store, original = accepted_record_in_store()
    replacement = store.create_replacement(
        original.id,
        MOCK_IDENTITIES[2],
        record_change=lambda _: None,
    )
    proposed = store.submit(
        replacement.id,
        replacement.author,
        has_designated_approver=True,
    )
    recorded_transitions: list[
        tuple[
            DecisionRecord,
            DecisionRecord,
            tuple[DecisionRecord, DecisionRecord] | None,
        ]
    ] = []

    accepted = store.decide(
        proposed.id,
        "Accepted",
        record_change=lambda before, after, related: recorded_transitions.append(
            (before, after, related)
        ),
    )

    superseded = store.get(original.id)
    assert superseded is not None
    assert accepted.status == "Accepted"
    assert accepted.replaces_record_id == original.id
    assert superseded.status == "Superseded"
    assert superseded.replacement_record_ids == [replacement.id]
    related_transition = recorded_transitions[0][2]
    assert related_transition is not None
    assert related_transition[0].status == "Accepted"
    assert related_transition[0].replacement_record_ids == [replacement.id]
    assert related_transition[1] == superseded


def test_replacement_transition_does_not_commit_when_audit_fails() -> None:
    store, original = accepted_record_in_store()
    replacement = store.create_replacement(
        original.id,
        MOCK_IDENTITIES[2],
        record_change=lambda _: None,
    )
    proposed = store.submit(
        replacement.id,
        replacement.author,
        has_designated_approver=True,
    )

    def fail_audit(*_: object) -> None:
        raise OSError("audit store unavailable")

    with pytest.raises(OSError, match="audit store unavailable"):
        store.decide(
            proposed.id,
            "Accepted",
            record_change=fail_audit,
        )

    assert store.get(original.id) == original.model_copy(
        update={"replacement_record_ids": [replacement.id]}
    )
    assert store.get(replacement.id) == proposed


def test_replacement_create_and_abandon_do_not_commit_when_audit_fails() -> None:
    store, original = accepted_record_in_store()

    def fail_audit(*_: object) -> None:
        raise OSError("audit store unavailable")

    with pytest.raises(OSError, match="audit store unavailable"):
        store.create_replacement(
            original.id,
            MOCK_IDENTITIES[2],
            record_change=fail_audit,
        )
    assert store.get(original.id) == original

    replacement = store.create_replacement(
        original.id,
        MOCK_IDENTITIES[2],
        record_change=lambda _: None,
    )
    with pytest.raises(OSError, match="audit store unavailable"):
        store.abandon_replacement(
            replacement.id,
            MOCK_IDENTITIES[2],
            record_change=fail_audit,
        )

    assert store.get(original.id) == original.model_copy(
        update={"replacement_record_ids": [replacement.id]}
    )
    assert store.get(replacement.id) == replacement


def test_replacement_acceptance_route_audits_both_atomic_status_changes(
    client: TestClient,
) -> None:
    original = accept_record(client)
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    replacement = client.post(
        f"/api/decision-records/{original['id']}/replacements"
    ).json()
    proposed = client.post(
        f"/api/decision-records/{replacement['id']}/submit"
    ).json()
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})

    accepted = client.post(
        f"/api/decision-records/{proposed['id']}/decision",
        json={"outcome": "Accepted"},
    )

    assert accepted.status_code == 200
    assert accepted.json()["status"] == "Accepted"
    superseded = client.get(
        f"/api/decision-records/{original['id']}"
    ).json()
    assert superseded["status"] == "Superseded"
    events = client.get(
        f"/api/decision-records/{replacement['id']}/audit-events"
    ).json()["events"]
    related_status_field = f"related_record.{original['id']}.status"
    transition = next(
        event
        for event in events
        if any(
            change["field"] == related_status_field
            for change in event["changes"]
        )
    )
    assert transition["actor"]["id"] == "arun-approver"
    assert {
        "field": "status",
        "before": "Proposed",
        "after": "Accepted",
    } in transition["changes"]
    assert {
        "field": related_status_field,
        "before": "Accepted",
        "after": "Superseded",
    } in transition["changes"]


def test_abandonment_retains_and_audits_draft_and_allows_new_replacement(
    client: TestClient,
) -> None:
    original = accept_record(client)
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    response = client.post(
        f"/api/decision-records/{original['id']}/replacements"
    )
    assert response.status_code == 201
    replacement = response.json()

    abandoned = client.post(
        f"/api/decision-records/{replacement['id']}/abandon"
    )

    assert abandoned.status_code == 200
    assert abandoned.json()["status"] == "Draft"
    assert abandoned.json()["abandoned"] is True
    assert abandoned.json()["replaces_record_id"] == original["id"]
    retained_original = client.get(
        f"/api/decision-records/{original['id']}"
    ).json()
    assert retained_original["status"] == "Accepted"
    assert retained_original["replacement_record_ids"] == [replacement["id"]]

    events = client.get(
        f"/api/decision-records/{replacement['id']}/audit-events"
    ).json()["events"]
    abandonment = next(
        event
        for event in events
        if event["event_type"] == "replacement_draft_abandoned"
    )
    assert abandonment["actor"]["id"] == "zoe-admin"
    assert abandonment["occurred_at"]
    assert abandonment["changes"] == [
        {"field": "abandoned", "before": False, "after": True}
    ]

    next_replacement = client.post(
        f"/api/decision-records/{original['id']}/replacements"
    )
    assert next_replacement.status_code == 201
    assert next_replacement.json()["id"] != replacement["id"]
    assert client.get(f"/api/decision-records/{original['id']}").json()[
        "replacement_record_ids"
    ] == [replacement["id"], next_replacement.json()["id"]]


def test_only_administrator_can_abandon_replacement(client: TestClient) -> None:
    original = accept_record(client)
    client.post("/api/mock-session", json={"identity_id": "zoe-admin"})
    replacement = client.post(
        f"/api/decision-records/{original['id']}/replacements"
    ).json()
    client.post("/api/mock-session", json={"identity_id": "maya-member"})

    response = client.post(
        f"/api/decision-records/{replacement['id']}/abandon"
    )

    assert response.status_code == 403
    retained = client.get(
        f"/api/decision-records/{replacement['id']}"
    ).json()
    assert retained["status"] == "Draft"
    assert retained["abandoned"] is False
    events = client.get(
        f"/api/decision-records/{replacement['id']}/audit-events"
    ).json()["events"]
    assert not any(
        event["event_type"] == "replacement_draft_abandoned"
        for event in events
    )


@pytest.mark.parametrize(
    ("target_kind", "expected_status"),
    [
        ("ordinary_draft", "Draft"),
        ("proposed_replacement", "Proposed"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("superseded", "Superseded"),
    ],
)
def test_abandonment_rejects_invalid_targets(
    target_kind: str,
    expected_status: str,
) -> None:
    store, original = accepted_record_in_store()
    if target_kind == "ordinary_draft":
        target = store.create(
            DecisionRecordCreate(**complete_payload()),
            MOCK_IDENTITIES[0],
        )
    elif target_kind == "proposed_replacement":
        target = store.create_replacement(
            original.id,
            MOCK_IDENTITIES[2],
            record_change=lambda _: None,
        )
        target = store.submit(
            target.id,
            target.author,
            has_designated_approver=True,
        )
    elif target_kind == "accepted":
        target = original
    else:
        proposed = store.create(
            DecisionRecordCreate(**complete_payload()),
            MOCK_IDENTITIES[0],
        )
        proposed = store.submit(
            proposed.id,
            proposed.author,
            has_designated_approver=True,
        )
        target = store.decide(
            proposed.id,
            "Rejected",
            record_change=lambda *_: None,
        )
        if target_kind == "superseded":
            target = target.model_copy(update={"status": "Superseded"})
            store._records[target.id] = target

    before = store.get(target.id)
    assert before is not None
    assert before.status == expected_status
    with pytest.raises(RecordActionError, match="active replacement Draft"):
        store.abandon_replacement(
            target.id,
            MOCK_IDENTITIES[2],
            record_change=lambda *_: None,
        )
    assert store.get(target.id) == before


def test_abandoned_replacement_is_permanently_immutable() -> None:
    store, original = accepted_record_in_store()
    replacement = store.create_replacement(
        original.id,
        MOCK_IDENTITIES[2],
        record_change=lambda _: None,
    )
    abandoned = store.abandon_replacement(
        replacement.id,
        MOCK_IDENTITIES[2],
        record_change=lambda *_: None,
    )

    with pytest.raises(RecordActionError, match="Abandoned"):
        store.update(
            replacement.id,
            DecisionRecordUpdate(title="Changed"),
            replacement.author,
        )
    with pytest.raises(RecordActionError, match="Abandoned"):
        store.submit(
            replacement.id,
            replacement.author,
            has_designated_approver=True,
        )
    with pytest.raises(RecordActionError, match="Abandoned"):
        store.transfer_owner(
            replacement.id,
            "maya-member",
            MOCK_IDENTITIES[2],
            record_change=lambda *_: None,
        )
    with pytest.raises(RecordActionError, match="active replacement Draft"):
        store.abandon_replacement(
            replacement.id,
            MOCK_IDENTITIES[2],
            record_change=lambda *_: None,
        )
    assert store.get(replacement.id) == abandoned
    retained_original = store.get(original.id)
    assert retained_original is not None
    assert retained_original.status == "Accepted"
    assert retained_original.replacement_record_ids == [replacement.id]
