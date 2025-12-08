# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
title: Compact Tension
description: Carbon fibre reinforced plastics - Test method - Determination of interlaminar fracture toughness energy - Mode I - GIC
author: hess_ja
requirements:
analysis: Get Energy Release Plot
version: 0.1.0
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field

from ...support.model.geometry import Geometry
from ...support.results.crack_analysis import CrackAnalysis


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
    ANALYSIS_STEP: int = Field(
        default= 1, 
        title='Step',
        description='Step',
    )
    ANALYSIS_EXODUS_OUTPUT: str = Field(
        default= "Exodus", 
        title='Exodus Ouptu',
        description='Exodus Ouptu',
        examples='outputs',
    )
    ANALYSIS_CSV_OUTPUT: str = Field(
        default= "CSV", 
        title='CSV Output',
        description='CSV Output',
        examples='outputs',
    )
    ANALYSIS_LOAD_VARIABLE: str = Field(
        default= "External_Forces", 
        title='Load Variable',
        description='Load Variable',
        examples='computes',
    )
    ANALYSIS_DISPL_VARIABLE: str = Field(
        default= "External_Displacements", 
        title='Displacement Variable',
        description='Displacement Variable',
        examples='computes',
    )


class main:
    def __init__(self, valves, model_data, analysisValves = {}):
        self.xbegin = 0.0
        self.ybegin = -0.6 * valves["LENGTH"]
        self.xend = 1.25 * valves["LENGTH"]
        self.yend = 0.6 * valves["LENGTH"]
        self.length = valves["LENGTH"]
        self.discretization = valves["DISCRETIZATION"]
        self.notch_enabled = valves["NOTCH_ENABLED"]
        self.two_d = model_data.model.twoDimensional
        self.x_crack_end = model_data.bondFilters[0].lowerLeftCornerX + model_data.bondFilters[0].bottomLength - 1.0
        self.thickness = model_data.damages[0].thickness

        if self.two_d:
            self.zbegin = 0
            self.zend = 0
        else:
            self.zbegin = -valves["WIDTH"] / 2
            self.zend = valves["WIDTH"] / 2

        if analysisValves:
            self.step = analysisValves["ANALYSIS_STEP"]
            self.exodus_output = analysisValves["ANALYSIS_EXODUS_OUTPUT"]
            self.csv_output = analysisValves["ANALYSIS_CSV_OUTPUT"]
            self.load_variable = analysisValves["ANALYSIS_LOAD_VARIABLE"]
            self.displ_variable = analysisValves["ANALYSIS_DISPL_VARIABLE"]

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

    def analysis(self,model_name,resultpath):
        step = int(self.step)
        load_variable = self.load_variable + "y"
        displ_variable = self.displ_variable + "y"
        csv_output = self.csv_output
        exodus_output = self.exodus_output

        file = os.path.join(resultpath, model_name + "_" + csv_output + ".csv")
        result_file = os.path.join(resultpath, model_name + "_results.png")

        if not os.path.exists(file):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=model_name + "_" + csv_output + ".csv can not be found"
            )

        df = pd.read_csv(file)

        file = os.path.join(resultpath, model_name + "_" + exodus_output + ".e")
        print(file)
        print(step)
        (crack_length, crack_width, time) = CrackAnalysis.get_crack_length(file, step)

        x = df[displ_variable]
        y1 = df[load_variable]

        time_array = df["Time"]
        index = np.argmin(np.abs(time_array - time))
        y2 = np.linspace(0, y1[index], index)

        plt.clf()
        plt.plot(x, df[load_variable], label="Original data")

        x = x[:index]
        y1 = y1[:index]

        plt.plot(x, y2, "r", label="Linear equation (y=x+2)")
        plt.fill_between(x, y1, y2, alpha=0.3, label="Area between lines")

        z = np.array(y1 - y2)
        dx = x[2] - x[1]
        areas_pos = abs(z[:-1] + z[1:]) * 0.5 * dx
        dissipated_energy = np.sum(areas_pos)

        thickness_crack = self.thickness
        if self.thickness == None:
            thickness_crack = crack_width

        GIC = dissipated_energy / (thickness_crack * crack_length)

        # Add title and labels
        plt.title(f"Energy: {round(dissipated_energy,4)} | Crack: {round(crack_length,4)}mm | GIC: {round(GIC,4)}N/mm")
        plt.xlabel("Displacement [mm]")
        plt.ylabel("Force [N]")
        plt.legend()

        # Display the plot
        plt.savefig(result_file)

        return result_file