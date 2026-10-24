from fastapi import APIRouter, Request, Response, status

from app.api.dependencies import (
    SESSION_COOKIE,
    AppSettings,
    AuthServiceDep,
    RequestCredentials,
)
from app.dto.accounts import (
    AccountResponse,
    AgentSignupResponse,
    ApiKeyResponse,
    LoginRequest,
    SignupRequest,
)
from app.services.identity import SESSION_LIFETIME

router = APIRouter(prefix="/auth", tags=["auth"])
signup_router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str, settings: AppSettings) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(SESSION_LIFETIME.total_seconds()),
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )


@signup_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(
    body: SignupRequest, response: Response, settings: AppSettings, auth: AuthServiceDep
) -> AccountResponse | AgentSignupResponse:
    result = auth.signup(body)
    if result.api_key is not None:
        return AgentSignupResponse(account=result.account, api_key=result.api_key)
    if result.session_token is not None:
        _set_session_cookie(response, result.session_token, settings)
    return result.account


@router.post("/login")
def login(
    body: LoginRequest, response: Response, settings: AppSettings, auth: AuthServiceDep
) -> AccountResponse:
    result = auth.login(body)
    _set_session_cookie(response, result.session_token, settings)
    return result.account


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, settings: AppSettings, auth: AuthServiceDep) -> Response:
    auth.logout(request.cookies.get(SESSION_COOKIE))
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        SESSION_COOKIE, path="/", secure=settings.cookie_secure, httponly=True, samesite="lax"
    )
    return response


@router.get("/me")
def me(credentials: RequestCredentials, auth: AuthServiceDep) -> AccountResponse | None:
    return auth.current(credentials)


@router.post("/rotate-key")
def rotate_key(credentials: RequestCredentials, auth: AuthServiceDep) -> ApiKeyResponse:
    return ApiKeyResponse(api_key=auth.rotate_key(credentials))
