from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.identities import MOCK_IDENTITIES, MockIdentity, Role
from app.main import create_app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_entry_screen_labels_mock_identities_and_data_boundary(
    client: TestClient,
) -> None:
    response = client.get("/")
    page_text = " ".join(response.text.split())

    assert response.status_code == 200
    assert "Choose a Mock Identity" in page_text
    assert "demo or synthetic data" in page_text
    assert "real internal" in page_text
    assert "regulated personal information" in page_text
    assert "health information" in page_text
    assert "not authentication" in page_text
    assert "does not verify who you are" in page_text
    assert "verify team" in page_text
    assert "unauthorized access" in page_text


def test_lists_preconfigured_identities_as_mock_users(client: TestClient) -> None:
    response = client.get("/api/mock-identities")

    assert response.status_code == 200
    identities = response.json()
    assert len(identities) == len(MOCK_IDENTITIES)
    assert all(identity["is_mock"] is True for identity in identities)
    assert all("Mock User" in identity["label"] for identity in identities)
    assert {identity["id"] for identity in identities} == {
        identity.id for identity in MOCK_IDENTITIES
    }


@pytest.mark.parametrize("identity", MOCK_IDENTITIES, ids=lambda item: item.id)
def test_selection_propagates_roles_and_attribution(
    client: TestClient,
    identity: MockIdentity,
) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": identity.id},
    )

    assert response.status_code == 200
    assert response.json()["selected_identity"] == identity.model_dump(mode="json")

    session = client.get("/api/mock-session")
    assert session.json()["selected_identity"]["id"] == identity.id
    assert session.json()["selected_identity"]["roles"] == [
        role.value for role in identity.roles
    ]

    attribution = client.get("/api/attribution-preview")
    assert attribution.status_code == 200
    assert attribution.json()["actor"]["id"] == identity.id
    assert identity.display_name in attribution.json()["message"]


def test_roles_are_additive_for_combined_mock_identity(client: TestClient) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": "lee-admin-approver"},
    )

    assert response.status_code == 200
    assert response.json()["selected_identity"]["roles"] == [
        Role.TEAM_MEMBER.value,
        Role.ADMINISTRATOR.value,
        Role.APPROVER.value,
    ]


def test_selection_requires_no_sso_or_authorization_header(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": "zoe-admin"},
    )

    assert response.status_code == 200
    assert response.json()["selected_identity"]["id"] == "zoe-admin"


def test_unknown_identity_is_rejected_without_changing_context(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/mock-session",
        json={"identity_id": "not-configured"},
    )

    assert response.status_code == 404
    assert client.get("/api/mock-session").json() == {"selected_identity": None}


def test_attribution_requires_a_selected_mock_identity(client: TestClient) -> None:
    response = client.get("/api/attribution-preview")

    assert response.status_code == 400
    assert response.json()["detail"] == "Choose a Mock identity before continuing."


def test_identity_can_be_changed_and_cleared(client: TestClient) -> None:
    client.post("/api/mock-session", json={"identity_id": "maya-member"})
    client.post("/api/mock-session", json={"identity_id": "arun-approver"})

    assert (
        client.get("/api/mock-session").json()["selected_identity"]["id"]
        == "arun-approver"
    )

    response = client.delete("/api/mock-session")
    assert response.status_code == 204
    assert client.get("/api/mock-session").json() == {"selected_identity": None}
