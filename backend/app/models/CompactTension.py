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

from ..support.model.geometry import Geometry


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
    TWOD: bool = Field(
        default=True,
        title="Two Dimensional",
        description="Two Dimensional",
    )
    NOTCH_ENABLED: bool = Field(
        default=True,
        title="Notch enabled",
        description="Notch enabled",
    )


class main:
    def __init__(
        self,
        valves,
    ):
        self.xbegin = 0.0
        self.ybegin = -0.6 * valves["LENGTH"]
        self.xend = 1.25 * valves["LENGTH"]
        self.yend = 0.6 * valves["LENGTH"]

        if valves["TWOD"]:
            self.zbegin = 0
            self.zend = 0
        else:
            self.zbegin = -valves["WIDTH"] / 2
            self.zend = valves["WIDTH"] / 2

    def get_discretization(self, valves):
        number_nodes = 2 * int(valves["DISCRETIZATION"] / 2) + 1
        dx_value = [
            1.25 * valves["LENGTH"] / number_nodes,
            1.25 * valves["LENGTH"] / number_nodes,
            1.25 * valves["LENGTH"] / number_nodes,
        ]
        self.dx_value = dx_value
        return dx_value

    def create_geometry(self, valves):
        """doc"""

        geo = Geometry()

        x_value, y_value, z_value = geo.create_rectangle(
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

        if valves["NOTCH_ENABLED"]:
            x_value, y_value, z_value = geo.check_val_in_notch(
                x_value,
                y_value,
                z_value,
                0.0,
                self.xend,
                0.45 * valves["LENGTH"],
                1.6,
                self.dx_value[0],
                60,
            )

        return (
            x_value,
            y_value,
            z_value,
        )

    def crate_block_definition(self, valves, x_value, y_value, z_value, k):
        """doc"""

        k = np.where(
            np.logical_and(
                np.logical_and(
                    x_value <= 0.45 * valves["LENGTH"],
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
                    x_value <= 0.45 * valves["LENGTH"],
                    x_value >= 0,
                ),
                y_value <= 0,
            ),
            5,
            k,
        )
        condition = np.where(
            ((x_value - 0.25 * valves["LENGTH"]) ** 2) + ((y_value - 0.275 * valves["LENGTH"]) ** 2)
            <= (0.125 * valves["LENGTH"]) ** 2,
            1.0,
            0,
        )
        k = np.where(
            condition,
            2,
            k,
        )
        # Center of the circle
        center_x = 0.25 * valves["LENGTH"]
        center_y = 0.275 * valves["LENGTH"]

        # Calculate distances of all points from the center
        distances = np.sqrt((x_value - center_x) ** 2 + (y_value - center_y) ** 2)

        # Find the index of the point closest to the center
        closest_index = np.argmin(distances)

        condition = np.where(
            ((x_value - 0.25 * valves["LENGTH"]) ** 2) + ((y_value + 0.275 * valves["LENGTH"]) ** 2)
            <= (0.125 * valves["LENGTH"]) ** 2,
            1.0,
            0,
        )
        k = np.where(
            condition,
            3,
            k,
        )
        return k
