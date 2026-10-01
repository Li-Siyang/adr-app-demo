"""Independent acceptance coverage for STORY-013, TS-013."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.governance import designated_approver_ids
from app.identities import MOCK_IDENTITIES
from app.main import create_app
from app.records import DecisionRecordStore

RECORD_FIELDS = {
    "title": "Retain every decision record",
    "context": "Records must remain retained in every condition.",
    "decision": "Keep record deletion unavailable.",
    "rationale": "Archival is reversible and preserves the record.",
    "alternatives_considered": "Permanently or softly delete the record.",
    "consequences": "The record remains available for permitted actions.",
    "owner_id": "maya-member",
    "decision_date": "2026-10-01",
    "tags": ["retention"],
}


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    designated_approver_ids.clear()
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as test_client:
        yield test_client
    designated_approver_ids.clear()


@pytest.mark.parametrize(
    ("status", "archived", "abandoned", "replacement"),
    [
        pytest.param("Draft", False, False, False, id="draft"),
        pytest.param("Proposed", False, False, False, id="proposed"),
        pytest.param("Accepted", False, False, False, id="accepted"),
        pytest.param("Rejected", False, False, False, id="rejected"),
        pytest.param("Superseded", False, False, False, id="superseded"),
        pytest.param("Draft", False, False, True, id="active-replacement-draft"),
        pytest.param("Proposed", False, False, True, id="active-replacement-proposed"),
        pytest.param("Draft", False, True, True, id="abandoned-replacement"),
        pytest.param("Draft", True, False, False, id="archived"),
        pytest.param("Accepted", True, False, False, id="archived-accepted"),
        pytest.param("Draft", True, True, True, id="archived-abandoned-replacement"),
    ],
)
def test_every_identity_is_denied_record_deletion_and_record_is_retained(
    client: TestClient,
    status: str,
    archived: bool,
    abandoned: bool,
    replacement: bool,
) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    created = client.post("/api/decision-records", json=RECORD_FIELDS)
    assert created.status_code == 201

    store: DecisionRecordStore = client.app.state.record_store
    original = store.get(created.json()["id"])
    assert original is not None
    retained = original.model_copy(
        update={
            "status": status,
            "archived": archived,
            "abandoned": abandoned,
            "replaces_record_id": "original-record" if replacement else None,
        }
    )
    store._records[retained.id] = retained
    path = f"/api/decision-records/{retained.id}"

    for identity in MOCK_IDENTITIES:
        client.post("/api/mock-session", json={"identity_id": identity.id})
        assert client.delete(path).status_code == 405
        assert client.put(path, json={"deleted": True}).status_code == 422
        assert client.get(path).json() == retained.model_dump(mode="json")

    listed = client.get("/api/decision-records").json()["records"]
    assert listed == [retained.model_dump(mode="json")]
