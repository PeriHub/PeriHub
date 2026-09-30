# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import textwrap

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routers import results
from backend.app.support.model import loader

client = TestClient(app)

MODEL = """
from perihub import Param, PeriHubModel, analysis, box


class Model(PeriHubModel):
    title = "Bar"
    LENGTH = Param(4.0, "Length")
    spacing = 1.0

    def geometry(self):
        return box([0, 0, 0], [self.LENGTH, 1, 0])


@analysis("Force curve", OUTPUT=Param("CSV", "Output", options="outputs"), SCALE=Param(2.0, "Scale"))
def force(ctx):
    df = ctx.csv(ctx.OUTPUT)
    fig, ax = ctx.figure()
    ax.plot(df["Time"], df["Force"] * ctx.SCALE * ctx.params.LENGTH)
    return fig


@analysis("Escape")
def escape(ctx):
    return "../../etc/passwd"


@analysis("Broken")
def broken(ctx):
    return ctx.csv("Missing")
"""


@pytest.fixture
def bar_model(tmp_path, monkeypatch):
    own = tmp_path / "own_models"
    (own / "Bar").mkdir(parents=True)
    (own / "Bar" / "Bar.py").write_text(textwrap.dedent(MODEL), encoding="utf-8")
    monkeypatch.setitem(loader.MODEL_DIRS, "own", own)

    run = tmp_path / "run"
    run.mkdir()
    (run / "Bar_CSV.csv").write_text("Time,Force\n0,0\n1,2\n2,3\n", encoding="utf-8")
    monkeypatch.setattr(results, "_result_folder", lambda *_: str(run))
    return run


def _body():
    with open(loader.APP_DIR / "assets" / "config_template.json", encoding="UTF-8") as file:
        data = json.load(file)
    valves = client.get("/models/Bar/params").json()
    return {"data": data, "valves": valves, "analysis_params": {"SCALE": 3}}


def test_lists_analyses_with_their_params(bar_model):
    analyses = client.get("/models/Bar/analyses").json()
    assert [a["id"] for a in analyses] == ["force", "escape", "broken"]
    assert [(p["name"], p["type"], p["options"]) for p in analyses[0]["params"]] == [
        ("OUTPUT", "select", "outputs"),
        ("SCALE", "number", None),
    ]


def test_model_without_analyses_lists_none():
    assert client.get("/models/DCBmodel/analyses").json() == []


def test_runs_analysis_and_returns_png(bar_model):
    response = client.post("/results/analysis", params={"model_name": "Bar", "analysis_id": "force"}, json=_body())
    assert response.status_code == 200, response.text
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG")


def test_rejects_paths_outside_the_result_folder(bar_model):
    response = client.post("/results/analysis", params={"model_name": "Bar", "analysis_id": "escape"}, json=_body())
    assert response.status_code == 422
    assert "outside the result folder" in response.json()["detail"]


def test_analysis_errors_are_422_with_message(bar_model):
    response = client.post("/results/analysis", params={"model_name": "Bar", "analysis_id": "broken"}, json=_body())
    assert response.status_code == 422
    assert "Bar_Missing.csv not found" in response.json()["detail"]


def test_unknown_analysis_is_404(bar_model):
    response = client.post("/results/analysis", params={"model_name": "Bar", "analysis_id": "nope"}, json=_body())
    assert response.status_code == 404
