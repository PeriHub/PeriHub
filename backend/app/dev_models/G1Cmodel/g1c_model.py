# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import numpy as np

from ...support.base_models import Block
from ...support.model.geometry import Geometry
from ...support.writer.model_writer import ModelWriter


class G1Cmodel:
    def __init__(
        self,
        model_data,
        filename="G1Cmodel",
        model_folder_name="",
        username="",
        max_nodes=10000000,
        ignore_mesh=False,
        dx_value=[0.25, 0.25, 0.25],
    ):
        """
        definition der blocks
        k =
        1 basisplatte
        2 X Zero Node Set
        3 X Zero Node Set
        4 Load Node Set
        """

        self.filename = filename
        self.model_folder_name = model_folder_name
        self.scal = 3.01
        self.disc_type = "txt"
        self.meshFile = None
        self.two_d = model_data.model.twoDimensional
        self.ns_list = []
        if not dx_value:
            dx_value = [0.001, 0.001, 0.001]
        self.dx_value = dx_value
        self.angle = model_data.model.angles
        self.length = model_data.model.length
        self.xbegin = 0.0
        self.ybegin = -model_data.model.height / 2
        self.xend = model_data.model.length
        self.yend = model_data.model.height / 2
        self.rot = model_data.model.rotatedAngles
        self.block_def = model_data.blocks
        self.username = username
        self.max_nodes = max_nodes
        self.ignore_mesh = ignore_mesh
        self.notch_enabled = model_data.model.notchEnabled
        self.cracklength = model_data.model.cracklength
        if self.two_d:
            self.zbegin = 0
            self.zend = 0
            self.dx_value[2] = 1
        else:
            self.zbegin = -model_data.model.width / 2
            self.zend = model_data.model.width / 2

        number_of_blocks = 5

        """ Definition of model
        """
        self.model_data = model_data

        self.dam_block = [""] * number_of_blocks
        self.dam_block[0] = self.model_data.damages[0].name

        self.int_block_id = [""] * number_of_blocks
        self.mat_block = [self.model_data.materials[0].name] * number_of_blocks

    def create_blocks(self, x_value, y_value, k):
        """doc"""
        k = np.where(
            y_value <= 0,
            2,
            k,
        )

        k = np.where(
            x_value <= self.cracklength,
            3,
            k,
        )

        x_intro = self.cracklength / 2
        k = np.where(
            np.logical_and(
                np.logical_and(
                    x_value <= x_intro + 0.5 * self.dx_value[0],
                    x_value >= x_intro - 0.5 * self.dx_value[0],
                ),
                y_value >= self.yend - 0.5 * self.dx_value[1],
            ),
            4,
            k,
        )
        k = np.where(
            np.logical_and(
                np.logical_and(
                    x_value <= x_intro + 0.5 * self.dx_value[0],
                    x_value >= x_intro - 0.5 * self.dx_value[0],
                ),
                y_value <= -self.yend + 0.5 * self.dx_value[1],
            ),
            5,
            k,
        )
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
                angle_x = np.full_like(x_value, self.angle[0])
                if self.two_d:
                    angle_y = np.zeros(len(x_value))
                    angle_z = np.zeros(len(x_value))
                else:
                    angle_y = np.full_like(x_value, self.angle[1])
                    angle_z = np.full_like(x_value, self.angle[2])

            k = self.create_blocks(x_value, y_value, k)

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
                writer.write_mesh_with_angles(model, self.two_d)
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
                writer.write_mesh(model, self.two_d)
            writer.write_node_sets(model)

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
        # 3d tbd
        return block_dict

    def write_file(self, writer, block_len):
        """doc"""

        if not self.block_def:
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
