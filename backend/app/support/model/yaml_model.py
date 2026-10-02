# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""No-code models: a YAML file becomes a `PeriHubModel` subclass.

    parameters: {NAME: {default, label, description, options, depends}}  (or NAME: default)
    geometry:   {spacing, grid_origin, add: [shape], remove: [shape], keep_only: [shape]}
    blocks:     [{id, <shape>, where}]        later entries override earlier ones
    set:        {"bondFilters[0].lowerLeftCornerY": expr}   edits the input deck

A shape is `{box|sphere|ellipsoid|cylinder|cone: {arg: expr}}`. Expressions (expr.py) see the
parameters, `spacing`, `two_d`, and in `where:` also `x`, `y`, `z`. Every error names the
YAML path it came from, which the /models editor shows next to the preview.
"""

import re

import magicattr
import numpy as np
import yaml

from .expr import ExpressionError, evaluate
from .model_api import Param, PeriHubModel
from .shapes import PRIMITIVES, Union

TOP_LEVEL = {"title", "description", "author", "version", "requirements", "parameters", "geometry", "blocks", "set"}
PARAM_KEYS = {"default", "label", "description", "options", "depends"}
GEOMETRY_KEYS = {"spacing", "grid_origin", "add", "remove", "keep_only"}
# `set:` keys are handed to magicattr, which follows any attribute/subscript path - so only plain ModelData field
# paths (`solver.finalTime`, `bondFilters[0].lowerLeftCornerY`): no `_`/dunder names that could reach module state.
SET_PATH = re.compile(r"[A-Za-z][A-Za-z0-9]*(\[\d+\])?(\.[A-Za-z][A-Za-z0-9]*(\[\d+\])?)*")


class ModelSpecError(ValueError):
    """A problem in a model file, prefixed with where it is (`blocks[1].where: ...`)."""


def _fail(path, message):
    raise ModelSpecError(f"{path}: {message}" if path else message)


def _expr(value, names, path):
    if isinstance(value, list):
        return [_expr(v, names, f"{path}[{i}]") for i, v in enumerate(value)]
    try:
        return evaluate(value, names)
    except (ExpressionError, ArithmeticError, TypeError, ValueError) as e:
        _fail(path, e)


def _shape(entry, names, path):
    """A shape entry, or None when its optional `if:` condition is false."""
    if isinstance(entry, dict) and "if" in entry:
        entry = dict(entry)
        if not _expr(entry.pop("if"), names, f"{path}.if"):
            return None
    if not isinstance(entry, dict) or len(entry) != 1 or next(iter(entry)) not in PRIMITIVES:
        _fail(path, f"expected one of {', '.join(PRIMITIVES)} (plus an optional 'if')")
    kind, args = next(iter(entry.items()))
    return _primitive(kind, args, names, f"{path}.{kind}")


def _primitive(kind, args, names, path):
    if not isinstance(args, dict):
        _fail(path, "expected a mapping of arguments")
    values = {key: _expr(value, names, f"{path}.{key}") for key, value in args.items()}
    try:
        return PRIMITIVES[kind](**values)
    except TypeError as e:
        # "Sphere.__init__() missing 1 required positional argument: 'radius'" -> without the class
        _fail(path, f"wrong arguments ({str(e).split(') ', 1)[-1]})")
    except ValueError as e:
        _fail(path, e)


def _shape_list(entries, names, path):
    if entries in (None, []):
        return []
    if not isinstance(entries, list):
        _fail(path, "expected a list of shapes")
    shapes = [_shape(entry, names, f"{path}[{i}]") for i, entry in enumerate(entries)]
    return [shape for shape in shapes if shape is not None]


def _params(spec):
    if spec is None:
        return {}
    if not isinstance(spec, dict):
        _fail("parameters", "expected a mapping NAME: {default: ...}")
    params = {}
    for name, entry in spec.items():
        path = f"parameters.{name}"
        if not isinstance(entry, dict):
            entry = {"default": entry}
        unknown = set(entry) - PARAM_KEYS
        if unknown:
            _fail(path, f"unknown key '{sorted(unknown)[0]}'")
        if "default" not in entry:
            _fail(path, "missing 'default'")
        try:
            param = Param(**entry)
        except TypeError as e:
            _fail(path, e)
        param.__set_name__(None, name)
        params[name] = param
    return params


def _validate(doc):
    if not isinstance(doc, dict):
        _fail("", "the model file must be a YAML mapping")
    unknown = set(doc) - TOP_LEVEL
    if unknown:
        _fail(sorted(unknown)[0], f"unknown section (allowed: {', '.join(sorted(TOP_LEVEL))})")
    geometry = doc.get("geometry")
    if not isinstance(geometry, dict) or not geometry.get("add"):
        _fail("geometry.add", "at least one shape is required")
    unknown = set(geometry) - GEOMETRY_KEYS
    if unknown:
        _fail(f"geometry.{sorted(unknown)[0]}", "unknown key")
    blocks = doc.get("blocks") or []
    if not isinstance(blocks, list):
        _fail("blocks", "expected a list")
    for i, block in enumerate(blocks):
        if not isinstance(block, dict) or "id" not in block:
            _fail(f"blocks[{i}]", "every block needs an 'id'")
        if not set(block) - {"id"}:
            _fail(f"blocks[{i}]", "needs a shape and/or a 'where' condition")
    if not isinstance(doc.get("set") or {}, dict):
        _fail("set", "expected a mapping of input-deck path: expression")
    for path in doc.get("set") or {}:
        if not isinstance(path, str) or not SET_PATH.fullmatch(path):
            _fail(f"set.{path}", "must be an input-deck field path like 'bondFilters[0].lowerLeftCornerY'")


def parse(text: str) -> dict:
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f"line {mark.line + 1}" if mark else "YAML"
        _fail(where, getattr(e, "problem", None) or str(e))
    _validate(doc)
    return doc


def requirements(meta: dict) -> list:
    """`requirements:` as a list; a comma-separated string is accepted too."""
    value = meta.get("requirements") or []
    return [r.strip() for r in value.split(",") if r.strip()] if isinstance(value, str) else value


def model_class(text: str, name: str = "Model") -> type[PeriHubModel]:
    doc = parse(text)
    params = _params(doc.get("parameters"))
    namespace = {
        **params,
        "title": str(doc.get("title") or name),
        "description": str(doc.get("description") or ""),
        "author": str(doc.get("author") or ""),
        "version": str(doc.get("version") or "0.1.0"),
        "requirements": requirements(doc),
        "spec": doc,
    }
    return type(name, (YamlModel,), namespace)


class YamlModel(PeriHubModel):
    spec: dict = {}

    def _names(self, with_spacing=True):
        names = {p.name: getattr(self, p.name) for p in self.params()}
        names["two_d"] = self.two_d
        if with_spacing:
            names["spacing"] = self.spacing
        return names

    @property
    def spacing(self):
        geometry = self.spec["geometry"]
        if "spacing" in geometry:
            value = _expr(geometry["spacing"], self._names(with_spacing=False), "geometry.spacing")
            if not np.isscalar(value) or value <= 0:
                _fail("geometry.spacing", "must be a positive number")
            return float(value)
        if not hasattr(self, "DISCRETIZATION"):
            _fail("geometry.spacing", "set geometry.spacing or add a DISCRETIZATION parameter")
        try:
            return self._spacing_for(self._geometry(self._names(with_spacing=False)))
        except ModelSpecError as e:
            if "unknown name 'spacing'" in str(e):
                _fail("geometry.spacing", "the geometry uses 'spacing', so set geometry.spacing explicitly")
            raise

    def geometry(self):
        return self._geometry(self._names())

    def _geometry(self, names):
        geometry = self.spec["geometry"]
        added = _shape_list(geometry["add"], names, "geometry.add")
        if not added:
            _fail("geometry.add", "every shape is switched off by its 'if'")
        shape = added[0] if len(added) == 1 else Union(*added)
        for cut in _shape_list(geometry.get("remove"), names, "geometry.remove"):
            shape = shape - cut
        for keep in _shape_list(geometry.get("keep_only"), names, "geometry.keep_only"):
            shape = shape & keep
        return shape

    def grid_origin(self):
        origin = self.spec["geometry"].get("grid_origin")
        if origin is None:
            return None
        values = _expr(origin, self._names(), "geometry.grid_origin")
        if not isinstance(values, list) or len(values) not in (2, 3):
            _fail("geometry.grid_origin", "expected [x, y] or [x, y, z]")
        return values + [0.0] * (3 - len(values))

    def blocks(self, x, y, z):
        names = {**self._names(), "x": x, "y": y, "z": z}
        regions = []
        for i, block in enumerate(self.spec.get("blocks") or []):
            path = f"blocks[{i}]"
            block_id = _expr(block["id"], names, f"{path}.id")
            shape_keys = [key for key in block if key in PRIMITIVES]
            unknown = set(block) - {"id", "where", *PRIMITIVES}
            if unknown:
                _fail(f"{path}.{sorted(unknown)[0]}", "unknown key")
            if len(shape_keys) > 1:
                _fail(path, "use one shape per block entry")
            region = None
            if shape_keys:
                kind = shape_keys[0]
                region = _primitive(kind, block[kind], names, f"{path}.{kind}")
            if "where" in block:
                condition = np.asarray(_expr(block["where"], names, f"{path}.where"), dtype=bool)
                region = condition if region is None else region.contains(x, y, z) & condition
            regions.append((block_id, region))
        return regions

    def block_regions(self, raster):
        from .regions import shape_region, where_region

        names, result = self._names(), []
        for i, block in enumerate(self.spec.get("blocks") or []):
            path = f"blocks[{i}]"
            parts = []
            for kind in PRIMITIVES:
                if kind in block:
                    parts.append(shape_region(_primitive(kind, block[kind], names, f"{path}.{kind}"), raster))
            if "where" in block:
                try:
                    parts.append(where_region(str(block["where"]), names, raster))
                except (ExpressionError, ArithmeticError, TypeError, ValueError, SyntaxError) as e:
                    _fail(f"{path}.where", e)
            region = parts[0] if len(parts) == 1 else {"type": "and", "children": parts}
            result.append({"id": int(_expr(block["id"], names, f"{path}.id")), "region": region})
        return result

    def edit_model_data(self, model_data):
        names = self._names()
        for path, value in (self.spec.get("set") or {}).items():
            result = _expr(value, names, f"set.{path}")
            try:
                magicattr.set(model_data, path, float(result) if np.isscalar(result) else result)
            except (AttributeError, IndexError, KeyError, TypeError, ValueError) as e:
                _fail(f"set.{path}", f"no such input-deck field ({e})")
