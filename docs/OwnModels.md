---
layout: default
title: Own Models
nav_order: 3
---

<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

# Own models

An own model is a specimen you describe once — its parameters, its shape, and how it is split
into blocks — and then use in the editor like the built-in ones. Create and edit models on the
**Models** page (live preview next to the editor) or directly in the `own_models/` folder.

Each model is one folder:

```text
own_models/
  MyPlate/
    MyPlate.yaml     the model — or MyPlate.py for a Python model
    analysis.py      optional: result images (YAML models only; Python models keep them in MyPlate.py)
    MyPlate.json     the default input deck (materials, boundary conditions, outputs, ...)
```

Write the model in **YAML** unless you need something it can't express; YAML needs no
programming. **Python** is for custom point clouds and logic (loops, text parameters).

## YAML models

```yaml
title: Plate with hole
description: Tension plate with a central hole
author: jt
version: 0.1.0
requirements: [] # extra pip packages, installed at startup

parameters: # shown as input fields in the editor
  DISCRETIZATION: { default: 21, label: Points over the height }
  LENGTH: { default: 50, label: Length (mm) }
  HEIGHT: { default: 20, label: Height (mm) }
  THICKNESS: { default: 4, label: Thickness (mm) }
  RADIUS: { default: 3, label: Hole radius }
  HOLE: { default: true, label: With hole }

geometry:
  spacing: HEIGHT / DISCRETIZATION # distance between points
  add: # the body: union of these shapes
    - box: { min: [0, 0, -THICKNESS / 2], max: [LENGTH, HEIGHT, THICKNESS / 2] }
  remove: # cut-outs
    - if: HOLE
      cylinder:
        {
          start: [LENGTH / 2, HEIGHT / 2, -THICKNESS],
          end: [LENGTH / 2, HEIGHT / 2, THICKNESS],
          radius: RADIUS
        }

blocks: # everything else is block 1; later rules win
  - { id: 2, where: 'x < 3 * spacing' } # left grip
  - { id: 3, box: { min: [LENGTH - 1, 0, -THICKNESS], max: [LENGTH, HEIGHT, THICKNESS] } } # right grip

set: # optional: adjust the input deck to the geometry
  bondFilters[0].lowerLeftCornerY: HEIGHT / 2
```

### Parameters

`NAME: {default, label, description, options, depends}` or just `NAME: default`.
The field type follows the default: a number gives a number field, `true`/`false` a switch,
text a text field — or a dropdown with `options: [a, b]`. `depends: OTHER` shows the field only
while the switch `OTHER` is on.

### Shapes

| Shape       | Arguments                                         |                                                                       |
| ----------- | ------------------------------------------------- | --------------------------------------------------------------------- |
| `box`       | `min: [x, y, z]`, `max: [x, y, z]`                | axis-aligned                                                          |
| `sphere`    | `center`, `radius`                                |                                                                       |
| `ellipsoid` | `center`, `radii: [a, b, c]`                      |                                                                       |
| `cylinder`  | `start`, `end`, `radius`                          | any direction                                                         |
| `cone`      | `start`, `end`, `radius_start`, `radius_end`      | a frustum; `0` gives a tip                                            |
| `polygon`   | `points: [[x, y], ...]`, optional `z: [min, max]` | a 2D outline pushed through z; without `z` it cuts through everything |

Coordinates may have 2 entries (`z` = 0). Any shape entry can carry `if: <condition>`.

`geometry.add` is the union of its shapes, `remove` cuts shapes out, `keep_only` keeps only what
lies inside its shapes. Points are laid on a regular grid with `spacing` over the body's bounding
box; `grid_origin: [x, y, z]` moves the grid so it passes through that point (e.g.
`[0, spacing / 2, 0]` keeps a point row off a crack plane at y = 0). Without `spacing` it is the
shortest edge divided by an odd number derived from `DISCRETIZATION`.

**2D:** in a two-dimensional model every point has z = 0, so shapes are cut at that plane — a
sphere becomes a circle, a box a rectangle. The same file works in 2D and 3D as long as its
shapes reach z = 0.

### Blocks

Each rule has an `id` and a shape, a `where` condition, or both (then both must hold). Points
no rule matches are block 1; when rules overlap, the later one wins.

### Expressions

Wherever a number is expected you can write an expression: the parameters, `spacing`, `two_d`
(true in 2D), `pi`, `+ - * / ** %`, comparisons (also chained: `0 < x <= LENGTH`),
`and`/`or`/`not`, and `abs sqrt sin cos tan min max floor ceil round int`. In `where` you also
have the point coordinates `x`, `y`, `z`. Nothing else is allowed — no function calls into Python.

