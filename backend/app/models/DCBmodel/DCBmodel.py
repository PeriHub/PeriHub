# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
title: DCB Model
description: DCB Model
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
        default=50,
        title="Length",
        description="Length",
    )
    HEIGHT: float = Field(
        default=20,
        title="Height",
        description="Height",
    )
    WIDTH: float = Field(
        default=6,
        title="Width",
        description="Width",
    )


class main:
    def __init__(self, valves, model_data):
        self.xbegin = 0.0
        self.ybegin = -valves["HEIGHT"] / 2
        self.xend = valves["LENGTH"]
        self.yend = valves["HEIGHT"] / 2
        self.length = valves["LENGTH"]
        self.discretization = valves["DISCRETIZATION"]
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
            self.length / number_nodes,
            self.length / number_nodes,
            self.length / number_nodes,
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
            y_value > 0,
            2,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value < 2.0,
                y_value > 0,
            ),
            3,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value < 2.0,
                y_value < 0,
            ),
            4,
            k,
        )
        return k
