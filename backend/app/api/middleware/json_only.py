from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.errors import error_response
from app.errors import ErrorCode

_WRITE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


class JsonOnlyMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["method"] in _WRITE_METHODS:
            headers = Headers(scope=scope)
            if _has_body(headers) and not _is_json(headers.get("content-type", "")):
                response = error_response(
                    ErrorCode.UNSUPPORTED_MEDIA_TYPE, "Request bodies must be application/json."
                )
                await response(scope, receive, send)
                return
        await self._app(scope, receive, send)


def _has_body(headers: Headers) -> bool:
    if "transfer-encoding" in headers:
        return True
    length = headers.get("content-length", "0")
    return not length.isdigit() or int(length) > 0


def _is_json(content_type: str) -> bool:
    return content_type.split(";", 1)[0].strip().lower() == "application/json"
