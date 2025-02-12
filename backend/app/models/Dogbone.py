# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
title: Dogbone
description: Tensile dogbone
author: hess_ja
requirements:
version: 0.1.0
"""
import numpy as np
from pydantic import BaseModel, Field

from ..support.model.geometry import Geometry


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
    HEIGHT1: float = Field(
        default=1,
        title="Inner Height",
        description="Inner Height",
    )
    HEIGHT2: float = Field(
        default=2,
        title="Outer Height",
        description="Outer Height",
    )
    WIDTH: float = Field(
        default=0.1,
        title="Width",
        description="Width",
    )
    STRUCTURED: bool = Field(
        default=True,
        title="Structured",
        description="Structured",
    )
    TWOD: bool = Field(
        default=True,
        title="Two Dimensional",
        description="Two Dimensional",
    )


class main:
    def __init__(
        self,
        valves,
    ):
        self.xend = valves["LENGTH"]
        self.height1 = valves["HEIGHT1"]
        self.height2 = valves["HEIGHT2"]

        if valves["TWOD"]:
            self.zend = 1
        else:
            self.zend = valves["WIDTH"]

        self.radius = 7.6
        self.length2 = 5.7
        self.delta_height = (self.height2 - self.height1) / 2
        self.delta_length = np.sqrt(self.radius * self.radius - (self.radius - self.delta_height) ** 2)
        self.length1 = (self.xend - 2 * self.delta_length - self.length2) / 2
        self.alpha = np.arccos((self.radius - self.delta_height) / self.radius) * 180 / np.pi

    def get_discretization(self, valves):
        number_nodes = 2 * int(valves["DISCRETIZATION"] / 2)
        dx_value = [
            valves["HEIGHT2"] / number_nodes,
            valves["HEIGHT2"] / number_nodes,
            valves["HEIGHT2"] / number_nodes,
        ]
        self.dx_value = dx_value
        return dx_value

    def create_geometry(self, valves):
        """doc"""

        geo = Geometry()

        x_value_0 = np.arange(0, self.xend, self.dx_value[0])
        y_value_0 = np.arange(
            -self.height2 / 2 - self.dx_value[1],
            self.height2 / 2 + self.dx_value[1],
            self.dx_value[1],
        )
        z_value_0 = np.arange(0, self.zend, self.dx_value[2])

        if valves["STRUCTURED"]:
            number_nodes = 2 * int((self.height2 / self.dx_value[1]) / 2) + 1
            num_rows = int((number_nodes - 1) / 2)
            fh2 = (2 * self.dx_value[1] * (num_rows) + self.height1 - self.height2) / (self.dx_value[1] * (num_rows))
            x_value = np.array([])
            y_value = np.array([])
            z_value = np.array([])
            for zval in z_value_0:
                for i in range(0, num_rows):
                    height1 = self.height1 - self.dx_value[1] * i * fh2
                    height2 = self.height2 - self.dx_value[1] * i * 2
                    # R1 = radius+0.03*i
                    dh1 = (height2 - height1) / 2

                    alpha1 = np.arccos((self.radius - dh1) / self.radius) * 180 / np.pi

                    (
                        top_surf,
                        bottom_surf,
                    ) = geo.create_boundary_curve(
                        height=height2 / 2,
                        length1=self.length1,
                        radius=self.radius,
                        length2=self.length2,
                        alpha_max=self.alpha,
                        alpha_max1=alpha1,
                        delta_length=self.delta_length,
                        delta_height=dh1,
                    )
                    upper_y_value = top_surf(x_value_0)
                    lower_y_value = bottom_surf(x_value_0)
                    x_value = np.concatenate((x_value, x_value_0))
                    x_value = np.concatenate((x_value, x_value_0))
                    y_value = np.concatenate((y_value, upper_y_value))
                    y_value = np.concatenate((y_value, lower_y_value))
                    z_value = np.concatenate((z_value, np.full_like(x_value_0, zval)))
                    z_value = np.concatenate((z_value, np.full_like(x_value_0, zval)))

                x_value = np.concatenate((x_value, x_value_0))
                y_value = np.concatenate((y_value, np.zeros_like(x_value_0)))
                z_value = np.concatenate((z_value, np.full_like(x_value_0, zval)))

        else:
            top_surf, bottom_surf = geo.create_boundary_curve_old(
                height=self.height2 / 2,
                length1=self.length1,
                radius=self.radius,
                length2=self.length2,
                alpha_max=self.alpha,
                delta_length=self.delta_length,
                delta_height=self.delta_height,
            )

            x_value = []
            y_value = []
            z_value = []
            for xval in x_value_0:
                for yval in y_value_0:
                    for zval in z_value_0:
                        if geo.check_val_greater(yval, bottom_surf(xval)) and geo.check_val_lower(yval, top_surf(xval)):
                            x_value.append(xval)
                            y_value.append(yval)
                            z_value.append(zval)

        return (
            x_value,
            y_value,
            z_value,
        )

    def crate_block_definition(self, valves, x_value, y_value, z_value, k):
        """doc"""

        boundary_condition = 0.2

        k = np.where(
            x_value >= boundary_condition,
            2,
            k,
        )
        k = np.where(
            x_value >= valves["LENGTH"],
            3,
            k,
        )
        k = np.where(
            x_value >= valves["LENGTH"] + 2 * self.delta_length + self.length2,
            4,
            k,
        )
        k = np.where(
            x_value >= self.xend - boundary_condition,
            5,
            k,
        )
        return k
