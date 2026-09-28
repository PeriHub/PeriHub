# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""Tensile dogbone. The "structured" point layout follows the curved flanks row by row, which
no grid of shapes can express — so this model overrides points() instead of geometry()."""

import numpy as np
from perihub import Param, PeriHubModel
from scipy.interpolate import interp1d

RADIUS = 7.6  # flank radius
LENGTH2 = 5.7  # length of the narrow middle section


def boundary_curve(height, length1, radius, length2, alpha_max, alpha_max1, delta_length, delta_height):
    """Upper/lower outline y(x) of the dogbone: flat grip, flank arc, narrow middle, flank arc, grip."""
    dalpha = 0.025
    alpha = np.arange(0, alpha_max, dalpha)
    if alpha_max1 == 0:
        alpha1 = np.zeros_like(alpha)
    elif alpha_max == alpha_max1:
        alpha1 = np.arange(0, alpha_max, dalpha)
    else:
        dalpha1 = alpha_max1 / len(alpha)
        alpha1 = np.arange(0, alpha_max1, dalpha1)
        if len(alpha1) > len(alpha):
            alpha1 = np.arange(0, alpha_max1 - dalpha1 / 2, dalpha1)

    x_value = np.concatenate(
        (
            [0],
            length1 + delta_length + radius * np.sin(-alpha / 180 * np.pi),
            length1 + delta_length + length2 + radius * np.sin(alpha / 180 * np.pi),
            [2 * delta_length + 2 * length1 + length2 + 0.01],
        )
    )
    y_value = np.concatenate(
        (
            [height],
            height - delta_height + radius - radius * np.cos(-alpha1 / 180 * np.pi),
            height - delta_height + radius - radius * np.cos(alpha1 / 180 * np.pi),
            [height],
        )
    )
    return interp1d(x_value, y_value), interp1d(x_value, -y_value)


def unstructured_boundary_curve(height, length1, radius, length2, alpha_max, delta_length, delta_height):
    """The outline used for the unstructured grid (arcs include their end angle)."""
    alpha = np.arange(0, alpha_max + 0.025, 0.025)
    x_value = np.concatenate(
        (
            [0],
            length1 + delta_length + radius * np.sin(-alpha / 180 * np.pi),
            length1 + delta_length + length2 + radius * np.sin(alpha / 180 * np.pi),
            [2 * delta_length + 2 * length1 + length2 + 0.01],
        )
    )
    y_value = np.concatenate(
        (
            [height],
            height + radius - delta_height - radius * np.cos(-alpha / 180 * np.pi),
            height - delta_height + radius - radius * np.cos(alpha / 180 * np.pi),
            [height],
        )
    )
    return interp1d(x_value, y_value), interp1d(x_value, -y_value)


class Model(PeriHubModel):
    title = "Dogbone"
    description = "Tensile dogbone"
    author = "hess_ja"
    version = "0.1.0"

    DISCRETIZATION = Param(21, "Discretization", "Points over the outer height")
    LENGTH = Param(13.0, "Length")
    HEIGHT1 = Param(1.0, "Inner Height")
    HEIGHT2 = Param(2.0, "Outer Height")
    WIDTH = Param(0.1, "Width")
    STRUCTURED = Param(True, "Structured", "Point rows follow the curved flanks")

    @property
    def spacing(self):
        return self.HEIGHT2 / (2 * int(self.DISCRETIZATION / 2))

    @property
    def _layout(self):
        delta_height = (self.HEIGHT2 - self.HEIGHT1) / 2
        delta_length = np.sqrt(RADIUS**2 - (RADIUS - delta_height) ** 2)
        length1 = (self.LENGTH - 2 * delta_length - LENGTH2) / 2
        alpha = np.arccos((RADIUS - delta_height) / RADIUS) * 180 / np.pi
        return delta_height, delta_length, length1, alpha

    def points(self):
        dx = self.spacing
        delta_height, delta_length, length1, alpha = self._layout
        x_row = np.arange(0, self.LENGTH, dx)
        z_layers = [0] if self.two_d else np.arange(0, self.WIDTH, dx)

        if not self.STRUCTURED:
            top, bottom = unstructured_boundary_curve(
                self.HEIGHT2 / 2, length1, RADIUS, LENGTH2, alpha, delta_length, delta_height
            )
            y_col = np.arange(-self.HEIGHT2 / 2 - dx, self.HEIGHT2 / 2 + dx, dx)
            gx, gy, gz = (g.ravel() for g in np.meshgrid(x_row, y_col, z_layers, indexing="ij"))
            keep = (gy >= bottom(gx)) & (gy <= top(gx))
            return gx[keep], gy[keep], gz[keep], None

        # Each row pair is a scaled copy of the outline, so rows bunch up in the narrow middle.
        num_rows = int((2 * int((self.HEIGHT2 / dx) / 2) + 1 - 1) / 2)
        fh2 = (2 * dx * num_rows + self.HEIGHT1 - self.HEIGHT2) / (dx * num_rows)
        xs, ys, zs = [], [], []
        for z in z_layers:
            for i in range(num_rows):
                height1 = self.HEIGHT1 - dx * i * fh2
                height2 = self.HEIGHT2 - dx * i * 2
                dh1 = (height2 - height1) / 2
                alpha1 = np.arccos((RADIUS - dh1) / RADIUS) * 180 / np.pi
                top, bottom = boundary_curve(height2 / 2, length1, RADIUS, LENGTH2, alpha, alpha1, delta_length, dh1)
                xs += [x_row, x_row]
                ys += [top(x_row), bottom(x_row)]
                zs += [np.full_like(x_row, z)] * 2
            xs.append(x_row)
            ys.append(np.zeros_like(x_row))
            zs.append(np.full_like(x_row, z))
        return np.concatenate(xs), np.concatenate(ys), np.concatenate(zs), None

    def blocks(self, x, y, z):
        _, delta_length, length1, _ = self._layout
        grip = 0.2  # clamped length at each end
        return {
            2: x >= grip,
            3: x >= length1,
            4: x >= length1 + 2 * delta_length + LENGTH2,
            5: x >= self.LENGTH - grip,
        }
