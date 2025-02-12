from fastapi import APIRouter

from .endpoints import facebook, item

api_router = APIRouter()
api_router.include_router(item.router, prefix="/items", tags=["items"])
api_router.include_router(facebook.router, tags=["facebook"])
