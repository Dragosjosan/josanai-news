from fastapi import APIRouter

from app.api.routes.queries import admin, auth, comments, items, search

router = APIRouter()
router.include_router(auth.router)
router.include_router(items.router)
router.include_router(comments.router)
router.include_router(search.router)
router.include_router(admin.router)
