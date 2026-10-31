from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

from app.dto.validation import Password, RequestModel, Username


class SignupRequest(RequestModel):
    kind: Literal["user", "agent"]
    username: Username
    password: Password | None = None
    website: str = Field(default="", max_length=0)

    @model_validator(mode="after")
    def check_password(self) -> Self:
        if self.kind == "user" and self.password is None:
            raise ValueError("a user needs a password")
        if self.kind == "agent" and self.password is not None:
            raise ValueError("an agent has no password")
        return self


class LoginRequest(RequestModel):
    username: str = Field(max_length=32)
    password: str = Field(max_length=128)


class AccountResponse(BaseModel):
    id: int
    username: str
    kind: Literal["user", "agent"]
    role: Literal["user", "admin"]
    created_at: datetime


class AgentSignupResponse(BaseModel):
    account: AccountResponse
    api_key: str


class ApiKeyResponse(BaseModel):
    api_key: str
