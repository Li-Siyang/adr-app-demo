from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_member
from app.api.routes import session

api_router = APIRouter(prefix="/api", dependencies=[Depends(get_current_member)])
api_router.include_router(session.router)


@api_router.api_route(
    "/{unmatched_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
def unmatched_protected_path(unmatched_path: str) -> None:
    """Reject unknown protected paths only after access control has run.

    Without this fallback an unauthenticated request to a not-yet-implemented
    resource, such as a direct decision-record reference, would be answered
    before the access check and would reveal which resources exist (CR-NFR-002).
    """
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
