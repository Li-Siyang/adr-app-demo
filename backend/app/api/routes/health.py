from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Unauthenticated liveness probe; exposes no decision data."""
    return {"status": "ok"}
