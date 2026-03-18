import asyncio
import selectors
import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Make `app` package importable ──
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings          # noqa: E402
from app.core.database import Base            # noqa: E402
from app.models import User                   
from app.models.syllabus import Syllabus            # noqa: E402, F401
from app.models.source_document import SourceDocument  # noqa: E402, F401
from app.models.pyq_question import PYQuestion      # noqa: E402, F401
from app.models.question_bank import QuestionBank   # noqa: E402, F401
from app.models.exam import Exam                    # noqa: E402, F401
from app.models.attempt import Attempt              # noqa: E402, F401
from app.models.user_analytics import UserAnalytics # noqa: E402, F401

config = context.config

# Override the sqlalchemy.url from our .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
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
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    # ── FIX for Windows ──
    # Windows uses ProactorEventLoop by default, which is incompatible
    # with asyncpg / psycopg async drivers.
    # Force SelectorEventLoop on Windows.
    if sys.platform == "win32":
        selector = selectors.SelectSelector()
        loop = asyncio.SelectorEventLoop(selector)
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_async_migrations())
        finally:
            loop.close()
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()