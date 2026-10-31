import re
import unicodedata
from typing import Annotated, Any
from urllib.parse import urlsplit

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, StringConstraints

INVISIBLE_CHARACTERS = frozenset(
    [*range(0x200B, 0x2010), 0x2060, 0xFEFF, *range(0x202A, 0x202F), *range(0x2066, 0x206A)]
)
MAX_URL_LENGTH = 2048

_LABEL_PATTERN = re.compile(r"[A-Za-z0-9 ._-]+")
_USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_-]+")


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _reject_unsafe(text: str, *, allow_newlines: bool) -> None:
    for character in text:
        if allow_newlines and character == "\n":
            continue
        if unicodedata.category(character) == "Cc" or ord(character) in INVISIBLE_CHARACTERS:
            raise ValueError("must not contain control or invisible characters")


def clean_line(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = unicodedata.normalize("NFC", value).strip()
    _reject_unsafe(text, allow_newlines=False)
    return text


def clean_title(value: Any) -> Any:
    text = clean_line(value)
    return " ".join(text.split()) if isinstance(text, str) else text


def clean_multiline(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = unicodedata.normalize("NFC", value).replace("\r\n", "\n").replace("\r", "\n").strip()
    _reject_unsafe(text, allow_newlines=True)
    return text


def clean_label(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = " ".join(value.split())
    if text and not _LABEL_PATTERN.fullmatch(text):
        raise ValueError("may only contain ASCII letters, digits, spaces, '-', '_' and '.'")
    return text


def clean_username(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if text and not _USERNAME_PATTERN.fullmatch(text):
        raise ValueError("may only contain ASCII letters, digits, '-' and '_'")
    return text


def check_url(value: str) -> str:
    if any(character.isspace() for character in value):
        raise ValueError("must not contain whitespace")
    _reject_unsafe(value, allow_newlines=False)
    try:
        parts = urlsplit(value)
        _ = parts.port
    except ValueError as error:
        raise ValueError("is not a valid URL") from error
    if parts.scheme.lower() not in ("http", "https"):
        raise ValueError("must be an http or https URL")
    if not parts.hostname:
        raise ValueError("must have a host")
    try:
        parts.hostname.encode("idna")
    except UnicodeError as error:
        raise ValueError("must have a valid host") from error
    if "@" in parts.netloc:
        raise ValueError("must not contain credentials")
    return value


def name_key(name: str) -> str:
    return name.lower()


Title = Annotated[
    str, BeforeValidator(clean_title), StringConstraints(min_length=1, max_length=300)
]
SourceName = Annotated[
    str, BeforeValidator(clean_line), StringConstraints(min_length=1, max_length=200)
]
PrimaryRef = Annotated[
    str, BeforeValidator(clean_line), StringConstraints(min_length=1, max_length=200)
]
Summary = Annotated[
    str, BeforeValidator(clean_multiline), StringConstraints(min_length=1, max_length=500)
]
CommentText = Annotated[
    str, BeforeValidator(clean_multiline), StringConstraints(min_length=1, max_length=5000)
]
SearchText = Annotated[str, BeforeValidator(clean_line), StringConstraints(max_length=200)]
Label = Annotated[str, BeforeValidator(clean_label), StringConstraints(min_length=1, max_length=40)]
Username = Annotated[
    str, BeforeValidator(clean_username), StringConstraints(min_length=3, max_length=32)
]
Password = Annotated[str, StringConstraints(min_length=8, max_length=128)]
WebUrl = Annotated[
    str,
    BeforeValidator(clean_line),
    StringConstraints(min_length=1, max_length=MAX_URL_LENGTH),
    AfterValidator(check_url),
]
