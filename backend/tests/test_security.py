"""Unit tests for SSO token claim handling (CR-FR-001)."""

import pytest

from app.core.security import TokenVerificationError, _to_claims


def test_claims_are_extracted_from_a_valid_payload() -> None:
    claims = _to_claims({"sub": "sso|1", "email": "a@example.com", "name": "Ada"})

    assert claims.subject == "sso|1"
    assert claims.email == "a@example.com"
    assert claims.display_name == "Ada"


def test_display_name_falls_back_to_email() -> None:
    claims = _to_claims({"sub": "sso|1", "email": "a@example.com"})

    assert claims.display_name == "a@example.com"


@pytest.mark.parametrize(
    "payload",
    [{"email": "a@example.com"}, {"sub": "sso|1"}, {}],
)
def test_missing_identity_claims_are_rejected(payload: dict) -> None:
    with pytest.raises(TokenVerificationError):
        _to_claims(payload)
