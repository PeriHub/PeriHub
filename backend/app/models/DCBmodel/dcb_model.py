# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import numpy as np

from support.base_models import Block
from support.model.geometry import Geometry
from support.writer.model_writer import ModelWriter


class DCBmodel:
    def __init__(
        self,
        model_data,
        filename="DCBmodel",
        model_folder_name="",
        username="",
        max_nodes=100000,
        ignore_mesh=False,
        dx_value=None,
    ):
        """
        definition der blocks
        k =
        1 basisplatte
        2 Z Zero Node Set
        3 Min Y Up Node Set
        4 Min Y Down Node Set
        """

        self.filename = filename
        self.model_folder_name = model_folder_name
        self.scal = 4.01
        self.disc_type = "txt"
        self.mesh_file = None
        self.two_d = model_data.model.twoDimensional
        self.ns_list = [3, 4]
        if not dx_value:
            dx_value = [0.001, 0.001, 0.001]
        self.dx_value = dx_value
        self.angle = model_data.model.angles
        self.xbegin = -0.005
        self.ybegin = -model_data.model.height
        self.xend = model_data.model.length + dx_value[0]
        self.yend = model_data.model.height + dx_value[1]
        self.rot = model_data.model.rotatedAngles
        self.block_def = model_data.blocks
        self.username = username
        self.max_nodes = max_nodes
        self.ignore_mesh = ignore_mesh
        self.software = model_data.job.software
        if self.two_d:
            self.zbegin = 0
            self.zend = 0
            self.dx_value[2] = 1
        else:
            self.zbegin = -model_data.model.width
            self.zend = model_data.model.width + dx_value[2]

        number_of_blocks = 4

        """ Definition of model
        """
        self.model_data = model_data

        self.dam_block = [""] * number_of_blocks
        self.dam_block[0] = self.model_data.damages[0].name
        self.dam_block[1] = self.model_data.damages[0].name

        self.int_block_id = [""] * number_of_blocks
        self.mat_block = [self.model_data.materials[0].name] * number_of_blocks

    def create_load_intro_node(self, x_value, y_value, k):
        """doc"""
        k = np.where(
            np.logical_and(
                x_value < self.xbegin + self.dx_value[0] * 3,
                y_value > 0,
            ),
            3,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value < self.xbegin + self.dx_value[0] * 3,
                y_value < 0,
            ),
            4,
            k,
        )
        return k

    @staticmethod
    def create_block(y_value, k):
        """doc"""
        k = np.where(y_value > 0, 1, k)
        k = np.where(y_value > 0, 2, k)
        return k

    def create_model(self):
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

        if len(x_value) > self.max_nodes:
            return "The number of nodes (" + str(len(x_value)) + ") is larger than the allowed " + str(self.max_nodes)

        if self.ignore_mesh and self.block_def != "":
            writer = ModelWriter(model_class=self)
            for _, block in enumerate(self.block_def):
                block.horizon = self.scal * max([self.dx_value[0], self.dx_value[1]])
            block_def = self.block_def

            try:
                writer.create_file(block_def)
            except TypeError as exception:
                return str(exception)

        else:
            vol = np.zeros(len(x_value))
            k = np.ones(len(x_value))
            if self.rot:
                angle_x = np.zeros(len(x_value))
                angle_y = np.zeros(len(x_value))
                angle_z = np.zeros(len(x_value))

            k = self.create_block(y_value, k)
            k = self.create_load_intro_node(x_value, y_value, k)

            vol = np.full_like(
                x_value,
                self.dx_value[0] * self.dx_value[1] * self.dx_value[2],
            )

            writer = ModelWriter(model_class=self)

            if self.rot:
                model = np.transpose(
                    np.vstack(
                        [
                            x_value.ravel(),
                            y_value.ravel(),
                            z_value.ravel(),
                            k.ravel(),
                            vol.ravel(),
                            angle_x.ravel(),
                            angle_y.ravel(),
                            angle_z.ravel(),
                        ]
                    )
                )
                writer.write_mesh_with_angles(model, self.software)
            else:
                model = np.transpose(
                    np.vstack(
                        [
                            x_value.ravel(),
                            y_value.ravel(),
                            z_value.ravel(),
                            k.ravel(),
                            vol.ravel(),
                        ]
                    )
                )
                writer.write_mesh(model, self.software, self.two_d)
            writer.write_node_sets(model, self.software)

            block_len = int(max(k))

            write_return = self.write_file(writer=writer, block_len=block_len)

            if write_return != 0:
                return write_return

        return "Model created"

    def create_blockdef(self, block_len):
        """doc"""
        block_dict = []
        for idx in range(0, block_len):
            block_def = Block(
                id=1,
                name="block_" + str(idx + 1),
                material=self.mat_block[idx],
                damageModel=self.dam_block[idx],
                horizon=self.scal * max([self.dx_value[0], self.dx_value[1]]),
                show=False,
            )
            block_dict.append(block_def)
        return block_dict

    def write_file(self, writer, block_len):
        """doc"""

        if self.block_def == "":
            block_def = self.create_blockdef(block_len)
        else:
            for _, block in enumerate(self.block_def):
                block.horizon = self.scal * max([self.dx_value[0], self.dx_value[1]])
            block_def = self.block_def

        try:
            writer.create_file(block_def)
        except TypeError as exception:
            return str(exception)
        return 0
