# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# `alembic/` is always a sibling of the `app` package's directory - locally
# that's backend/ (containing app/ and alembic/); in the Docker image it's
# / (containing /app, which plays the role of the `app` package via its
# directory name, and /alembic). Either way, alembic/'s parent is what
# needs to be on sys.path for `from app...` imports to resolve.
_ROOT = Path(__file__).resolve().parent.parent
if not (_ROOT / "app" / "db" / "base.py").exists():
    raise RuntimeError(
        f"Expected an 'app' package as a sibling of {Path(__file__).parent} "
        f"(looked in {_ROOT}). Run alembic from backend/ locally, or from "
        "/ in the backend container."
    )
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Import the app's models so Base.metadata is fully populated for
# autogenerate, and reuse the same DATABASE_URL the app itself reads
# (support/globals.py already calls load_dotenv()).
from app.db.base import Base
from app.db.models import (  # noqa: F401
    AdminSetting,
    JobQueueEntry,
    Material,
    ModelConfig,
    OAuthIdentity,
    Organization,
    Project,
    ProjectMembership,
    Team,
    TeamMembership,
    User,
)
from app.support.globals import database_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

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


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
