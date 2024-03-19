# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import os
import time

import numpy as np

from support.globals import log
from support.writer.yaml_writer_perilab import YAMLcreatorPeriLab

# from numba import jit


class ModelWriter:
    """doc"""

    def __init__(self, model_class):
        """doc"""

        self.filename = model_class.filename
        self.model_folder_name = model_class.model_folder_name
        self.ns_name = "ns_" + model_class.filename
        self.path = "simulations/" + os.path.join(
            model_class.username, model_class.filename, model_class.model_folder_name
        )
        self.mesh_file = model_class.model_data.model.mesh_file
        self.bc_dict = model_class.model_data.boundaryConditions
        self.solver_dict = model_class.model_data.solver
        self.job_dict = model_class.model_data.job
        self.model_data = model_class.model_data
        self.disc_type = model_class.disc_type
        if not os.path.exists("simulations"):
            os.mkdir("simulations")

        number_of_ns = 0
        node_set_ids = []
        for bcs in self.bc_dict.conditions:
            if bcs.blockId not in node_set_ids:
                number_of_ns += 1
                node_set_ids.append(bcs.blockId)
        self.ns_list = node_set_ids

    def write_node_sets(self, model):
        """doc"""
        for idx, k in enumerate(self.ns_list):
            if k == 0:
                points = np.where(model[:, 3] >= 0)
            else:
                points = np.where(model[:, 3] == k)
            string = "header: global_id\n"
            for point in points[0]:
                string += str(int(point) + 1) + "\n"
            if k == 0:
                self.file_writer(self.ns_name + "_all.txt", string)
            else:
                self.file_writer(self.ns_name + "_" + str(idx + 1) + ".txt", string)

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

    def create_file(self, block_def):
        """doc"""
        string = ""
        yaml_perilab = YAMLcreatorPeriLab(self, block_def=block_def)
        string = yaml_perilab.create_yaml()

        self.file_writer(self.filename + ".yaml", string)
