import os
import math
import json
import numpy as np
import matplotlib.pyplot as plt
from support.base_models import Model
from support.exodus_reader import ExodusReader

from support.globals import log


class Analysis:

    @staticmethod
    def get_global_data(file, variable, axis):

        global_data, time = ExodusReader.read(file)

        if variable == "Time":
            data = time
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
    def get_g1c(username, model_name, output, model: Model):

        w = model.width
        a = model.cracklength
        L = model.length / 2.2

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(
            file, -1
        )

        P_low = global_data["Lower_Load_Force"][1]
        P_up = global_data["Upper_Load_Force"][1]
        d_low = global_data["Lower_Load_Displacement"][1]
        d_up = global_data["Upper_Load_Displacement"][1]

        delta = d_up + abs(d_low)

        Delta = 1

        print(P_low)
        print(P_up)
        print(d_low)
        print(d_up)
        print(delta)
        print(w)
        print(a)

        GIC = (3 * P_up * delta) / (
            2 * w * (a + abs(Delta))
        )

        return GIC

    @staticmethod
    def get_g2c(username, model_name, output, model: Model):

        w = model.width
        a = model.cracklength - model.length / 22
        L = model.length / 2.2

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(
            file, -1
        )

        P = global_data["Crosshead_Force"][1]
        d = -global_data["Crosshead_Displacement"][1]

        GIIC = (9 * P * math.pow(a, 2) * d * 1000) / (
            2 * w * (1 / 4 * math.pow(L, 3) + 3 * math.pow(a, 3))
        )

        log.info(GIIC)

        return GIIC

    @staticmethod
    def get_result_file(username, model_name, output):

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(file, 0)

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
                    filter = (damage_blocks[block_id] > 0.0)
                    current_points = block_points + point_data["Displacement"][block_ids]

                    filtered_points = current_points[filter]

        points, point_data, global_data, cell_data, ns, block_data, time = ExodusReader.read_timestep(file, -1)

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
                    "z": first_displ[2]
                },
                "force": {
                    "x": first_force[0],
                    "y": first_force[1],
                    "z": first_force[2]
                },
                "points": {
                    "x": filtered_points[0][0],
                    "y": filtered_points[0][1],
                    "z": filtered_points[0][2]
                }
            },
            "last_ply_failure": {
                "time": last_time,
                "block_id": last_damage_id,
                "displacement": {
                    "x": last_displ[0],
                    "y": last_displ[1],
                    "z": last_displ[2]
                },
                "force": {
                    "x": last_force[0],
                    "y": last_force[1],
                    "z": last_force[2]
                }
            }
        }

        json_path = os.path.join(resultpath, model_name + "_" + output + ".json")

        with open(json_path, "w") as file:
	        json.dump(result_dict, file)

        return json_path