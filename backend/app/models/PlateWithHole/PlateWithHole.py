# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
title: Plate with Hole
description: Crack propagation
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
        default=100,
        title="Length",
        description="Length",
    )
    HEIGHT: float = Field(
        default=100,
        title="Height",
        description="Height",
    )
    WIDTH: float = Field(
        default=10,
        title="Width",
        description="Width",
    )
    RADIUS: float = Field(
        default=10,
        title="Radius",
        description="Radius",
    )


class main:
    def __init__(self, valves, twoDimensional):
        self.xbegin = -valves["LENGTH"] / 2
        self.xend = valves["LENGTH"] / 2
        self.ybegin = -valves["HEIGHT"] / 2
        self.yend = valves["HEIGHT"] / 2
        self.discretization = valves["DISCRETIZATION"]
        self.radius = valves["RADIUS"]

        if twoDimensional:
            self.zbegin = 0
            self.zend = 0
        else:
            self.zbegin = -valves["WIDTH"] / 2
            self.zend = valves["WIDTH"] / 2

    def get_discretization(self):
        number_nodes = 2 * int(self.discretization / 2) + 1
        dx_value = [
            self.yend / number_nodes,
            self.yend / number_nodes,
            self.yend / number_nodes,
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

        x_values, y_values, z_values = geo.check_val_in_circle(
            x_values,
            y_values,
            z_values,
            0,
            0,
            self.radius,
            False,
        )

        return (
            x_values,
            y_values,
            z_values,
        )

    def crate_block_definition(self, x_values, y_values, z_values, k):
        """doc"""
        k = np.where(
            y_values < self.ybegin + self.dx_value[1] * 3,
            2,
            k,
        )
        k = np.where(
            y_values > self.yend - self.dx_value[1] * 3,
            3,
            k,
        )
        return k
