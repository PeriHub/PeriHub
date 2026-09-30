# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Run a model generator up to (but not including) writing files.

Shared by POST /workspaces/{model}/{folder}/generate (the real mesh) and POST /models/{name}/preview
(a coarse point cloud the frontend draws instead of a hand-made preview
image), so the preview can never drift from what actually gets generated.
"""

from .loader import load_model
from .regions import preview_regions
from .yaml_model import model_class as yaml_model_class


def valves_to_dict(valves) -> dict:
    casts = {"int": int, "float": float, "bool": bool, "str": str}
    return {v["name"]: casts[v["value_type"]](v["value"]) for v in valves.model_dump()["valves"]}


def build_point_cloud(
    model_name: str, data, valves_dict: dict, source: str | None = None, region_valves: dict | None = None
) -> dict:
    """PeriHubModel.build() of the named model (or of unsaved YAML `source`): dx, x, y, z,
    volume (may be None), block, shapes, blocks. With `region_valves`, also the preview regions
    (regions.py; None for point-cloud models) for those parameters — the preview caps the
    discretization of the points, but regions cost the same at full resolution and blocks like
    `x < 3 * spacing` must match the real mesh. `data` may be edited in place by the model."""
    model_class = yaml_model_class(source, model_name) if source is not None else load_model(model_name)
    result = model_class(valves_dict, data).build(summary=region_valves is not None)
    if region_valves is not None:
        result["regions"] = preview_regions(model_class(region_valves, data))
    return result
