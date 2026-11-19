import json
import os

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "model_name",
    [
        "Dogbone",
        "CompactTension",
        # "DCBmodel",
        # "ENFmodel",
        # "Kalthoff-Winkler",
        # "PlateWithHole",
        # "PlateWithOpening",
        # "RingOnRing",
    ],
)
def test_generate_model(model_name, no_db):
    assets_path = "./models"

    with open(
        os.path.join(assets_path, model_name, model_name + ".json"),
        "r",
        encoding="UTF-8",
    ) as file:
        params = json.load(file)
    valves = client.get(f"/models/{model_name}/params").json()
    response = client.post(f"/workspaces/{model_name}/Default/generate", json={"data": params, "valves": valves})
    assert response.status_code == 200, response.text


def test_generate_uses_block_spacing_for_horizon(no_db, monkeypatch):
    """A model's block_spacing() sets that block's horizon; the other blocks keep 2.5 * spacing."""
    from backend.app.routers import generate

    real = generate.build_point_cloud

    def with_block_dx(*args, **kwargs):
        cloud = real(*args, **kwargs)
        cloud["block_dx"] = {1: 0.01}
        return cloud

    horizons = {}
    monkeypatch.setattr(generate, "build_point_cloud", with_block_dx)
    monkeypatch.setattr(
        generate.ModelWriter,
        "create_file",
        lambda self, block_def, *a: horizons.update({b.blocksId: b.params["Horizon"] for b in block_def}),
    )
    response = client.post("/workspaces/Dogbone/Default/generate", json={})
    assert response.status_code == 200, response.text
    assert horizons[1] == pytest.approx(0.025)
    assert all(h > 0.025 for block_id, h in horizons.items() if block_id != 1)
