# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Geometry primitives for model generators, as vectorised "is this point inside?" tests.

Models never mesh: they lay a regular point grid and keep/label points by shape membership,
so a primitive is just `contains(x, y, z) -> bool array` plus a bounding box. Shapes combine
with `+` (union), `-` (difference) and `&` (intersection). In 2D all points have z = 0, so a
shape is evaluated in that plane (sphere -> circle, box -> rectangle).

`to_dict()` describes a shape for the frontend preview, which draws the outlines.
"""

import numpy as np

# Points generated exactly on a face must count as inside despite float round-off.
_REL_TOL = 1e-9


def _tol(*values) -> float:
    return _REL_TOL * (1.0 + max(float(np.max(np.abs(v))) for v in values))


def _vec(value, name) -> np.ndarray:
    arr = np.asarray(value, dtype=float).ravel()
    if arr.size == 2:
        arr = np.append(arr, 0.0)
    if arr.size != 3:
        raise ValueError(f"{name} needs 2 or 3 coordinates, got {arr.size}")
    return arr


class Shape:
    """Base class; subclasses implement `contains`, `bounds` and `to_dict`."""

    def contains(self, x, y, z) -> np.ndarray:
        raise NotImplementedError

    @property
    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError

    def __add__(self, other):
        return Union(self, other)

    def __sub__(self, other):
        return Difference(self, other)

    def __and__(self, other):
        return Intersection(self, other)

    def _described(self, **params) -> dict:
        lo, hi = self.bounds
        return {"type": type(self).__name__.lower(), **params, "bounds": [lo.tolist(), hi.tolist()]}


class Box(Shape):
    def __init__(self, min, max):  # noqa: A002 - matches the YAML keys
        self.min, self.max = _vec(min, "box.min"), _vec(max, "box.max")
        if np.any(self.max < self.min):
            raise ValueError("box.max must be >= box.min on every axis")

    def contains(self, x, y, z):
        t = _tol(self.min, self.max)
        inside = np.ones(np.shape(x), dtype=bool)
        for v, lo, hi in zip((x, y, z), self.min, self.max):
            inside &= (v >= lo - t) & (v <= hi + t)
        return inside

    @property
    def bounds(self):
        return self.min, self.max

    def to_dict(self):
        return self._described(min=self.min.tolist(), max=self.max.tolist())


class Sphere(Shape):
    def __init__(self, center, radius):
        self.center, self.radius = _vec(center, "sphere.center"), float(radius)

    def contains(self, x, y, z):
        c = self.center
        d2 = (x - c[0]) ** 2 + (y - c[1]) ** 2 + (z - c[2]) ** 2
        return d2 <= (self.radius + _tol(c, self.radius)) ** 2

    @property
    def bounds(self):
        return self.center - self.radius, self.center + self.radius

    def to_dict(self):
        return self._described(center=self.center.tolist(), radius=self.radius)


class Ellipsoid(Shape):
    def __init__(self, center, radii):
        self.center, self.radii = _vec(center, "ellipsoid.center"), _vec(radii, "ellipsoid.radii")
        if np.any(self.radii <= 0):
            raise ValueError("ellipsoid.radii must be positive")

    def contains(self, x, y, z):
        c, r = self.center, self.radii
        return ((x - c[0]) / r[0]) ** 2 + ((y - c[1]) / r[1]) ** 2 + ((z - c[2]) / r[2]) ** 2 <= 1 + _REL_TOL

    @property
    def bounds(self):
        return self.center - self.radii, self.center + self.radii

    def to_dict(self):
        return self._described(center=self.center.tolist(), radii=self.radii.tolist())


class Cone(Shape):
    """Frustum along start -> end, radius varying linearly. Cylinder is the equal-radius case."""

    def __init__(self, start, end, radius_start, radius_end):
        self.start, self.end = _vec(start, "start"), _vec(end, "end")
        self.radius_start, self.radius_end = float(radius_start), float(radius_end)
        self.axis = self.end - self.start
        self.length2 = float(self.axis @ self.axis)
        if self.length2 == 0:
            raise ValueError("start and end must differ")

    def contains(self, x, y, z):
        s, a = self.start, self.axis
        px, py, pz = x - s[0], y - s[1], z - s[2]
        t = (px * a[0] + py * a[1] + pz * a[2]) / self.length2
        dist2 = px**2 + py**2 + pz**2 - t**2 * self.length2
        radius = self.radius_start + (self.radius_end - self.radius_start) * t
        tol_t = _tol(t)
        tol_r = _tol(self.start, self.end, self.radius_start, self.radius_end)
        return (t >= -tol_t) & (t <= 1 + tol_t) & (dist2 <= (radius + tol_r) ** 2)

    @property
    def bounds(self):
        # Per axis, a disc of radius r normal to unit axis u extends r * sqrt(1 - u_i^2).
        u = self.axis / np.sqrt(self.length2)
        spread = np.sqrt(np.clip(1 - u**2, 0, None))
        lo = np.minimum(self.start - self.radius_start * spread, self.end - self.radius_end * spread)
        hi = np.maximum(self.start + self.radius_start * spread, self.end + self.radius_end * spread)
        return lo, hi

    def to_dict(self):
        return self._described(
            start=self.start.tolist(),
            end=self.end.tolist(),
            radius_start=self.radius_start,
            radius_end=self.radius_end,
        )


class Cylinder(Cone):
    def __init__(self, start, end, radius):
        super().__init__(start, end, radius, radius)

    def to_dict(self):
        return self._described(start=self.start.tolist(), end=self.end.tolist(), radius=self.radius_start)


class Polygon(Shape):
    """A 2D outline in the x/y plane, extruded along z. `z` = [z_min, z_max]; omitted means
    through everything (fine for cuts — a body needs finite bounds for its point grid)."""

    def __init__(self, points, z=None):
        self.points = np.asarray(points, dtype=float)
        if self.points.ndim != 2 or self.points.shape[1] != 2 or len(self.points) < 3:
            raise ValueError("polygon.points needs at least 3 [x, y] pairs")
        self.z = np.asarray(z if z is not None else [-np.inf, np.inf], dtype=float)
        if self.z.shape != (2,) or self.z[1] < self.z[0]:
            raise ValueError("polygon.z must be [z_min, z_max]")

    def contains(self, x, y, z):
        # Crossing-number test, vectorised over points, looping over the (few) edges.
        inside = np.zeros(np.shape(x), dtype=bool)
        px, py = self.points[:, 0], self.points[:, 1]
        for (xi, yi), (xj, yj) in zip(zip(px, py), zip(np.roll(px, -1), np.roll(py, -1))):
            if yi == yj:
                continue
            crosses = (yi > y) != (yj > y)
            inside ^= crosses & (x < (xj - xi) * (y - yi) / (yj - yi) + xi)
        t = _tol(self.z[np.isfinite(self.z)]) if np.isfinite(self.z).any() else 0
        return inside & (z >= self.z[0] - t) & (z <= self.z[1] + t)

    @property
    def bounds(self):
        lo, hi = self.points.min(axis=0), self.points.max(axis=0)
        return np.append(lo, self.z[0]), np.append(hi, self.z[1])

    def to_dict(self):
        lo, hi = self.bounds
        return {
            "type": "polygon",
            "points": self.points.tolist(),
            # JSON has no infinity; the preview only needs x/y anyway.
            "bounds": [
                [float(v) if np.isfinite(v) else None for v in lo],
                [float(v) if np.isfinite(v) else None for v in hi],
            ],
        }


class Union(Shape):
    def __init__(self, *parts):
        self.parts = parts

    def contains(self, x, y, z):
        return np.logical_or.reduce([p.contains(x, y, z) for p in self.parts])

    @property
    def bounds(self):
        los, his = zip(*(p.bounds for p in self.parts))
        return np.min(los, axis=0), np.max(his, axis=0)

    def to_dict(self):
        return self._described(parts=[p.to_dict() for p in self.parts])


class Difference(Shape):
    def __init__(self, base, cut):
        self.base, self.cut = base, cut

    def contains(self, x, y, z):
        return self.base.contains(x, y, z) & ~self.cut.contains(x, y, z)

    @property
    def bounds(self):
        return self.base.bounds

    def to_dict(self):
        return self._described(base=self.base.to_dict(), cut=self.cut.to_dict())


class Intersection(Shape):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def contains(self, x, y, z):
        return self.a.contains(x, y, z) & self.b.contains(x, y, z)

    @property
    def bounds(self):
        (alo, ahi), (blo, bhi) = self.a.bounds, self.b.bounds
        return np.maximum(alo, blo), np.minimum(ahi, bhi)

    def to_dict(self):
        return self._described(a=self.a.to_dict(), b=self.b.to_dict())


# Lower-case constructors are the public API (`box(...)`, `sphere(...)`), also used for YAML keys.
PRIMITIVES = {
    "box": Box,
    "sphere": Sphere,
    "ellipsoid": Ellipsoid,
    "cylinder": Cylinder,
    "cone": Cone,
    "polygon": Polygon,
}
box, sphere, ellipsoid, cylinder, cone, polygon = Box, Sphere, Ellipsoid, Cylinder, Cone, Polygon


def flatten(shape: Shape, role: str, block_id: int | None = None) -> list[dict]:
    """Primitive outlines for the preview. Composites are split into their parts, with the
    subtracted side of a difference tagged role "remove"."""
    if isinstance(shape, Union):
        return [d for p in shape.parts for d in flatten(p, role, block_id)]
    if isinstance(shape, Difference):
        return flatten(shape.base, role, block_id) + flatten(shape.cut, "remove", block_id)
    if isinstance(shape, Intersection):
        return flatten(shape.a, role, block_id) + flatten(shape.b, role, block_id)
    item = {"role": role, **shape.to_dict()}
    if block_id is not None:
        item["block_id"] = block_id
    return [item]
