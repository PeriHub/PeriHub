# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import os
import time

import numpy as np

from ...support.file_handler import FileHandler
from ...support.globals import log
from ...support.writer.yaml_writer_perilab import YAMLcreatorPeriLab

# from numba import jit


class ModelWriter:
    """doc"""

    def __init__(self, model_data, filename, model_folder_name, username):
        """doc"""

        self.filename = filename
        self.model_folder_name = model_folder_name
        self.ns_name = "ns_" + filename
        self.path = FileHandler.get_local_model_folder_path(username, filename, model_folder_name)
        self.mesh_file = model_data.model.mesh_file
        self.bc_dict = model_data.boundaryConditions
        self.solver_dict = model_data.solvers
        self.job_dict = model_data.job
        self.model_data = model_data
        self.disc_type = "txt"

        node_set_ids = []
        for bcs in self.bc_dict.conditions:
            if bcs.blockId not in node_set_ids:
                node_set_ids.append(bcs.blockId)
        self.node_set_ids = node_set_ids
        log.info(f"Node Sets: {node_set_ids}")

    def write_node_sets(self, model):
        """doc"""
        number_of_ns = 0
        for idx, k in enumerate(self.node_set_ids):
            points = np.where(model[:, 3] == k)
            string = "header: global_id\n"
            for point in points[0]:
                string += str(int(point) + 1) + "\n"
            self.file_writer(self.ns_name + "_" + str(idx + 1) + ".txt", string)
            number_of_ns += 1
            # print(self.ns_list)
            # for idx, points in enumerate(self.ns_list):
            #     string = "header: global_id\n"
            #     for point in points:
            #         string += str(int(point) + 1) + "\n"
            # self.file_writer(self.ns_name + "_" + str(idx + 1 + number_of_ns) + ".txt", string)

    def file_writer(self, filename, string):
        """doc"""
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(self.path + "/" + filename, "w", encoding="UTF-8") as file:
            file.write(string)

    def mesh_file_writer(self, filename, string, mesh_array, mesh_format):
        """doc"""
        log.info("Write mesh file")
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        with open(self.path + "/" + filename, "w", encoding="UTF-8") as file:
            file.write(string)
            np.savetxt(file, mesh_array, fmt=mesh_format, delimiter=" ")

    def write_mesh(self, model, twoD=False):
        """doc"""
        start_time = time.time()
        values = "%.18e %.18e %.18e %d %.18e"
        if twoD:
            string = "header: x y block_id volume\n"
            # remove z entry from model
            model = np.delete(model, 2, axis=1)
            values = "%.18e %.18e %d %.18e"
        else:
            string = "header: x y z block_id volume\n"
        self.mesh_file_writer(
            self.filename + ".txt",
            string,
            model,
            values,
        )
        log.info("Mesh written in %.2f seconds", time.time() - start_time)

    def write_mesh_with_angles(self, model, twoD=False):
        """doc"""
        start_time = time.time()
        values = "%.18e %.18e %.18e %d %.18e %.18e %.18e %.18e"
        if twoD:
            string = "header: x y block_id volume Angles\n"
            # remove z entry from model
            model = np.delete(model, [2, 6, 7], axis=1)
            values = "%.18e %.18e %d %.18e %.18e"
        else:
            string = "header: x y z block_id volume Angles_x Angles_y Angles_z\n"
        self.mesh_file_writer(
            self.filename + ".txt",
            string,
            model,
            values,
        )
        log.info("Mesh written in %.2f seconds", time.time() - start_time)

    def create_file(self, block_def, max_block_id):
        """doc"""
        string = ""
        yaml_perilab = YAMLcreatorPeriLab(self, block_def=block_def)
        string = yaml_perilab.create_yaml(max_block_id)

        self.file_writer(self.filename + ".yaml", string)
