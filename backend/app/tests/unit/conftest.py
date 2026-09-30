# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db import models  # noqa: F401 - registers tables on Base.metadata
from backend.app.db import base
from backend.app.main import app
from backend.app.support.admin_settings import set_setting


@pytest.fixture
def client(monkeypatch):
    """TestClient on a fresh in-memory SQLite DB (lifespan not started, so no background sweeper)."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    base.Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(base, "SessionLocal", session_local)

    def get_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[base.get_db] = get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def no_db(monkeypatch):
    """Run DB-less (local dev without accounts), whatever DATABASE_URL the developer's .env sets."""
    monkeypatch.setattr(base, "SessionLocal", None)


def set_instance_setting(key, value):
    """Store an instance setting in the DB of the current `client` fixture."""
    with base.SessionLocal() as db:
        set_setting(db, key, value)
