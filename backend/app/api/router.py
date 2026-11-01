from fastapi import APIRouter

from app.api.routes import commands, queries

api_router = APIRouter()
api_router.include_router(queries.router)
api_router.include_router(commands.router)
