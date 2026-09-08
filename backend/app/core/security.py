from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol

import jwt
from jwt import PyJWKClient

from app.core.config import Settings, get_settings


class TokenVerificationError(Exception):
    """Raised when a presented token is missing, malformed, or untrusted."""


@dataclass(frozen=True)
class TokenClaims:
    """The identity claims the application trusts from the SSO provider."""

    subject: str
    email: str
    display_name: str


class TokenVerifier(Protocol):
    def verify(self, token: str) -> TokenClaims: ...


class SsoTokenVerifier:
    """Verifies organizational SSO tokens against the provider's JWKS (CR-FR-001)."""

    def __init__(self, settings: Settings, jwk_client: PyJWKClient | None = None) -> None:
        self._settings = settings
        self._jwk_client = jwk_client or PyJWKClient(settings.sso_jwks_url)

    def verify(self, token: str) -> TokenClaims:
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self._settings.sso_issuer,
                audience=self._settings.sso_audience,
                options={"require": ["exp", "iss", "aud", "sub"]},
            )
        except Exception as error:  # noqa: BLE001 - any failure means untrusted token
            raise TokenVerificationError("Token could not be verified") from error

        return _to_claims(payload)


def _to_claims(payload: dict) -> TokenClaims:
    subject = payload.get("sub")
    email = payload.get("email")
    if not subject or not email:
        raise TokenVerificationError("Token is missing required identity claims")

    return TokenClaims(
        subject=subject,
        email=email,
        display_name=payload.get("name") or email,
    )


@lru_cache
def get_token_verifier() -> TokenVerifier:
    return SsoTokenVerifier(get_settings())
