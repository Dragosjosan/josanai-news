from typing import Any

from pydantic import BaseModel

from app.errors import ErrorCode


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