### Errors

Mistakes are reported with where they are, e.g. `blocks[1].where: unknown name 'LENGHT'` or
`geometry.remove[0].sphere: wrong arguments (missing 1 required positional argument: 'radius')`.
The Models page shows them next to the preview while you type.

## Python models

```python
from perihub import Param, PeriHubModel, box, cylinder


class Model(PeriHubModel):
    title = "Plate with hole"
    description = "Tension plate with a central hole"
    requirements = []

    DISCRETIZATION = Param(21, "Points over the height")
    LENGTH = Param(50.0, "Length (mm)")
    HEIGHT = Param(20.0, "Height (mm)")
    MODE = Param("A", "Mode", options=["A", "B"])

    @property
    def spacing(self):
        return self.HEIGHT / self.DISCRETIZATION

    def geometry(self):
        plate = box([0, 0, -2], [self.LENGTH, self.HEIGHT, 2])
        return plate - cylinder([25, 10, -3], [25, 10, 3], 3)   # + union, - cut, & intersect

    def blocks(self, x, y, z):
        return {2: x < 3 * self.spacing, 3: box([49, 0, -3], [50, 20, 3])}

    def edit_model_data(self, model_data):                      # optional
        model_data.bondFilters[0].lowerLeftCornerY = self.HEIGHT / 2
```

Parameters are attributes (`self.LENGTH`); `self.two_d` and `self.model_data` are available.
Instead of `geometry()` a model can override `points()` and return `(x, y, z, volume_or_None)`
for a point cloud that isn't a grid (see the built-in Dogbone). `grid_origin()` returns the point
the grid passes through.

## Analyses (result images)

An analysis turns a run's results into an image. In the editor, the **Analysis** button (next
to Plot) lists a model's analyses, asks for their parameters, and shows the image in the
**Analysis** tab.

```python
from perihub import Param, analysis


@analysis(
    "Force over displacement",
    OUTPUT=Param("CSV", "Output", options="outputs"),        # dropdown of the model's outputs
    LOAD=Param("External_Forces", "Load", options="computes"),
)
def force_displacement(ctx):
    df = ctx.csv(ctx.OUTPUT)            # <model>_<OUTPUT>.csv of this run, as a DataFrame
    fig, ax = ctx.figure()
    ax.plot(df["External_Displacementsy"], df[ctx.LOAD + "y"])
    ax.set_xlabel("Displacement (mm)")
    return fig                          # or the path of an image written into ctx.result_dir
```

`ctx` offers the analysis parameters as attributes and

- `ctx.params` — the model's parameters (`ctx.params.LENGTH`), `ctx.model_data`, `ctx.model_name`
- `ctx.result_dir`, `ctx.path(name)`, `ctx.files(".e")`
- `ctx.output_files(output, ".csv")` — the run's files of an output, one per sample with deviations
- `ctx.deviations_enabled`
- `ctx.crack_length(exodus_file, step)` — `(length, width, time)` of the crack at a step
- `ctx.figure()` — a new matplotlib figure and axes

Analyses go in `analysis.py` next to a YAML model, or anywhere in a Python model's file.

## Converting a legacy model

Models written for the old contract (`class Valves(BaseModel)` + `class main` with
`get_discretization` / `create_geometry` / `crate_block_definition`) are listed with
"legacy model format" and can't be used until converted:

| Old                                       | New                                                 |
| ----------------------------------------- | --------------------------------------------------- |
| `Valves` fields                           | `parameters:` (YAML) / `Param(...)` attributes      |
| `ANALYSIS_*` fields, `examples='outputs'` | parameters of `@analysis(...)`, `options="outputs"` |
| `valves["LENGTH"]`                        | `LENGTH` (YAML) / `self.LENGTH`                     |
| `get_discretization()`                    | `geometry.spacing` / `spacing` property             |
| `create_rectangle(...)`                   | `box` in `geometry.add`                             |
| `check_val_in_circle(..., False)` etc.    | a shape in `geometry.remove`                        |
| `create_rectangle` with `ybegin == -yend` | `grid_origin: [.., spacing / 2, ..]`                |
| `crate_block_definition` `np.where` chain | `blocks:` in the same order                         |
| `edit_model_data`                         | `set:` (YAML) / `edit_model_data`                   |
| `analysis(self, model_name, resultpath)`  | `@analysis` functions using `ctx`                   |
| docstring frontmatter                     | top-level keys (YAML) / class attributes            |

Old grids built with `np.arange(start, end + dx, dx)` could overshoot the specified size by one
row; the new grid stays inside the body.
