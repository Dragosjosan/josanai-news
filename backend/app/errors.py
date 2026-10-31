from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    NOT_AUTHENTICATED = "not_authenticated"
    INVALID_API_KEY = "invalid_api_key"
    INVALID_CREDENTIALS = "invalid_credentials"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    DUPLICATE = "duplicate"
    USERNAME_TAKEN = "username_taken"
    PAYLOAD_TOO_LARGE = "payload_too_large"
    UNSUPPORTED_MEDIA_TYPE = "unsupported_media_type"
    VALIDATION_ERROR = "validation_error"
    UNSUPPORTED_CONTRACT_VERSION = "unsupported_contract_version"
    PARENT_NOT_FOUND = "parent_not_found"
    RATE_LIMITED = "rate_limited"
    HTTP_ERROR = "http_error"
    INTERNAL_ERROR = "internal_error"


STATUS_BY_CODE: dict[ErrorCode, int] = {
    ErrorCode.NOT_AUTHENTICATED: 401,
    ErrorCode.INVALID_API_KEY: 401,
    ErrorCode.INVALID_CREDENTIALS: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.METHOD_NOT_ALLOWED: 405,
    ErrorCode.DUPLICATE: 409,
    ErrorCode.USERNAME_TAKEN: 409,
    ErrorCode.PAYLOAD_TOO_LARGE: 413,
    ErrorCode.UNSUPPORTED_MEDIA_TYPE: 415,
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNSUPPORTED_CONTRACT_VERSION: 422,
    ErrorCode.PARENT_NOT_FOUND: 422,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.HTTP_ERROR: 400,
    ErrorCode.INTERNAL_ERROR: 500,
}


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
        self.retry_after = retry_after

    @property
    def status(self) -> int:
        return STATUS_BY_CODE[self.code]
