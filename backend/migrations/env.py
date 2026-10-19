from logging.config import fileConfig

from alembic import context

from app.config import settings
from app.db.connection import build_engine, prepare_database_directory
from app.db.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata
database_url = config.get_main_option("sqlalchemy.url") or settings.database_url
SEARCH_INDEX_PREFIX = "items_fts"


def include_name(name: str | None, type_: str, _parent_names: object) -> bool:
    return not (type_ == "table" and name is not None and name.startswith(SEARCH_INDEX_PREFIX))


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    prepare_database_directory(database_url)
    engine = build_engine(database_url)
    with engine.connect() as connection:
        sqlite = connection.dialect.name == "sqlite"
        if sqlite:
            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
            connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            include_name=include_name,
        )
        with context.begin_transaction():
            context.run_migrations()
        if sqlite:
            violations = connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
            connection.commit()
            if violations:
                raise RuntimeError(f"Foreign key violations after migration: {violations}")
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
