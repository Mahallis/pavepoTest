from importlib import import_module
from logging.config import fileConfig
from os import getenv

from alembic import context
from config.db_session import Base
from config.general import BASE_PATH
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

config = context.config

load_dotenv(BASE_PATH.parent / ".env")

MODELS_FILE_NAME = ["audio_storage.models", "auth.models"]

DATABASE_URL = (
    f"postgresql+asyncpg://{getenv('POSTGRES_USER')}:"
    f"{getenv('POSTGRES_PASSWORD')}@{getenv('DB_HOST')}:"
    f"{getenv('DB_PORT')}/{getenv('POSTGRES_NAME')}"
)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

for model in MODELS_FILE_NAME:  # Динамически добавляю модели из модулей
    try:
        import_module(model)
    except ModuleNotFoundError as e:
        print(f"Не найден модуль {model}: {e}")

target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Выполняет миграции."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Запускает миграции в асинхронном режиме."""
    connectable = create_async_engine(DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_async_migrations())
