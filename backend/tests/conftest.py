from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import bearer_scheme  # noqa: F401 - keeps import side effects explicit
from app.core.security import TokenClaims, TokenVerificationError, get_token_verifier
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models.user import User

MEMBER_TOKEN = "token-member"
OUTSIDER_TOKEN = "token-outsider"

KNOWN_TOKENS = {
    MEMBER_TOKEN: TokenClaims(
        subject="sso|member", email="member@example.com", display_name="Team Member"
    ),
    OUTSIDER_TOKEN: TokenClaims(
        subject="sso|outsider", email="outsider@example.com", display_name="Outsider"
    ),
}


class FakeTokenVerifier:
    """Stands in for the organizational SSO provider during unit tests."""

    def verify(self, token: str) -> TokenClaims:
        try:
            return KNOWN_TOKENS[token]
        except KeyError:
            raise TokenVerificationError("unknown token") from None


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    app = create_app(initialize_schema=lambda: None)
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_verifier] = FakeTokenVerifier
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def team_member(db_session: Session) -> User:
    user = User(
        subject="sso|member",
        email="member@example.com",
        display_name="Team Member",
        is_team_member=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
