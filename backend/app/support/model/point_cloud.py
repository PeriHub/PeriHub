# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Run a model generator up to (but not including) writing files.

Shared by POST /generate/model (the real mesh) and POST /generate/preview
(a coarse point cloud the frontend draws instead of a hand-made preview
image), so the preview can never drift from what actually gets generated.
"""

import importlib
import sys

import numpy as np


def load_or_reload_main(model_name: str):
    """Import/reload `app.own_models.<model_name>.<model_name>` and return its `main` class."""
    module_name = f"app.own_models.{model_name}.{model_name}"
    if module_name in sys.modules:
        mod = importlib.reload(sys.modules[module_name])
    else:
        mod = importlib.import_module(module_name)
    return getattr(mod, "main")


def _is_missing(err: Exception, package: str) -> bool:
    """True if `err` means the model module itself doesn't exist (vs. existing but failing to import)."""
    return isinstance(err, ModuleNotFoundError) and bool(err.name) and package.startswith(err.name)


def load_model_class(model_name: str):
    """Built-in model first, then own_models.

    Raises LookupError: "not found" if neither exists, otherwise the real import error
    (e.g. a missing requirement), so the UI can say why a model can't be used.
    """
    builtin = f"app.models.{model_name}.{model_name}"
    try:
        return getattr(importlib.import_module(builtin), "main")
    except Exception as e:
        builtin_err = None if _is_missing(e, builtin) else e
    try:
        return load_or_reload_main(model_name)
    except Exception as e:
        err = builtin_err or (None if _is_missing(e, f"app.own_models.{model_name}.{model_name}") else e)
        if err is None:
            raise LookupError(f"Model {model_name} not found") from e
        raise LookupError(f"Model {model_name} could not be loaded: {err}") from err


def valves_to_dict(valves) -> dict:
    casts = {"int": int, "float": float, "bool": bool, "str": str}
    return {v["name"]: casts[v["value_type"]](v["value"]) for v in valves.model_dump()["valves"]}


def build_point_cloud(model_name: str, data, valves_dict: dict):
    """Returns (dx_value, x, y, z, vol, k). `vol` is whatever the generator returned (may be None).

    `data` may be modified in place by the generator's optional edit_model_data().
    """
    model = load_model_class(model_name)(valves_dict, data)
    dx_value = model.get_discretization()
    x_value, y_value, z_value, vol = model.create_geometry()
    # Optional hook; failures were always ignored here, kept that way so no existing model breaks.
    try:
        model.edit_model_data(data)
    except Exception:
        pass
    k = model.crate_block_definition(x_value, y_value, z_value, np.ones(len(x_value)))
    return dx_value, x_value, y_value, z_value, vol, k
