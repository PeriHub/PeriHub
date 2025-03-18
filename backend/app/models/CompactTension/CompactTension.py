# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
title: Compact Tension
description: Carbon fibre reinforced plastics - Test method - Determination of interlaminar fracture toughness energy - Mode I - GIC
author: hess_ja
requirements:
version: 0.1.0
"""
import numpy as np
from pydantic import BaseModel, Field

from ...support.model.geometry import Geometry
from ...support.model.rve import RVE


class Valves(BaseModel):
    DISCRETIZATION: float = Field(
        default=100,
        title="Discretization",
        description="Discretization",
    )
    LENGTH: float = Field(
        default=75,
        title="Length",
        description="Length",
    )
    WIDTH: float = Field(
        default=10,
        title="Width",
        description="Width",
    )
    NOTCH_ENABLED: bool = Field(
        default=True,
        title="Notch enabled",
        description="Notch enabled",
    )
    EMBEDDED_RVE: bool = Field(
        default=False,
        title="Embedded RVE",
        description="Embedded RVE",
    )
    DISC_FACTOR: float = Field(default=3.0, title="Disc factor", description="Disc factor", alias="EMBEDDED_RVE")
    FIBER_RADIUS: float = Field(default=2.0, title="Fiber radius", description="Fiber radius", alias="EMBEDDED_RVE")
    FIBER_CONTENT: float = Field(default=50.0, title="Fiber content", description="Fiber content", alias="EMBEDDED_RVE")
    RVE_DR: float = Field(
        default=0.1, title="RVE diameter ratio", description="RVE diameter ratio", alias="EMBEDDED_RVE"
    )
    RVE_LENGTH: float = Field(default=20.0, title="RVE length", description="RVE length", alias="EMBEDDED_RVE")


class main:
    def __init__(self, valves, model_data):
        self.xbegin = 0.0
        self.ybegin = -0.6 * valves["LENGTH"]
        self.xend = 1.25 * valves["LENGTH"]
        self.yend = 0.6 * valves["LENGTH"]
        self.length = valves["LENGTH"]
        self.discretization = valves["DISCRETIZATION"]
        self.notch_enabled = valves["NOTCH_ENABLED"]
        self.embedded_rve = valves["EMBEDDED_RVE"]
        self.two_d = model_data.model.twoDimensional
        self.x_crack_end = model_data.bondFilters[0].lowerLeftCornerX + model_data.bondFilters[0].bottomLength - 1.0
        self.fiber_radius = valves["FIBER_RADIUS"]
        self.fiber_content = valves["FIBER_CONTENT"]
        self.rve_dr = valves["RVE_DR"]
        self.rve_length = valves["RVE_LENGTH"]
        self.disc_factor = valves["DISC_FACTOR"]

        if self.two_d:
            self.zbegin = 0
            self.zend = 0
        else:
            self.zbegin = -valves["WIDTH"] / 2
            self.zend = valves["WIDTH"] / 2

    def get_discretization(self):
        number_nodes = 2 * int(self.discretization / 2) + 1
        dx_value = [
            1.25 * self.length / number_nodes,
            1.25 * self.length / number_nodes,
            1.25 * self.length / number_nodes,
        ]

        dx_fine = [i / self.disc_factor for i in dx_value]

        self.dx_value = dx_value
        self.dx_fine = dx_fine
        return [*[dx_value] * 5, *[dx_fine] * 2]

    def create_geometry(self):
        """doc"""

        geo = Geometry()

        x_values, y_values, z_values = geo.create_rectangle(
            coor=[
                self.xbegin,
                self.xend,
                self.ybegin,
                self.yend,
                self.zbegin,
                self.zend,
            ],
            dx_value=self.dx_value,
        )

        if self.notch_enabled:
            x_values, y_values, z_values = geo.check_val_in_notch(
                x_values,
                y_values,
                z_values,
                0.0,
                self.xend,
                0.45 * self.length,
                1.6,
                self.dx_value[0],
                60,
            )
        if self.two_d:
            volume = np.full_like(
                x_values,
                self.dx_value[0] * self.dx_value[1],
            )
        else:
            volume = np.full_like(
                x_values,
                self.dx_value[0] * self.dx_value[1] * self.dx_value[2],
            )
        if self.embedded_rve:
            disc_factor = 3
            dx_fine = [i / self.disc_factor for i in self.dx_value]
            x_values_extracted, y_values_extracted, z_values_extracted = geo.check_val_in_rectangle(
                x_values,
                y_values,
                z_values,
                self.x_crack_end + self.rve_length / 2,
                0.0,
                self.rve_length,
                self.rve_length,
                True,
            )
            x_values, y_values, z_values = geo.check_val_in_rectangle(
                x_values,
                y_values,
                z_values,
                self.x_crack_end + self.rve_length / 2,
                0.0,
                self.rve_length,
                self.rve_length,
                False,
            )

            if self.two_d:
                volume = np.full_like(
                    x_values,
                    self.dx_value[0] * self.dx_value[1],
                )
            else:
                volume = np.full_like(
                    x_values,
                    self.dx_value[0] * self.dx_value[1] * self.dx_value[2],
                )

            lower_left_point = [np.min(x_values_extracted), np.min(y_values_extracted)]
            upper_right_point = [np.max(x_values_extracted), np.max(y_values_extracted)]

            x_values_fine, y_values_fine, z_values_fine = geo.create_rectangle(
                coor=[
                    lower_left_point[0] - self.dx_value[0] / 2 + self.dx_fine[0] / 2,
                    upper_right_point[0] + self.dx_value[0] / 2 - self.dx_fine[0] * 1.5,
                    lower_left_point[1] - self.dx_value[1] / 2 + self.dx_fine[1] / 2,
                    upper_right_point[1] + self.dx_value[1] / 2 - self.dx_fine[1] * 1.5,
                    self.zbegin,
                    self.zend,
                ],
                dx_value=self.dx_fine,
            )
            x_values = np.append(x_values, x_values_fine)
            y_values = np.append(y_values, y_values_fine)
            z_values = np.append(z_values, z_values_fine)
            if self.two_d:
                volume = np.append(
                    volume,
                    np.full_like(
                        x_values_fine,
                        self.dx_fine[0] * self.dx_fine[1],
                    ),
                )
            else:
                volume = np.append(
                    volume,
                    np.full_like(
                        x_values_fine,
                        self.dx_fine[0] * self.dx_fine[1] * self.dx_fine[2],
                    ),
                )

        return (x_values, y_values, z_values, volume)

    def crate_block_definition(self, x_value, y_value, z_value, k):
        """doc"""

        k = np.where(
            np.logical_and(
                np.logical_and(
                    x_value <= 0.45 * self.length,
                    x_value >= 0,
                ),
                y_value >= 0,
            ),
            4,
            k,
        )
        k = np.where(
            np.logical_and(
                np.logical_and(
                    x_value <= 0.45 * self.length,
                    x_value >= 0,
                ),
                y_value <= 0,
            ),
            5,
            k,
        )
        condition = np.where(
            ((x_value - 0.25 * self.length) ** 2) + ((y_value - 0.275 * self.length) ** 2)
            <= (0.125 * self.length) ** 2,
            1.0,
            0,
        )
        k = np.where(
            condition,
            2,
            k,
        )
        # Center of the circle
        center_x = 0.25 * self.length
        center_y = 0.275 * self.length

        # Calculate distances of all points from the center
        distances = np.sqrt((x_value - center_x) ** 2 + (y_value - center_y) ** 2)

        # Find the index of the point closest to the center
        closest_index = np.argmin(distances)

        condition = np.where(
            ((x_value - 0.25 * self.length) ** 2) + ((y_value + 0.275 * self.length) ** 2)
            <= (0.125 * self.length) ** 2,
            1.0,
            0,
        )
        k = np.where(
            condition,
            3,
            k,
        )

        if self.embedded_rve:

            condition1 = np.where(
                np.logical_and(
                    np.logical_and(
                        x_value >= self.x_crack_end - self.dx_value[0] / 2,
                        x_value <= self.x_crack_end + self.rve_length + self.dx_value[0] / 2,
                    ),
                    np.logical_and(
                        y_value >= -self.rve_length / 2 - self.dx_value[1] / 2,
                        y_value <= self.rve_length / 2 + self.dx_value[1] / 2,
                    ),
                ),
                1.0,
                0,
            )
            k = np.where(
                condition1,
                6,
                k,
            )

            fibre_x, fibre_y = RVE.get_fibre_locations(
                self.fiber_radius, self.fiber_content, self.rve_dr, self.rve_length
            )

            for i, _ in enumerate(fibre_x):
                condition = np.where(
                    ((x_value - (self.x_crack_end + self.rve_length / 2 + fibre_x[i])) ** 2)
                    + ((y_value - fibre_y[i]) ** 2)
                    <= (self.fiber_radius) ** 2,
                    1.0,
                    0,
                )
                k = np.where(
                    np.logical_and(condition1, condition),
                    7,
                    k,
                )

        return k
