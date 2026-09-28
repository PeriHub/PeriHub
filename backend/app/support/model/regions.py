# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""The model preview as regions instead of points, so the frontend can draw exact edges.

A region is a JSON tree the frontend turns into SVG masks:

    {"type": "all" | "none"}
    {"type": "halfplane", "a", "b", "c", "strict"}       a*x + b*y <= c  (< if strict)
    {"type": "shape", "shape": Shape.to_dict()}          a primitive's outline in the x/y view
    {"type": "and" | "or", "children": [...]}, {"type": "not", "child": ...}
    {"type": "raster", "x0", "y0", "width", "height", "png"}   fallback: a sampled mask

The view is the slice z = 0 in 2D and a view from +z (top view) in 3D. `where:` conditions of
YAML models are read from their expression tree: comparisons that are affine in x and y become
half-planes, and/or/not stay operators; anything else (curved formulas, z in 3D) is sampled on a
fine grid — independent of the mesh discretization — as a raster leaf. Python blocks given as
shapes are exact; given as arrays they are sampled the same way.
"""

import ast
import base64
import struct
import zlib
from functools import cached_property

import numpy as np

from .expr import evaluate
from .shapes import Box, Cone, Difference, Ellipsoid, Intersection, Polygon, Shape, Sphere, Union

RASTER_PIXELS = 400  # along the longer side of the view
RASTER_LAYERS = 16  # z samples of the top view in 3D

ALL, NONE = {"type": "all"}, {"type": "none"}


# --- raster leaves ---------------------------------------------------------------------------


def _png(mask: np.ndarray) -> str:
    """Grayscale PNG (white = inside) of a (ny, nx) mask whose row 0 is the lowest y."""
    rows = (mask[::-1] * 255).astype(np.uint8)  # images run top to bottom
    raw = b"".join(b"\x00" + row.tobytes() for row in rows)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", mask.shape[1], mask.shape[0], 8, 0, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    return base64.b64encode(png).decode()


class Raster:
    """Sample grid over the model's x/y bounds (pixel centres); in 3D also z layers, because a
    top-view pixel shows a condition if it holds at any height inside the body."""

    def __init__(self, model):
        self.model = model
        lo, hi = model.geometry().bounds
        self.lo, self.hi, self.two_d = lo, hi, model.two_d
        width, height = float(hi[0] - lo[0]), float(hi[1] - lo[1])
        scale = RASTER_PIXELS / max(width, height, 1e-12)
        self.nx, self.ny = max(1, round(width * scale)), max(1, round(height * scale))

    # The grid and body mask are only built if something actually needs sampling.
    @cached_property
    def _grid(self):
        lo, hi = self.lo, self.hi
        xs = lo[0] + (np.arange(self.nx) + 0.5) * (hi[0] - lo[0]) / self.nx
        ys = lo[1] + (np.arange(self.ny) + 0.5) * (hi[1] - lo[1]) / self.ny
        flat = self.two_d or not np.isfinite(lo[2] + hi[2])
        zs = np.zeros(1) if flat else np.linspace(lo[2], hi[2], RASTER_LAYERS)
        gz, gy, gx = np.meshgrid(zs, ys, xs, indexing="ij")  # (nz, ny, nx)
        return gx.ravel(), gy.ravel(), gz.ravel(), gz.shape

    x = property(lambda self: self._grid[0])
    y = property(lambda self: self._grid[1])
    z = property(lambda self: self._grid[2])

    @cached_property
    def body(self):
        return None if self.two_d else self.model.geometry().contains(self.x, self.y, self.z)

    def leaf(self, inside) -> dict:
        """Raster region of a condition given as values at (self.x, self.y, self.z)."""
        mask = np.broadcast_to(np.asarray(inside, dtype=bool), self.x.shape)
        if self.body is not None:
            mask = mask & self.body
        mask = mask.reshape(self._grid[3]).any(axis=0)
        if mask.all():
            return ALL
        if not mask.any():
            return NONE
        return {
            "type": "raster",
            "x0": float(self.lo[0]),
            "y0": float(self.lo[1]),
            "width": float(self.hi[0] - self.lo[0]),
            "height": float(self.hi[1] - self.lo[1]),
            "png": _png(mask),
        }


# --- shapes ----------------------------------------------------------------------------------


def shape_region(shape: Shape, raster: Raster) -> dict:
    if isinstance(shape, Union):
        return {"type": "or", "children": [shape_region(p, raster) for p in shape.parts]}
    if isinstance(shape, Difference):
        return {"type": "and", "children": [shape_region(shape.base, raster), _not(shape_region(shape.cut, raster))]}
    if isinstance(shape, Intersection):
        return {"type": "and", "children": [shape_region(shape.a, raster), shape_region(shape.b, raster)]}
    if not raster.two_d:
        # ponytail: 3D top view projects each primitive, so a cut-out counts as going through the
        # full thickness (true for all current models); a blind hole would need raster leaves.
        return {"type": "shape", "shape": shape.to_dict()}
    return _slice_z0(shape, raster)


def _slice_z0(shape: Shape, raster: Raster) -> dict:
    """A primitive's cut at z = 0, as an exact outline where the frontend can draw one."""
    if isinstance(shape, Box):
        return {"type": "shape", "shape": shape.to_dict()} if shape.min[2] <= 1e-12 and shape.max[2] >= -1e-12 else NONE
    if isinstance(shape, Polygon):
        return {"type": "shape", "shape": shape.to_dict()} if shape.z[0] <= 0 <= shape.z[1] else NONE
    if isinstance(shape, Ellipsoid):
        c, r = shape.center, shape.radii
        k = 1 - (c[2] / r[2]) ** 2
        if k <= 0:
            return NONE
        return {"type": "shape", "shape": Ellipsoid([c[0], c[1], 0], [r[0] * k**0.5, r[1] * k**0.5, r[2]]).to_dict()}
    if isinstance(shape, Sphere):
        r2 = shape.radius**2 - shape.center[2] ** 2
        if r2 <= 0:
            return NONE
        return {"type": "shape", "shape": Sphere([shape.center[0], shape.center[1], 0], r2**0.5).to_dict()}
    if isinstance(shape, Cone):
        s, e = shape.start, shape.end
        if s[2] == 0 and e[2] == 0:  # axis in the plane: the cut is the outline itself
            return {"type": "shape", "shape": shape.to_dict()}
        if s[0] == e[0] and s[1] == e[1]:  # axis along z: a circle
            t = -s[2] / (e[2] - s[2])
            if not 0 <= t <= 1:
                return NONE
            radius = shape.radius_start + (shape.radius_end - shape.radius_start) * t
            return {"type": "shape", "shape": Sphere([s[0], s[1], 0], radius).to_dict()}
    return raster.leaf(shape.contains(raster.x, raster.y, raster.z))


