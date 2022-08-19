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
    def get_g1c(username, model_name, output, model: Model):

        w = model.width
        a = model.cracklength
        L = model.length / 2.2

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        points, point_data, global_data, cell_data, ns, block_data = ExodusReader.read(
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

        points, point_data, global_data, cell_data, ns, block_data = ExodusReader.read(
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

        points, point_data, global_data, cell_data, ns, block_data = ExodusReader.read(file, 0)

        first_displ = global_data["External_Displacement"][0]
        first_force = global_data["External_Force"][0]
        damage_blocks = cell_data["Damage"]

        first_damage_id = []
        for id, damage_block in enumerate(damage_blocks):
            if len(damage_block)!=0:
                if np.max(damage_block) > 0:
                    first_damage_id.append(id)

        points, point_data, global_data, cell_data, ns, block_data = ExodusReader.read(file, -1)

        last_displ = global_data["External_Displacement"][0]
        last_force = global_data["External_Force"][0]
        damage_blocks = cell_data["Damage"]

        last_damage_id = []
        for id, damage_block in enumerate(damage_blocks):
            if len(damage_block)!=0:
                if np.max(damage_block) > 0:
                    last_damage_id.append(id)

        result_dict = {
            # "wavelength": model.model.wavelength,
            # "amplitudeFactor": model.model.amplitudeFactor,
            "first_ply_failure": {
                "block_id": first_damage_id,
                "displacement": first_displ,
                "force": first_force
            },
            "last_ply_failure": {
                "block_id": last_damage_id,
                "displacement": last_displ,
                "force": last_force
            }
        }

        json_path = os.path.join(resultpath, model_name + "_" + output + ".json")

        with open(json_path, "w") as file:
	        json.dump(result_dict, file)

        return json_path