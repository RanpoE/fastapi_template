from fastapi import APIRouter

from .endpoints import root

router = APIRouter()

router.include_router(root.router, prefix="/ec2", tags=["Web services"])