def _not(region: dict) -> dict:
    if region is ALL:
        return NONE
    if region is NONE:
        return ALL
    return {"type": "not", "child": region}


# --- where: expressions ----------------------------------------------------------------------

COORDS = ("x", "y", "z")


class _Affine:
    """a·x + b·y + c·z + d."""

    def __init__(self, coef, const=0.0):
        self.coef, self.const = np.asarray(coef, dtype=float), float(const)

    def __add__(self, other):
        o = _as_affine(other)
        return _Affine(self.coef + o.coef, self.const + o.const)

    __radd__ = __add__

    def __sub__(self, other):
        return self + (-1) * _as_affine(other)

    def __rsub__(self, other):
        return _as_affine(other) - self

    def __mul__(self, k):
        return _Affine(self.coef * k, self.const * k)

    __rmul__ = __mul__

    def __neg__(self):
        return self * -1


def _as_affine(value):
    return value if isinstance(value, _Affine) else _Affine([0, 0, 0], value)


def _uses_coords(node) -> bool:
    return any(isinstance(n, ast.Name) and n.id in COORDS for n in ast.walk(node))


def _affine(node, names):
    """The node as a number or _Affine, or None if it isn't affine in x, y, z."""
    if not _uses_coords(node):
        value = evaluate(ast.unparse(node), names)
        return float(value) if np.isscalar(value) else None
    if isinstance(node, ast.Name):
        return _Affine(np.eye(3)[COORDS.index(node.id)])
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _affine(node.operand, names)
        return None if value is None else (-value if isinstance(node.op, ast.USub) else value)
    if isinstance(node, ast.BinOp):
        left, right = _affine(node.left, names), _affine(node.right, names)
        if left is None or right is None:
            return None
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult) and not (isinstance(left, _Affine) and isinstance(right, _Affine)):
            return left * right
        if isinstance(node.op, ast.Div) and not isinstance(right, _Affine) and right != 0:
            return left * (1 / right)
    return None


_LESS = (ast.Lt, ast.LtE)
_GREATER = (ast.Gt, ast.GtE)


def where_region(expression: str, names: dict, raster: Raster) -> dict:
    """Region of a `where:` condition (names: parameters, spacing, two_d — not x/y/z)."""
    return _region(ast.parse(expression.strip(), mode="eval").body, names, raster)


def _region(node, names, raster):
    if isinstance(node, ast.BoolOp):
        children = [_region(v, names, raster) for v in node.values]
        return {"type": "and" if isinstance(node.op, ast.And) else "or", "children": children}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return _not(_region(node.operand, names, raster))
    if isinstance(node, ast.Compare) and len(node.ops) > 1:
        pairs = zip([node.left, *node.comparators[:-1]], node.ops, node.comparators)
        return {
            "type": "and",
            "children": [_region(ast.Compare(left, [op], [right]), names, raster) for left, op, right in pairs],
        }
    if isinstance(node, ast.Compare) and isinstance(node.ops[0], _LESS + _GREATER):
        left, right = _affine(node.left, names), _affine(node.comparators[0], names)
        if left is not None and right is not None:
            diff = _as_affine(left) - _as_affine(right)  # condition: diff < 0 (or > 0)
            if isinstance(node.ops[0], _GREATER):
                diff = -diff
            if raster.two_d or diff.coef[2] == 0:  # z is 0 in 2D; z-dependent in 3D -> raster
                a, b = diff.coef[:2]
                if a == 0 and b == 0:
                    return ALL if diff.const <= 0 else NONE
                strict = isinstance(node.ops[0], (ast.Lt, ast.Gt))
                return {"type": "halfplane", "a": float(a), "b": float(b), "c": float(-diff.const), "strict": strict}
    # Anything else: sample the condition itself.
    return raster.leaf(evaluate(ast.unparse(node), {**names, "x": raster.x, "y": raster.y, "z": raster.z}))


def preview_regions(model) -> dict | None:
    """{"body": region, "blocks": [{"id", "region"}]} for the preview, or None when the model
    makes its own point cloud (points() overridden) and has no primitives to draw."""
    from .model_api import PeriHubModel

    if type(model).points is not PeriHubModel.points:
        return None
    raster = Raster(model)
    return {"body": shape_region(model.geometry(), raster), "blocks": model.block_regions(raster)}
