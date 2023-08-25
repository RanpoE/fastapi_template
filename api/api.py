from fastapi import APIRouter
from .endpoints import root

router = APIRouter()

router.include_router(root.router, prefix="/v1", tags=["Web services"])
