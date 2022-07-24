from fastapi import APIRouter

from ..schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health():
    return {"status": "ok"}