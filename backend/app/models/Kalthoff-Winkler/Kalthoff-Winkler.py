# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
title: Kalthoff-Winkler
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
        default=200,
        title="Height",
        description="Height",
    )
    WIDTH: float = Field(
        default=9,
        title="Width",
        description="Width",
    )


class main:
    def __init__(self, valves, model_data):
        self.xbegin = 0
        self.xend = valves["LENGTH"]
        self.ybegin = -valves["HEIGHT"] / 2
        self.yend = valves["HEIGHT"] / 2
        self.discretization = valves["DISCRETIZATION"]

        if model_data.model.twoDimensional:
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
        x_values, y_values, z_values = geo.check_val_in_rectangle(
            x_values,
            y_values,
            z_values,
            50 / 2,
            25,
            1.5,
            50,
            False,
        )
        x_values, y_values, z_values = geo.check_val_in_rectangle(
            x_values,
            y_values,
            z_values,
            50 / 2,
            -25,
            1.5,
            50,
            False,
        )

        return (x_values, y_values, z_values, None)

    def crate_block_definition(self, x_values, y_values, z_values, k):
        """doc"""
        k = np.where(
            np.logical_and(
                x_values < self.dx_value[0] * 5,
                np.logical_and(y_values <= 25, y_values >= -25),
            ),
            2,
            k,
        )
        k = np.where(x_values >= self.xend - self.dx_value[0] * 3, 3, k)
        return k

    def edit_model_data(self, model_data):
        lowerLeftCornerY = int(25 / self.dx_value[0]) * self.dx_value[0] + self.dx_value[0] / 2
        model_data.bondFilters[0].lowerLeftCornerY = lowerLeftCornerY
        model_data.bondFilters[1].lowerLeftCornerY = -lowerLeftCornerY
        return model_data
