from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import TokenVerificationError, TokenVerifier, get_token_verifier
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthenticated() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _not_a_team_member() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access is restricted to designated team members",
    )


def get_current_member(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    db: Annotated[Session, Depends(get_db)],
    verifier: Annotated[TokenVerifier, Depends(get_token_verifier)],
) -> User:
    """Resolve the caller and allow only designated team members (AC-001).

    Membership is read from storage on every request so that losing team
    membership takes effect immediately, even for an existing session.
    """
    if credentials is None or not credentials.credentials:
        raise _unauthenticated()

    try:
        claims = verifier.verify(credentials.credentials)
    except TokenVerificationError:
        raise _unauthenticated() from None

    user = db.execute(
        select(User).where(User.subject == claims.subject)
    ).scalar_one_or_none()

    if user is None or not user.is_team_member:
        raise _not_a_team_member()

    return user


CurrentMember = Annotated[User, Depends(get_current_member)]
