from fastapi import APIRouter

from app.api.routes.commands import admin, auth, comments, items

router = APIRouter()
router.include_router(auth.router)
router.include_router(items.router)
router.include_router(comments.router)
router.include_router(admin.router)
