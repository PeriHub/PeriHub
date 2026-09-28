# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""A PeriHub model in Python — reference: docs/OwnModels.md."""

from perihub import Param, PeriHubModel, analysis, box, cylinder


class Model(PeriHubModel):
    title = "{title}"
    description = "{description}"
    author = "{author}"
    version = "0.1.0"
    requirements = []  # extra pip packages, installed at startup

    DISCRETIZATION = Param(21, "Points over the height")
    LENGTH = Param(20.0, "Length (mm)")
    HEIGHT = Param(10.0, "Height (mm)")
    WIDTH = Param(5.0, "Width (mm)", "Thickness in 3D; ignored in 2D")

    @property
    def spacing(self):
        return self.HEIGHT / self.DISCRETIZATION

    def geometry(self):
        body = box([0, 0, -self.WIDTH / 2], [self.LENGTH, self.HEIGHT, self.WIDTH / 2])
        hole = cylinder(
            [self.LENGTH / 2, self.HEIGHT / 2, -self.WIDTH], [self.LENGTH / 2, self.HEIGHT / 2, self.WIDTH], 2
        )
        return body - hole

    def blocks(self, x, y, z):
        # Everything else is block 1; later entries win.
        return {
            2: x < 3 * self.spacing,
            3: x > self.LENGTH - 3 * self.spacing,
        }


@analysis("Displacement over time", OUTPUT=Param("CSV", "Output", options="outputs"))
def displacement(ctx):
    df = ctx.csv(ctx.OUTPUT)
    fig, ax = ctx.figure()
    column = next(c for c in df.columns if c != "Time")
    ax.plot(df["Time"], df[column])
    ax.set_xlabel("Time")
    ax.set_ylabel(column)
    return fig
