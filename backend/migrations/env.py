import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure backend module imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Import your application's metadata object for 'autogenerate' support
from db.database import Base  # noqa: E402
target_metadata = Base.metadata

import config as app_config  # noqa: E402


def _sync_url_from_async(url: str) -> str:
    """Convert async dialect URLs to synchronous driver URLs for Alembic.

    Examples:
      - sqlite+aiosqlite:///./helplink.db -> sqlite:///./helplink.db
      - postgresql+asyncpg://user:pass@host/db -> postgresql+psycopg2://user:pass@host/db
    """
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
    # If already a sync URL, return as-is
    return url


# Override the sqlalchemy.url in alembic config with the app config value
app_db = getattr(app_config, "DATABASE_URL", None)
if app_db:
    sync_url = _sync_url_from_async(app_db)
    config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
