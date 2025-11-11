from fastapi import APIRouter

from .tasks import router as tasks_router
from .stream import router as stream_router

api_router = APIRouter(prefix="/api")
api_router.include_router(tasks_router)
api_router.include_router(stream_router)

__all__ = ["api_router"]
