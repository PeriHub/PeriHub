# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, timezone

import requests
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/energy", tags=["Upload Methods"])


def _signal() -> dict:
    """energy-charts.info's German grid signal: `unix_seconds` and the renewable `share` (%) per 15 min."""
    try:
        response = requests.get("https://api.energy-charts.info/signal", params={"country": "de"}, timeout=10)
    except requests.RequestException as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"energy-charts.info unreachable: {e}")
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"energy-charts.info request failed with status code {response.status_code}",
        )
    return response.json()


@router.get("/prognosis", operation_id="get_prognosis_energy")
def energy_prognosis() -> dict:
    """Forecast share of renewable power in the German grid from energy-charts.info, as `{UTC ISO time: share}`."""
    data = _signal()
    return {
        datetime.fromtimestamp(ts, timezone.utc).isoformat(): share
        for ts, share in zip(data["unix_seconds"], data["share"])
        if share is not None
    }


@router.get("/current", operation_id="get_current_energy")
def energy_current() -> float:
    """Current share of renewable power (%) in the German grid from energy-charts.info (the value nearest to now)."""
    data = _signal()
    now = datetime.now(timezone.utc).timestamp()
    points = [(ts, share) for ts, share in zip(data["unix_seconds"], data["share"]) if share is not None]
    if not points:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="energy-charts.info returned no data")
    return min(points, key=lambda p: abs(p[0] - now))[1]
