import argparse
import sys
from getpass import getpass

from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.db.connection import build_engine, build_session_factory, session_scope
from app.db.models import Account, AccountKind, Role
from app.db.repositories import accounts as account_repo
from app.dto.validation import Password, Username
from app.errors import AppError
from app.services.auth import create_account, issue_api_key, set_password

_username = TypeAdapter(Username)
_password = TypeAdapter(Password)


class CliError(Exception):
    pass


def _check[T](adapter: TypeAdapter[T], value: str, what: str) -> T:
    try:
        return adapter.validate_python(value)
    except ValidationError as error:
        raise CliError(f"Invalid {what}: {error.errors()[0]['msg']}") from error


def _ask_password() -> str:
    password = getpass("Password: ")
    if getpass("Repeat password: ") != password:
        raise CliError("The passwords do not match.")
    return _check(_password, password, "password")


def _get(session: Session, username: str) -> Account:
    account = account_repo.get_by_username(session, username.lower())
    if account is None:
        raise CliError(f"No account named '{username}'.")
    return account


def _create_user(session: Session, username: str, role: Role) -> None:
    name = _check(_username, username, "username")
    password = _ask_password()
    account, _ = create_account(session, AccountKind.USER, name, password, role=role)
    print(f"Created {role.value} '{account.username}'.")


def _remove_admin(session: Session, username: str) -> None:
    account = _get(session, username)
    if account.role is not Role.ADMIN:
        raise CliError(f"'{account.username}' is not an admin.")
    account.role = Role.USER
    print(f"'{account.username}' is no longer an admin.")


def _create_agent(session: Session, username: str) -> None:
    name = _check(_username, username, "username")
    account, api_key = create_account(session, AccountKind.AGENT, name, None)
    print(f"Created agent '{account.username}'. API key, shown only once:\n{api_key}")


def _rotate_key(session: Session, username: str) -> None:
    account = _get(session, username)
    if account.kind is not AccountKind.AGENT:
        raise CliError(f"'{account.username}' is not an agent.")
    print(f"New API key for '{account.username}', shown only once:\n{issue_api_key(account)}")


def _reset_password(session: Session, username: str) -> None:
    account = _get(session, username)
    if account.kind is not AccountKind.USER:
        raise CliError(f"'{account.username}' is not a user.")
    set_password(session, account, _ask_password())
    print(f"Password reset for '{account.username}'. Their sessions were ended.")


COMMANDS = {
    "create-admin": lambda session, name: _create_user(session, name, Role.ADMIN),
    "remove-admin": _remove_admin,
    "create-user": lambda session, name: _create_user(session, name, Role.USER),
    "create-agent": _create_agent,
    "rotate-key": _rotate_key,
    "reset-password": _reset_password,
}


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("username")
    args = parser.parse_args()
    engine = build_engine(settings.database_url)
    try:
        with session_scope(build_session_factory(engine)) as session:
            COMMANDS[args.command](session, args.username)
    except (CliError, AppError) as error:
        sys.exit(str(error))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
