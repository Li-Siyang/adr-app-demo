"""Unit tests for the production SSO verification path (CR-FR-001).

These tests exercise `SsoTokenVerifier` against a controlled JWKS and signing
key, so JWKS key selection, signature, issuer, audience, and expiry validation
are covered rather than stubbed out.
"""

import json
import time
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt import PyJWKClient
from jwt.algorithms import RSAAlgorithm

from app.core.config import Settings
from app.core.security import SsoTokenVerifier, TokenVerificationError

ISSUER = "https://sso.example.com/"
AUDIENCE = "adr-app"
KEY_ID = "test-key-1"
OTHER_KEY_ID = "test-key-2"


def _new_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _public_jwk(private_key: rsa.RSAPrivateKey, kid: str) -> dict[str, Any]:
    jwk = json.loads(RSAAlgorithm.to_jwk(private_key.public_key()))
    jwk.update({"kid": kid, "use": "sig", "alg": "RS256"})
    return jwk


@pytest.fixture(scope="module")
def signing_key() -> rsa.RSAPrivateKey:
    return _new_private_key()


@pytest.fixture(scope="module")
def decoy_key() -> rsa.RSAPrivateKey:
    return _new_private_key()


@pytest.fixture
def verifier(
    monkeypatch: pytest.MonkeyPatch,
    signing_key: rsa.RSAPrivateKey,
    decoy_key: rsa.RSAPrivateKey,
) -> SsoTokenVerifier:
    jwks = {
        "keys": [
            _public_jwk(decoy_key, OTHER_KEY_ID),
            _public_jwk(signing_key, KEY_ID),
        ]
    }
    jwk_client = PyJWKClient("https://sso.example.com/.well-known/jwks.json")
    monkeypatch.setattr(jwk_client, "fetch_data", lambda: jwks)

    settings = Settings(sso_issuer=ISSUER, sso_audience=AUDIENCE, sso_jwks_url="")
    return SsoTokenVerifier(settings, jwk_client=jwk_client)


def make_token(
    private_key: rsa.RSAPrivateKey,
    *,
    kid: str = KEY_ID,
    issuer: str = ISSUER,
    audience: str = AUDIENCE,
    expires_in: int = 300,
    claims: dict[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "sub": "sso|member",
        "email": "member@example.com",
        "name": "Team Member",
        "iss": issuer,
        "aud": audience,
        "exp": int(time.time()) + expires_in,
    }
    if claims is not None:
        payload.update(claims)
        for key, value in list(payload.items()):
            if value is None:
                del payload[key]
    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": kid})


def test_valid_token_is_accepted(
    verifier: SsoTokenVerifier, signing_key: rsa.RSAPrivateKey
) -> None:
    claims = verifier.verify(make_token(signing_key))

    assert claims.subject == "sso|member"
    assert claims.email == "member@example.com"
    assert claims.display_name == "Team Member"


def test_token_signed_by_an_untrusted_key_is_rejected(
    verifier: SsoTokenVerifier
) -> None:
    foreign_key = _new_private_key()

    with pytest.raises(TokenVerificationError):
        verifier.verify(make_token(foreign_key))


def test_token_signed_by_the_wrong_jwks_key_is_rejected(
    verifier: SsoTokenVerifier, signing_key: rsa.RSAPrivateKey
) -> None:
    # Advertises another published key id, so JWKS selection must not match.
    with pytest.raises(TokenVerificationError):
        verifier.verify(make_token(signing_key, kid=OTHER_KEY_ID))


def test_unknown_key_id_is_rejected(
    verifier: SsoTokenVerifier, signing_key: rsa.RSAPrivateKey
) -> None:
    with pytest.raises(TokenVerificationError):
        verifier.verify(make_token(signing_key, kid="unpublished-key"))


def test_wrong_issuer_is_rejected(
    verifier: SsoTokenVerifier, signing_key: rsa.RSAPrivateKey
) -> None:
    with pytest.raises(TokenVerificationError):
        verifier.verify(make_token(signing_key, issuer="https://attacker.example/"))


def test_wrong_audience_is_rejected(
    verifier: SsoTokenVerifier, signing_key: rsa.RSAPrivateKey
) -> None:
    with pytest.raises(TokenVerificationError):
        verifier.verify(make_token(signing_key, audience="other-app"))


def test_expired_token_is_rejected(
    verifier: SsoTokenVerifier, signing_key: rsa.RSAPrivateKey
) -> None:
    with pytest.raises(TokenVerificationError):
        verifier.verify(make_token(signing_key, expires_in=-60))


@pytest.mark.parametrize("missing_claim", ["exp", "iss", "aud", "sub"])
def test_token_missing_a_required_claim_is_rejected(
    verifier: SsoTokenVerifier, signing_key: rsa.RSAPrivateKey, missing_claim: str
) -> None:
    with pytest.raises(TokenVerificationError):
        verifier.verify(make_token(signing_key, claims={missing_claim: None}))


def test_malformed_token_is_rejected(verifier: SsoTokenVerifier) -> None:
    with pytest.raises(TokenVerificationError):
        verifier.verify("not-a-jwt")
