# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
title: ENFmodel
description: Carbon fibre reinforced plastics - Test method - Determination of interlaminar fracture toughness energy - Mode II - GIIC
author: hess_ja
requirements:
version: 0.1.0
"""
import numpy as np
from pydantic import BaseModel, Field

from ...support.model.geometry import Geometry


class Valves(BaseModel):
    DISCRETIZATION: float = Field(
        default=21,
        title="Discretization",
        description="Discretization",
    )
    LENGTH: float = Field(
        default=13,
        title="Length",
        description="Length",
    )
    HEIGHT: float = Field(
        default=2,
        title="Height",
        description="Height",
    )
    WIDTH: float = Field(
        default=10,
        title="Width",
        description="Width",
    )


class main:
    def __init__(self, valves, model_data):
        self.xbegin = 0
        self.xend = valves["LENGTH"]
        self.ybegin = 0
        self.yend = valves["HEIGHT"]
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

        return (
            x_value,
            y_value,
            z_value,
        )

    def crate_block_definition(self, x_value, y_value, z_value, k):
        """doc"""
        k = np.where(
            y_value <= self.yend / 2,
            2,
            k,
        )
        k = np.where(
            np.logical_and(
                (self.xend / 2) - (4 * self.dx_value[0]) <= x_value,
                np.logical_and(
                    x_value <= (self.xend / 2) + (4 * self.dx_value[0]),
                    self.yend - (4 * self.dx_value[0]) <= y_value,
                ),
            ),
            3,
            k,
        )
        k = np.where(
            np.logical_and(
                (self.xend / 2) - (self.dx_value[0]) <= x_value,
                np.logical_and(
                    x_value <= (self.xend / 2) + (self.dx_value[0]),
                    self.yend - (self.dx_value[0]) <= y_value,
                ),
            ),
            4,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value <= 4 * self.dx_value[0],
                y_value <= 4 * self.dx_value[0],
            ),
            5,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value < self.dx_value[0],
                y_value < self.dx_value[0],
            ),
            6,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value >= self.xend - (4 * self.dx_value[0]),
                y_value <= 4 * self.dx_value[0],
            ),
            7,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value > self.xend - (self.dx_value[0]),
                y_value < self.dx_value[0],
            ),
            8,
            k,
        )
        return k
