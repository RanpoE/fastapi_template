from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from api.api import router as root_router

description = """
    Template project using FastAPI. 🚀
"""
app = FastAPI(
    description=description,
    version="0.0.1",
    redoc_url="/docs",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root_router)
