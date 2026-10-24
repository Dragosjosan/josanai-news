from datetime import datetime, timedelta

from app.errors import AppError, ErrorCode

RATE_WINDOW = timedelta(hours=1)


def check_rate(count: int, oldest: datetime | None, limit: int, now: datetime, what: str) -> None:
    if count >= limit and oldest is not None:
        retry_after = max(int((oldest + RATE_WINDOW - now).total_seconds()) + 1, 1)
        raise AppError(
            ErrorCode.RATE_LIMITED,
            f"Too many {what}. Try again in {retry_after} seconds.",
            retry_after=retry_after,
        )
