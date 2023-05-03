from support.model_writer import ModelWriter


class OwnModel:
    def __init__(
        self,
        dx_value=None,
        disc_type="txt",
        two_d=False,
        filename="ownModel",
        model_sub_name="",
        model_data=None,
        username="",
    ):
        self.filename = filename
        self.model_sub_name = model_sub_name
        self.scal = 1
        self.disc_type = disc_type
        self.two_d = two_d
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
