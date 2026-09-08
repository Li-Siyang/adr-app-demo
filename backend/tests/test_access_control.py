"""Unit tests for STORY-001 access control (CR-FR-001-002, CR-NFR-001-002, AC-001)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from tests.conftest import MEMBER_TOKEN, OUTSIDER_TOKEN, auth

PROTECTED_PATH = "/api/me"
DECISION_RECORD_PATH = "/api/decisions/11111111-1111-1111-1111-111111111111"


def test_authenticated_team_member_is_granted_access(
    client: TestClient, team_member: User
) -> None:
    response = client.get(PROTECTED_PATH, headers=auth(MEMBER_TOKEN))

    assert response.status_code == 200
    assert response.json()["email"] == "member@example.com"


def test_unauthenticated_request_is_denied(client: TestClient, team_member: User) -> None:
    response = client.get(PROTECTED_PATH)

    assert response.status_code == 401


def test_invalid_token_is_denied(client: TestClient, team_member: User) -> None:
    response = client.get(PROTECTED_PATH, headers=auth("not-a-real-token"))

    assert response.status_code == 401


def test_unauthenticated_direct_record_reference_is_denied(client: TestClient) -> None:
    response = client.get(DECISION_RECORD_PATH)

    assert response.status_code == 401
    assert "decision" not in response.text.lower()


def test_authenticated_non_team_member_is_denied(client: TestClient) -> None:
    response = client.get(PROTECTED_PATH, headers=auth(OUTSIDER_TOKEN))

    assert response.status_code == 403


def test_authenticated_non_team_member_direct_record_reference_is_denied(
    client: TestClient,
) -> None:
    response = client.get(DECISION_RECORD_PATH, headers=auth(OUTSIDER_TOKEN))

    assert response.status_code == 403


def test_access_is_revoked_immediately_when_membership_is_lost(
    client: TestClient, db_session: Session, team_member: User
) -> None:
    assert client.get(PROTECTED_PATH, headers=auth(MEMBER_TOKEN)).status_code == 200

    team_member.is_team_member = False
    db_session.commit()

    assert client.get(PROTECTED_PATH, headers=auth(MEMBER_TOKEN)).status_code == 403


def test_health_endpoint_stays_public(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_protected_path_is_not_found_for_a_member(
    client: TestClient, team_member: User
) -> None:
    response = client.get(DECISION_RECORD_PATH, headers=auth(MEMBER_TOKEN))

    assert response.status_code == 404
