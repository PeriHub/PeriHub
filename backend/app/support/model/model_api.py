# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""The contract every model generator implements — importable in model files as `perihub`.

A model declares its UI parameters as `Param` class attributes and describes its body as a
`Shape` (see shapes.py); the base class lays the point grid, assigns blocks and reports block
bounds for the preview. YAML models (yaml_model.py) are turned into a subclass of the same
class, so there is exactly one runtime path. Result images are plain functions marked with
`@analysis`, run by POST /results/analysis with an `AnalysisContext`.

Replaces the old implicit contract (Pydantic `Valves` + lowercase `main` with
get_discretization / create_geometry / crate_block_definition).
"""

import glob
import os
from types import SimpleNamespace

import numpy as np

from .shapes import Shape, flatten

TYPE_NAMES = {bool: "bool", int: "int", float: "float", str: "str"}


class Param:
    """A UI parameter. The type (number / checkbox / text / select) follows from the default.

    options: list of choices, or "computes" / "outputs" to offer the names configured in the model.
    depends: name of a bool parameter; this one is only shown while that one is on.
    """

    def __init__(self, default, label=None, description="", options=None, depends=None):
        if type(default) not in TYPE_NAMES:
            raise TypeError(f"Param default must be bool, int, float or str, got {type(default).__name__}")
        self.default, self.label, self.description = default, label, description
        self.options, self.depends = options, depends
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def cast(self, value):
        kind = type(self.default)
        if kind is bool and isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        if kind is int and isinstance(value, float):
            return value
        return kind(value)

    def valve(self) -> dict:
        """The dict shape GET /model/getValves has always returned."""
        if isinstance(self.default, bool):
            kind = "checkbox"
        elif isinstance(self.default, (int, float)):
            kind = "number"
        else:
            kind = "select" if self.options else "text"
        return {
            "name": self.name,
            "type": kind,
            "value": self.default,
            "value_type": TYPE_NAMES[type(self.default)],
            "label": self.label or self.name.replace("_", " ").title(),
            "description": self.description or self.label or self.name,
            "options": self.options,
            "depends": self.depends,
        }


def odd_count(discretization) -> int:
    """Old models' node count: always odd, so a node row lies on the mid-plane."""
    return 2 * int(discretization / 2) + 1


