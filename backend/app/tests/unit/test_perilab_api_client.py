# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import HTTPException

from backend.app.support.perilab_api_client import PeriLabApiClient


def test_offline_api_raises_503():
    # Nothing listens on port 1 - connection refused.
    client = PeriLabApiClient("http://127.0.0.1:1", timeout=2)
    assert client.health() is False
    with pytest.raises(HTTPException) as exc_info:
        client.get_job("x")
    assert exc_info.value.status_code == 503
