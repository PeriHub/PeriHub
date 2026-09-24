# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Postgres engine/session setup.

Phase 0 of the multi-user roadmap: this module is the one place that knows
how to talk to Postgres. Everything else (models, auth, admin settings)
imports `SessionLocal`/`get_db` from here rather than creating its own
engine, so connection pooling and the DATABASE_URL are configured once.

DATABASE_URL is required for community/enterprise deployments. Trial mode
(no persistent accounts) can still run without Postgres configured - see
support/db_auth.py - but sharing model configs/materials always needs it,
so in practice every real deployment sets it.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..support.globals import database_url, log


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models (see db/models.py)."""


_engine = None
SessionLocal: sessionmaker | None = None

if database_url:
    # pool_pre_ping avoids handing out dead connections after a Postgres
    # restart/failover - cheap check, worth it for a long-lived service.
    _engine = create_engine(database_url, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
else:
    log.warning(
        "db.base: DATABASE_URL is not set - multi-user features (accounts, "
        "shared model configs/materials, admin settings) are unavailable. "
        "Trial mode still works without it."
    )


def get_engine():
    """Returns the module-level engine, or None if DATABASE_URL isn't set."""
    return _engine


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a request-scoped DB session.

    Raises RuntimeError if called without DATABASE_URL configured - callers
    that need to work in DB-less trial mode should check
    `db.base.get_engine() is not None` first rather than depending on this.
    """
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured - cannot open a DB session.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_optional() -> Generator[Session | None, None, None]:
    """Like get_db(), but yields None instead of raising when DATABASE_URL
    isn't configured - for endpoints (e.g. routers/jobs.py's fair-share
    queue) that have a degraded-but-working fallback for DB-less trial
    mode rather than requiring a database outright."""
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