class PeriHubModel:
    """Subclass this in `<Name>.py`; see docs/OwnModels.md."""

    title: str = ""
    description: str = ""
    author: str = ""
    version: str = "0.1.0"
    requirements: list = []

    def __init__(self, params: dict | None = None, model_data=None):
        params = params or {}
        for p in self.params():
            setattr(self, p.name, p.cast(params[p.name]) if params.get(p.name) is not None else p.default)
        self.model_data = model_data
        self.two_d = bool(model_data.model.twoDimensional) if model_data is not None else False

    @classmethod
    def params(cls) -> list[Param]:
        seen, result = set(), []
        for klass in reversed(cls.__mro__):
            for name, value in vars(klass).items():
                if isinstance(value, Param) and name not in seen:
                    seen.add(name)
                    result.append(value)
        return result

    # --- what a model defines -------------------------------------------------------------

    def geometry(self) -> Shape:
        raise NotImplementedError("define geometry() (or points() for a custom point cloud)")

    def blocks(self, x, y, z):
        """{block_id: Shape or bool array} (or a list of (id, region) pairs); later entries
        override earlier ones, unmatched points are block 1."""
        return {}

    def edit_model_data(self, model_data) -> None:
        """Optional: adjust the input deck to the generated geometry (e.g. move a bond filter)."""

    def block_regions(self, raster) -> list[dict]:
        """Blocks as preview regions (regions.py): shapes exactly, arrays sampled by calling
        blocks() on the raster's points. YAML models override this to read their expressions."""
        from .regions import shape_region

        regions = self.blocks(raster.x, raster.y, raster.z)
        result = []
        for block_id, region in regions.items() if isinstance(regions, dict) else regions:
            region = shape_region(region, raster) if isinstance(region, Shape) else raster.leaf(region)
            result.append({"id": int(block_id), "region": region})
        return result

    @property
    def spacing(self) -> float:
        """Point distance. Default: the shortest edge of the geometry (x/y only in 2D) split into
        an odd number (DISCRETIZATION) of points."""
        if not hasattr(self, "DISCRETIZATION"):
            raise AttributeError("define a DISCRETIZATION parameter or override spacing")
        return self._spacing_for(self.geometry())

    def _spacing_for(self, shape) -> float:
        lo, hi = shape.bounds
        edges = (hi - lo)[: 2 if self.two_d else 3]
        return float(min(e for e in edges if e > 0)) / odd_count(self.DISCRETIZATION)

    def grid_origin(self):
        """A point the grid passes through; default: the geometry's lower corner."""
        return None

    def points(self):
        """Advanced: return (x, y, z, volume_or_None) for a custom point cloud."""
        shape, dx = self.geometry(), self.spacing
        lo, hi = shape.bounds
        origin = self.grid_origin()
        origin = lo if origin is None else np.asarray(origin, dtype=float)
        used = 2 if self.two_d else 3
        if not np.all(np.isfinite(lo[:used])) or not np.all(np.isfinite(hi[:used])):
            raise ValueError("the geometry is unbounded — give every added polygon a z range")
        axes = [_axis(lo[i], hi[i], origin[i], dx) for i in range(used)] + [np.zeros(1)] * (3 - used)
        # indexing="xy" keeps the old create_rectangle point order (y rows, then x, then z).
        gx, gy, gz = (g.ravel() for g in np.meshgrid(*axes))
        keep = shape.contains(gx, gy, gz)
        return gx[keep], gy[keep], gz[keep], None

    # --- what the platform calls ----------------------------------------------------------

    def build(self, summary: bool = True) -> dict:
        """Run the generator; everything /generate/model and /generate/preview need. `summary`:
        also shape outlines and per-block bounds/labels (preview only; costs time on big meshes)."""
        dx = self.spacing
        x, y, z, vol = (np.asarray(a) if a is not None else None for a in self.points())
        self.edit_model_data(self.model_data)

        shapes, model_lo, model_hi = [], None, None
        try:
            geometry = self.geometry()
        except NotImplementedError:
            geometry = None
        if geometry is not None:
            shapes = flatten(geometry, "add")
            model_lo, model_hi = geometry.bounds

        k = np.ones(len(x), dtype=int)
        block_shapes = {}
        regions = self.blocks(x, y, z)
        for block_id, region in regions.items() if isinstance(regions, dict) else regions:
            if isinstance(region, Shape):
                block_shapes[int(block_id)] = region
                shapes += flatten(region, "block", int(block_id))
                region = region.contains(x, y, z)
            k = np.where(np.broadcast_to(np.asarray(region, dtype=bool), k.shape), int(block_id), k)

        return {
            "dx": [dx, dx, dx],
            "x": x,
            "y": y,
            "z": z,
            "volume": vol,
            "block": k,
            "shapes": shapes,
            "blocks": block_summary(x, y, k, block_shapes, model_lo, model_hi, dx) if summary else [],
        }


def _axis(lo, hi, origin, dx):
    """Grid coordinates origin + i*dx that lie within [lo, hi] (inclusive, round-off tolerant)."""
    eps = 1e-9
    first = int(np.ceil((lo - origin) / dx - eps))
    last = int(np.floor((hi - origin) / dx + eps))
    # np.arange's own float stepping (not origin + i*dx) reproduces the old generators' coordinates
    # bit for bit, which matters for points exactly on a block condition like `x <= 4 * spacing`.
    start = origin + first * dx
    return np.arange(start, start + (last - first + 0.5) * dx, dx)


def _label_anchors(x, y, k, dx) -> dict:
    """{block id: (x, y)}: the block's point deepest inside it — most room to its edges, holes
    and neighbouring blocks — found with a distance transform over the points' x/y grid cells.
    Ties go to the point nearest the block's centroid."""
    from scipy.ndimage import distance_transform_edt

    ix = np.round((x - x.min()) / dx).astype(int) + 1  # +1: an empty border around everything
    iy = np.round((y - y.min()) / dx).astype(int) + 1
    grid = np.zeros((iy.max() + 2, ix.max() + 2), dtype=int)
    grid[iy, ix] = k  # in 3D, points above each other share a cell; one of them wins
    anchors = {}
    for block_id in np.unique(k):
        depth = distance_transform_edt(grid == block_id)
        if depth.max() == 0:
            continue
        rows, cols = np.nonzero(depth == depth.max())
        px, py = x.min() + (cols - 1) * dx, y.min() + (rows - 1) * dx
        mask = k == block_id
        i = int(np.argmin((px - x[mask].mean()) ** 2 + (py - y[mask].mean()) ** 2))
        anchors[int(block_id)] = (float(px[i]), float(py[i]))
    return anchors


