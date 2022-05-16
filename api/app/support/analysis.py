import os
import math
from support.base_models import ModelData
from support.exodus_reader import ExodusReader


class Analysis:
    @staticmethod
    def get_g2c(username, model_name, output, model_data: ModelData):

        w = model_data.model.width
        a = model_data.model.cracklength - model_data.model.length / 22
        L = model_data.model.length / 2.2

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        points, point_data, global_data, cell_data, ns, block_data = ExodusReader.read(
            file, -1
        )

        P = global_data["Crosshead_Force"][1]
        d = global_data["Crosshead_Displacement"][0]

        GIIC = (9 * P * math.pow(a, 2) * d * 1000) / (
            2 * w * (1 / 4 * math.pow(L, 3) + 3 * math.pow(a, 3))
        )

        return GIIC

    @staticmethod
    def get_k1c(username, model_name, output, model_data: ModelData):

        w = model_data.model.length
        a = model_data.model.cracklength - model_data.model.length / 22
        L = model_data.model.length / 2.2

        resultpath = "./Results/" + os.path.join(username, model_name)
        file = os.path.join(resultpath, model_name + "_" + output + ".e")

        points, point_data, global_data, cell_data, ns, block_data = ExodusReader.read(
            file, -1
        )

        P = global_data["Crosshead_Force"][1]
        d = global_data["Crosshead_Displacement"][0]

        GIIC = (9 * P * math.pow(a, 2) * d * 1000) / (
            2 * w * (1 / 4 * math.pow(L, 3) + 3 * math.pow(a, 3))
        )

        return GIIC
