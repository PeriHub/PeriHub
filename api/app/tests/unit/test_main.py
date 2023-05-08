import json
import os

import pytest
from app.api_main import app
from fastapi.testclient import TestClient

client = TestClient(app)


@pytest.mark.parametrize(
    "model_name",
    ["Dogbone", "CompactTension", "Kalthoff-Winkler", "ENFmodel", "PlateWithHole"],
)
def test_generate_model(model_name):
    assets_path = "./assets/models"

    with open(
        os.path.join(assets_path, model_name, model_name + ".json"),
        "r",
        encoding="UTF-8",
    ) as file:
        params = json.load(file)
    response = client.post("/generateModel?model_name=" + model_name, json=params)
    assert response.status_code == 200
    assert response.json()["data"]
