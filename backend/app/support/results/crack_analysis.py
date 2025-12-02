# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import math
import os

import numpy as np
import pandas as pd
from exodusreader import exodusreader
from matplotlib import pyplot as plt

from ..base_models import Model
from ..globals import log


class CrackAnalysis:

    @staticmethod
    def get_crack_end(file: str, step: int = -1):

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, step)

        points_y = np.array(points[:, 0])
        damage = point_data["Damage"]

        damaged_points_y = points_y[damage != 0]

        if len(damaged_points_y) == 0:
            log.warning("No damaged points found")
            return 1

        crack_coordinate = np.max(damaged_points_y)

        return crack_coordinate

    @staticmethod
    def get_crack_length(file: str, step: int = -1):

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, step)

        points_x = np.array(points[:, 0])
        points_y = np.array(points[:, 1])
        points_z = np.array(points[:, 2])
        damage = point_data["Damage"]

        damaged_points_x = points_x[damage != 0]
        damaged_points_y = points_y[damage != 0]
        damaged_points_z = points_z[damage != 0]

        if len(damaged_points_x) == 0:
            log.warning("No damaged points found")
            return 1, 1, time

        crack_length = np.sqrt(
            pow(np.max(damaged_points_x) - np.min(damaged_points_x), 2)
            + pow(np.max(damaged_points_y) - np.min(damaged_points_y), 2)
        )
        crack_width = np.max(damaged_points_z) - np.min(damaged_points_z)

        return crack_length, crack_width, time
