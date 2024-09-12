# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import time

import numpy as np

from ...support.base_models import Block
from ...support.globals import log
from ...support.model.geometry import Geometry
from ...support.writer.model_writer import ModelWriter


class Dogbone:
    """doc"""

    def __init__(
        self,
        model_data,
        filename="Dogbone",
        model_folder_name="Default",
        username="",
        max_nodes=100000,
        ignore_mesh=False,
        dx_value=[0.05, 0.05, 0.05],
    ):
        """
        definition der blocks
        k =
        1 X Zero Node Set
        2 No Damage
        3 Damage
        4 No Damage
        5 Load Node Set
        """
        start_time = time.time()

        self.filename = filename
        self.model_folder_name = model_folder_name
        self.scal = 3.01
        self.disc_type = "txt"
        self.mesh_file = None
        self.two_d = model_data.model.twoDimensional
        self.ns_list = [3, 4]
        self.dx_value = dx_value
        self.xend = model_data.model.length
        self.height1 = model_data.model.height
        self.height2 = model_data.model.height2
        self.block_def = model_data.blocks
        self.structured = model_data.model.structured
        self.rot = model_data.model.rotatedAngles
        self.username = username
        self.max_nodes = max_nodes
        self.ignore_mesh = ignore_mesh
        if self.two_d:
            self.zend = 1
            self.dx_value[2] = 1
        else:
            self.zend = model_data.model.width + dx_value[2]

        number_of_blocks = 5

        """ Definition of model
        """
        self.model_data = model_data

        self.dam_block = [""] * number_of_blocks
        if len(self.model_data.damages) != 0:
            self.dam_block[2] = self.model_data.damages[0].name

        self.int_block_id = [""] * number_of_blocks
        self.mat_block = [self.model_data.materials[0].name] * number_of_blocks

        log.info(f"Initialized in {(time.time() - start_time):.2f} seconds")

    def create_model(self):
        """doc"""

        geo = Geometry()
        boundary_condition = 0.2
        radius = 7.6
        length2 = 5.7
        delta_height = (self.height1 - self.height2) / 2
        delta_length = np.sqrt(radius * radius - (radius - delta_height) ** 2)
        length1 = (self.xend - 2 * delta_length - length2) / 2
        alpha = np.arccos((radius - delta_height) / radius) * 180 / np.pi

        x_value_0 = np.arange(0, self.xend, self.dx_value[0])
        y_value_0 = np.arange(
            -self.height1 / 2 - self.dx_value[1],
            self.height1 / 2 + self.dx_value[1],
            self.dx_value[1],
        )
        z_value_0 = np.arange(0, self.zend, self.dx_value[2])

        num = len(x_value_0) * len(y_value_0) * len(z_value_0)

        if num > self.max_nodes:
            return "The number of nodes (" + str(num) + ") is larger than the allowed " + str(self.max_nodes)

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
            if self.structured:
                number_nodes = 2 * int((self.height1 / self.dx_value[1]) / 2) + 1
                num_rows = int((number_nodes - 1) / 2)
                fh2 = (2 * self.dx_value[1] * (num_rows) + self.height2 - self.height1) / (
                    self.dx_value[1] * (num_rows)
                )
                x_value = np.array([])
                y_value = np.array([])
                z_value = np.array([])
                vol_factor = np.array([])
                k = []
                for zval in z_value_0:
                    for i in range(0, num_rows):
                        height1 = self.height1 - self.dx_value[1] * i * 2
                        height2 = self.height2 - self.dx_value[1] * i * fh2
                        # R1 = radius+0.03*i
                        dh1 = (height1 - height2) / 2

                        alpha1 = np.arccos((radius - dh1) / radius) * 180 / np.pi

                        (
                            top_surf,
                            bottom_surf,
                        ) = geo.create_boundary_curve(
                            height=height1 / 2,
                            length1=length1,
                            radius=radius,
                            length2=length2,
                            alpha_max=alpha,
                            alpha_max1=alpha1,
                            delta_length=delta_length,
                            delta_height=dh1,
                        )
                        block_def = np.array(
                            [
                                0,
                                boundary_condition,
                                length1,
                                length1 + 2 * delta_length + length2,
                                self.xend - boundary_condition,
                            ]
                        )
                        upper_y_value = top_surf(x_value_0)
                        lower_y_value = bottom_surf(x_value_0)
                        x_value = np.concatenate((x_value, x_value_0))
                        x_value = np.concatenate((x_value, x_value_0))
                        y_value = np.concatenate((y_value, upper_y_value))
                        y_value = np.concatenate((y_value, lower_y_value))
                        z_value = np.concatenate((z_value, np.full_like(x_value_0, zval)))
                        z_value = np.concatenate((z_value, np.full_like(x_value_0, zval)))
                        vol_factor = np.concatenate(
                            (
                                vol_factor,
                                (upper_y_value - lower_y_value) / height1,
                            )
                        )
                        vol_factor = np.concatenate(
                            (
                                vol_factor,
                                (upper_y_value - lower_y_value) / height1,
                            )
                        )

                        for xval in x_value_0:
                            for idx, val in enumerate(block_def):
                                if geo.check_val_greater(xval, val):
                                    mat_num = idx + 1
                            k.append(mat_num)
                        for xval in x_value_0:
                            for idx, val in enumerate(block_def):
                                if geo.check_val_greater(xval, val):
                                    mat_num = idx + 1
                            k.append(mat_num)

                    x_value = np.concatenate((x_value, x_value_0))
                    y_value = np.concatenate((y_value, np.zeros_like(x_value_0)))
                    z_value = np.concatenate((z_value, np.full_like(x_value_0, zval)))
                    vol_factor = np.concatenate((vol_factor, np.ones_like(x_value_0)))
                    for xval in x_value_0:
                        for idx, val in enumerate(block_def):
                            if geo.check_val_greater(xval, val):
                                mat_num = idx + 1
                        k.append(mat_num)

                vol = np.full_like(
                    x_value,
                    self.dx_value[0] * self.dx_value[0] * vol_factor,
                )

            else:
                top_surf, bottom_surf = geo.create_boundary_curve_old(
                    height=self.height1 / 2,
                    length1=length1,
                    radius=radius,
                    length2=length2,
                    alpha_max=alpha,
                    delta_length=delta_length,
                    delta_height=delta_height,
                )
                block_def = np.array(
                    [
                        0,
                        boundary_condition,
                        length1,
                        length1 + 2 * delta_length + length2,
                        self.xend - boundary_condition,
                    ]
                )

                x_value = []
                y_value = []
                z_value = []
                k = []
                mat_num = 0
                for xval in x_value_0:
                    for yval in y_value_0:
                        for zval in z_value_0:
                            if geo.check_val_greater(yval, bottom_surf(xval)) and geo.check_val_lower(
                                yval, top_surf(xval)
                            ):
                                for idx, val in enumerate(block_def):
                                    if geo.check_val_greater(xval, val):
                                        mat_num = idx + 1
                                x_value.append(xval)
                                y_value.append(yval)
                                z_value.append(zval)
                                k.append(mat_num)
                vol = np.full_like(x_value, self.dx_value[0] * self.dx_value[0])

            if self.rot:
                angle_x = np.zeros(len(x_value))
                angle_y = np.zeros(len(x_value))
                angle_z = np.zeros(len(x_value))

            writer = ModelWriter(model_class=self)

            if self.rot:
                model = np.transpose(
                    np.vstack(
                        [
                            np.array(x_value).ravel(),
                            np.array(y_value).ravel(),
                            np.array(z_value).ravel(),
                            np.array(k).ravel(),
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
                            np.array(x_value).ravel(),
                            np.array(y_value).ravel(),
                            np.array(z_value).ravel(),
                            np.array(k).ravel(),
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

        if self.block_def == "":
            block_def = self.create_blockdef(block_len)
        else:
            for _, block in enumerate(self.block_def):
                block.horizon = self.scal * max([self.dx_value[0], self.dx_value[1]])
            block_def = self.block_def

        # try:
        writer.create_file(block_def)
        # except TypeError as exception:
        #     return str(exception)
        return 0