def block_summary(x, y, k, block_shapes, model_lo, model_hi, dx) -> list[dict]:
    """Per block: x/y bounds and a label anchor for the preview. Shape blocks use the shape's
    bounds (clipped to the model); others the extent of their points."""
    anchors = _label_anchors(x, y, k, dx) if len(x) else {}
    result = []
    for block_id in sorted(set(k.tolist())):
        mask = k == block_id
        bx, by = x[mask], y[mask]
        if block_id in block_shapes and model_lo is not None:
            lo, hi = block_shapes[block_id].bounds
            lo, hi = np.maximum(lo, model_lo), np.minimum(hi, model_hi)
            bounds = {"minX": lo[0], "maxX": hi[0], "minY": lo[1], "maxY": hi[1]}
        else:
            bounds = {"minX": bx.min(), "maxX": bx.max(), "minY": by.min(), "maxY": by.max()}
        if block_id in anchors:
            label_x, label_y = anchors[block_id]
        else:  # fallback: the block's point nearest its centroid
            i = int(np.argmin((bx - bx.mean()) ** 2 + (by - by.mean()) ** 2))
            label_x, label_y = float(bx[i]), float(by[i])
        result.append(
            {
                "id": int(block_id),
                "bounds": {key: float(v) for key, v in bounds.items()},
                "labelX": label_x,
                "labelY": label_y,
            }
        )
    return result


# --- analyses --------------------------------------------------------------------------------


def analysis(label: str, **params: Param):
    """Mark a function `fn(ctx) -> Figure | path` as a result image the user can run."""

    def mark(fn):
        for name, param in params.items():
            param.name = name
        fn.perihub_analysis = {"id": fn.__name__, "label": label, "params": list(params.values())}
        return fn

    return mark


class AnalysisContext(SimpleNamespace):
    """Passed to an @analysis function: analysis parameters as attributes, plus helpers."""

    def __init__(self, params: dict, analysis_params: dict, result_dir: str, model_name: str, model_data=None):
        super().__init__(**analysis_params)
        self.params = SimpleNamespace(**params)
        self.result_dir = result_dir
        self.model_name = model_name
        self.model_data = model_data

    def path(self, filename: str) -> str:
        return os.path.join(self.result_dir, filename)

    def csv(self, output: str):
        """This run's `<model>_<output>.csv` as a pandas DataFrame."""
        import pandas as pd

        file = self.path(f"{self.model_name}_{output}.csv")
        if not os.path.exists(file):
            raise FileNotFoundError(f"{os.path.basename(file)} not found — has the job written this output?")
        return pd.read_csv(file)

    def files(self, extension: str) -> list[str]:
        """All result files with this extension (e.g. ".csv"), sorted."""
        return sorted(glob.glob(os.path.join(self.result_dir, "*" + extension)))

    @property
    def deviations_enabled(self) -> bool:
        deviations = getattr(self.model_data, "deviations", None)
        return bool(deviations and deviations.enabled)

    def output_files(self, output: str, extension: str) -> list[str]:
        """Result files of one output — the run's own, or one per sample when deviations are on."""
        from ..file_handler import FileHandler

        return FileHandler.get_all_output_files_with_extension(
            self.result_dir, self.model_name, output, extension, self.deviations_enabled
        )

    @staticmethod
    def crack_length(exodus_file: str, step: int = -1):
        """(crack length, crack width, time) at `step` of an Exodus result, via CrackAnalysis."""
        from ..results.crack_analysis import CrackAnalysis

        return CrackAnalysis.get_crack_length(exodus_file, step)

    def figure(self, **kwargs):
        """A fresh matplotlib (fig, ax) that doesn't touch pyplot's global state."""
        from matplotlib.figure import Figure

        fig = Figure(**kwargs)
        return fig, fig.subplots()
