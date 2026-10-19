import logging
from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.dto.errors import ErrorDetail, ErrorResponse
from app.errors import STATUS_BY_CODE, AppError, ErrorCode

logger = logging.getLogger(__name__)

_CODE_BY_STATUS: dict[int, ErrorCode] = {
    401: ErrorCode.NOT_AUTHENTICATED,
    403: ErrorCode.FORBIDDEN,
    404: ErrorCode.NOT_FOUND,
    405: ErrorCode.METHOD_NOT_ALLOWED,
    413: ErrorCode.PAYLOAD_TOO_LARGE,
    415: ErrorCode.UNSUPPORTED_MEDIA_TYPE,
}


def error_response(
    code: ErrorCode,
    message: str,
    details: dict[str, Any] | None = None,
    status: int | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, message=message, details=details))
    return JSONResponse(
        status_code=status or STATUS_BY_CODE[code],
        content=body.model_dump(mode="json"),
        headers=headers,
    )


async def _app_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    headers = {"Retry-After": str(exc.retry_after)} if exc.retry_after is not None else None
    details = exc.details
    if exc.retry_after is not None:
        details = {**(details or {}), "retry_after": exc.retry_after}
    return error_response(exc.code, exc.message, details, headers=headers)


async def _validation_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    fields = [
        {"loc": list(error.get("loc", ())), "message": str(error.get("msg", ""))}
        for error in exc.errors()
    ]
    return error_response(
        ErrorCode.VALIDATION_ERROR, "The request is not valid.", {"fields": fields}
    )


async def _http_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code = _CODE_BY_STATUS.get(exc.status_code, ErrorCode.HTTP_ERROR)
    message = exc.detail if isinstance(exc.detail, str) else code.value
    return error_response(code, message, status=exc.status_code, headers=exc.headers)


async def _unhandled_error(_: Request, exc: Exception) -> JSONResponse:
    request_id = uuid4().hex
    logger.error("Unhandled error", exc_info=exc, extra={"request_id": request_id})
    return error_response(
        ErrorCode.INTERNAL_ERROR, "Something went wrong.", {"request_id": request_id}
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unhandled_error)
