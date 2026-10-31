from fastapi import APIRouter

from app.api.routes import auth, comments, items, search

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(items.router)
api_router.include_router(comments.router)
api_router.include_router(search.router)
