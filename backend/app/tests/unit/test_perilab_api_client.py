# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests
from fastapi import HTTPException

from backend.app.support.perilab_api_client import PeriLabApiClient


def test_offline_api_raises_503():
    # Nothing listens on port 1 - connection refused.
    client = PeriLabApiClient("http://127.0.0.1:1", timeout=2)
    assert client.health() is False
    with pytest.raises(HTTPException) as exc_info:
        client.get_job("x")
    assert exc_info.value.status_code == 503


def test_unknown_job_is_lost(monkeypatch):
    # PeriLab 404s jobs it no longer knows (e.g. after a restart).
    response = requests.Response()
    response.status_code = 404
    monkeypatch.setattr(requests, "request", lambda *a, **kw: response)
    job = PeriLabApiClient("http://perilab").get_job("x")
    assert job.status == "lost" and job.is_failed and not job.is_active
