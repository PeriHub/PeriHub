# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

import json
import math
import os

import numpy as np
from exodusreader import exodusreader

from ..base_models import Material, Model
from ..file_handler import FileHandler
from ..globals import log


class Analysis:
    @staticmethod
    def calculate_calibration_factor_f(alpha):
        f = ((2 + alpha) / math.pow((1 - alpha), 3 / 2)) * (
            0.886
            + (4.64 * alpha)
            - (13.32 * math.pow(alpha, 2))
            + (14.72 * math.pow(alpha, 3))
            - (5.6 * math.pow(alpha, 4))
        )

        return f

    @staticmethod
    def calculate_calibration_factor_phi(alpha):
        A = (
            1.9118
            + (19.118 * alpha)
            - (2.5122 * math.pow(alpha, 2))
            - (23.226 * math.pow(alpha, 3))
            + (20.54 * math.pow(alpha, 4))
        )
        B = (
            19.118
            - (5.0244 * alpha)
            - (69.678 * math.pow(alpha, 2))
            + (82.16 * math.pow(alpha, 3))
        ) * (1 - alpha)

        phi = (A * (1 - alpha)) / (B + (2 * A))

        return phi

    @staticmethod
    def calculate_k1(P, B, W, f):
        k1 = f * (P / (B * math.sqrt(W)))
        return k1

    @staticmethod
    def calculate_g1(Energy, B, W, phi):
        g1 = Energy / (B * W * phi)
        return g1

    @staticmethod
    def get_global_data(file, variable, axis, absolute):
        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read(file)

        if variable == "Time":
            data = time
        else:
            if absolute:
                if axis == "X":
                    data = [item[0] for item in abs(global_data[variable])]
                elif axis == "Y":
                    data = [item[1] for item in abs(global_data[variable])]
                elif axis == "Z":
                    data = [item[2] for item in abs(global_data[variable])]
                elif axis == "Magnitude":
                    data = [item[0] for item in abs(global_data[variable])]
            else:
                if axis == "X":
                    data = [item[0] for item in global_data[variable]]
                elif axis == "Y":
                    data = [item[1] for item in global_data[variable]]
                elif axis == "Z":
                    data = [item[2] for item in global_data[variable]]
                elif axis == "Magnitude":
                    data = [item[0] for item in global_data[variable]]
        return data

    @staticmethod
    def get_result_file(username, model_name, output):
        resultpath = FileHandler.get_local_model_path(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, 0)

        first_time = time.data.item()
        first_displ = global_data["External_Displacement"][0]
        first_force = global_data["External_Force"][0]
        damage_blocks = cell_data["Damage"][0]

        first_damage_id = []
        for block_id, _ in enumerate(block_data):
            if block_id in damage_blocks:
                if np.max(damage_blocks[block_id]) > 0:
                    first_damage_id.append(block_id)

                    block_ids = block_data[block_id][:, 0]
                    block_points = points[block_ids]
                    filter = damage_blocks[block_id] > 0.0
                    current_points = (
                        block_points + point_data["Displacement"][block_ids]
                    )

                    filtered_points = current_points[filter]

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, -1)

        last_time = time.data.item()
        last_displ = global_data["External_Displacement"][0]
        last_force = global_data["External_Force"][0]
        damage_blocks = cell_data["Damage"][0]

        last_damage_id = []
        for block_id, _ in enumerate(block_data):
            if block_id in damage_blocks:
                if np.max(damage_blocks[block_id]) > 0:
                    last_damage_id.append(block_id)

        result_dict = {
            "first_damage": {
                "time": first_time,
                "block_id": first_damage_id,
                "displacement": {
                    "x": first_displ[0],
                    "y": first_displ[1],
                    "z": first_displ[2],
                },
                "force": {
                    "x": first_force[0],
                    "y": first_force[1],
                    "z": first_force[2],
                },
                "points": {
                    "x": filtered_points[0][0],
                    "y": filtered_points[0][1],
                    "z": filtered_points[0][2],
                },
            },
            "last_ply_failure": {
                "time": last_time,
                "block_id": last_damage_id,
                "displacement": {
                    "x": last_displ[0],
                    "y": last_displ[1],
                    "z": last_displ[2],
                },
                "force": {
                    "x": last_force[0],
                    "y": last_force[1],
                    "z": last_force[2],
                },
            },
        }

        json_path = os.path.join(resultpath, model_name + "_" + output + ".json")

        with open(json_path, "w") as file:
            json.dump(result_dict, file)

        return json_path
