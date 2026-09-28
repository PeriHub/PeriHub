# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Finding and loading model generators — the one place that knows the on-disk layout.

    models/<Name>/       built-in (tracked in git), win over own models of the same name
    own_models/<Name>/   user models (mounted volume)
        <Name>.yaml | <Name>.py     exactly one — the generator
        analysis.py                 optional @analysis functions for a YAML model
        <Name>.json                 optional default input deck (ModelData)

Metadata (title, requirements, ...) is read statically — YAML parsing / `ast` for Python — so
listing models and installing requirements never imports user code whose requirements may be
missing. Python files are loaded by path, fresh on every call, so saved edits apply at once.
"""

import ast
import importlib.util
import os
import sys
from pathlib import Path

import yaml

from . import model_api, shapes
from .model_api import PeriHubModel
from .yaml_model import ModelSpecError, model_class, requirements

APP_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIRS = {"built_in": APP_DIR / "models", "own": APP_DIR / "own_models"}
LEGACY_MESSAGE = "legacy model format (Valves/main) — see docs/OwnModels.md to convert it"


def _register_perihub_module():
    """Model files write `from perihub import PeriHubModel, Param, box, ...`."""
    if "perihub" in sys.modules:
        return
    module = type(sys)("perihub")
    module.__doc__ = "Public API for PeriHub model files (see docs/OwnModels.md)."
    for name in ("PeriHubModel", "Param", "analysis", "AnalysisContext", "odd_count"):
        setattr(module, name, getattr(model_api, name))
    for name in ("Shape", "box", "sphere", "ellipsoid", "cylinder", "cone", "polygon"):
        setattr(module, name, getattr(shapes, name))
    sys.modules["perihub"] = module


_register_perihub_module()


def find_model(name: str) -> tuple[Path, str]:
    """(generator file, "yaml" | "python"); built-in models first."""
    if not name or "/" in name or "\\" in name or name.startswith("."):
        raise LookupError(f"Model {name} not found")
    for directory in MODEL_DIRS.values():
        found = _generator_file(directory / name)
        if found:
            return found
    raise LookupError(f"Model {name} not found")


def _import_file(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _model_subclasses(module):
    return [
        value
        for value in vars(module).values()
        if isinstance(value, type)
        and issubclass(value, PeriHubModel)
        and value is not PeriHubModel
        and value.__module__ == module.__name__
    ]


def load_model(name: str) -> type[PeriHubModel]:
    """The model's class. LookupError says why it can't be used (not found, legacy, broken)."""
    path, fmt = find_model(name)
    try:
        if fmt == "yaml":
            return model_class(path.read_text(encoding="utf-8"), name)
        module = _import_file(path, f"perihub_models.{name}")
    except ModelSpecError as e:
        raise LookupError(f"Model {name}: {e}") from e
    except Exception as e:
        raise LookupError(f"Model {name} could not be loaded: {e}") from e
    classes = _model_subclasses(module)
    if not classes:
        raise LookupError(f"Model {name}: {LEGACY_MESSAGE}")
    if len(classes) > 1:
        raise LookupError(f"Model {name} defines {len(classes)} PeriHubModel classes; keep exactly one")
    return classes[0]


# --- analyses --------------------------------------------------------------------------------


def _analysis_module(name: str):
    path, fmt = find_model(name)
    if fmt == "yaml":
        path = path.parent / "analysis.py"
        if not path.is_file():
            return None
    return _import_file(path, f"perihub_analyses.{name}")


def load_analyses(name: str) -> dict:
    """{id: function} of the model's @analysis functions, in file order."""
    try:
        module = _analysis_module(name)
    except Exception as e:
        raise LookupError(f"Analyses of {name} could not be loaded: {e}") from e
    if module is None:
        return {}
    return {
        value.perihub_analysis["id"]: value
        for value in vars(module).values()
        if callable(value) and hasattr(value, "perihub_analysis")
    }


# --- listing ---------------------------------------------------------------------------------


def _python_metadata(path: Path) -> dict:
    """Literal class attributes of the PeriHubModel subclass, without importing the file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and any(
            (isinstance(b, ast.Name) and b.id == "PeriHubModel")
            or (isinstance(b, ast.Attribute) and b.attr == "PeriHubModel")
            for b in node.bases
        ):
            meta = {}
            for statement in node.body:
                if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                    target = statement.targets[0]
                    if isinstance(target, ast.Name):
                        try:
                            meta[target.id] = ast.literal_eval(statement.value)
                        except ValueError:
                            pass
            return meta
    raise LookupError(LEGACY_MESSAGE)


def _generator_file(folder: Path) -> tuple[Path, str] | None:
    for suffix, fmt in ((".yaml", "yaml"), (".py", "python")):
        if (folder / (folder.name + suffix)).is_file():
            return folder / (folder.name + suffix), fmt
    return None


def metadata(folder: Path) -> dict:
    """What the model list shows. Never raises: a broken model is listed with `error`."""
    path, fmt = _generator_file(folder)
    info = {
        "file": folder.name,
        "title": folder.name,
        "description": "",
        "author": "",
        "version": "",
        "requirements": "",
        "format": fmt,
    }
    try:
        if fmt == "yaml":
            meta = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if not isinstance(meta, dict):
                raise ModelSpecError("the model file must be a YAML mapping")
        else:
            meta = _python_metadata(path)
    except (LookupError, ModelSpecError, yaml.YAMLError, SyntaxError, OSError) as e:
        info["error"] = str(e)
        return info
    for key in ("title", "description", "author", "version"):
        if meta.get(key):
            info[key] = str(meta[key])
    info["requirements"] = ", ".join(str(r) for r in requirements(meta))
    return info


def list_models(kind: str) -> list[dict]:
    directory = MODEL_DIRS[kind]
    if not directory.is_dir():
        return []
    folders = sorted(directory / entry for entry in os.listdir(directory) if not entry.startswith(("_", ".")))
    # A folder without a generator file (e.g. only a leftover config) isn't a model.
    return [metadata(folder) for folder in folders if folder.is_dir() and _generator_file(folder)]
