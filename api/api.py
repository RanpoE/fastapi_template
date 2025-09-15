from fastapi import APIRouter
from .endpoints import root, recipes

router = APIRouter()

router.include_router(root.router, prefix="/v1", tags=["Web services"])
router.include_router(recipes.router, prefix="/v1")
