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


class main:
    def __init__(self, valves, model_data):
        self.xbegin = 0.0
        self.ybegin = -0.6 * valves["LENGTH"]
        self.xend = 1.25 * valves["LENGTH"]
        self.yend = 0.6 * valves["LENGTH"]
        self.length = valves["LENGTH"]
        self.discretization = valves["DISCRETIZATION"]
        self.notch_enabled = valves["NOTCH_ENABLED"]
        self.two_d = model_data.model.twoDimensional
        self.x_crack_end = model_data.bondFilters[0].lowerLeftCornerX + model_data.bondFilters[0].bottomLength - 1.0

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

        self.dx_value = dx_value
        return dx_value

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

        # Center of the circle
        center_x = 0.25 * self.length
        center_y = 0.275 * self.length

        # Calculate distances of all points from the center
        distances = np.sqrt((x_value - center_x) ** 2 + (y_value - center_y) ** 2)

        # Find the index of the point closest to the center
        closest_index = np.argmin(distances)
        print(closest_index)

        # Center of the circle
        center_x = 0.25 * self.length
        center_y = -0.275 * self.length

        # Calculate distances of all points from the center
        distances = np.sqrt((x_value - center_x) ** 2 + (y_value - center_y) ** 2)

        # Find the index of the point closest to the center
        closest_index = np.argmin(distances)
        print(closest_index)

        return k
