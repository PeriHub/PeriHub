# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

from support.writer.model_writer import ModelWriter


class OwnModel:
    def __init__(
        self,
        model_data,
        filename="ownModel",
        model_folder_name="",
        disc_type="txt",
        username="",
        dx_value=None,
    ):
        self.filename = filename
        self.model_folder_name = model_folder_name
        self.scal = 1
        self.disc_type = disc_type
        self.mesh_file = model_data.model.mesh_file
        self.two_d = model_data.model.twoDimensional
        self.horizon = model_data.model.horizon
        if not dx_value:
            dx_value = [0.0005, 0.0005, 0.0005]
        self.dx_value = dx_value
        self.model_data = model_data
        self.username = username
        self.block_def = model_data.blocks

    def create_model(self):
        """doc"""

        writer = ModelWriter(model_class=self)
        self.write_file(writer=writer)

        return "Model created"

    def write_file(self, writer):
        """doc"""

        for _, block in enumerate(self.block_def):
            block.horizon = self.horizon

        writer.create_file(self.block_def)
