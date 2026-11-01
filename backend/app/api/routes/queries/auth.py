from fastapi import APIRouter

from app.api.dependencies import AuthServiceDep, RequestCredentials
from app.dto.accounts import AccountResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def me(credentials: RequestCredentials, auth: AuthServiceDep) -> AccountResponse | None:
    return auth.current(credentials)
