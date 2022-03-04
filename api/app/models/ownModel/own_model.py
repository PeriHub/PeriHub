from support.model_writer import ModelWriter


class OwnModel:
    def __init__(
        self,
        dx_value=[0.0005, 0.0005, 0.0005],
        disc_type="txt",
        two_d=False,
        horizon=0.1,
        filename="ownModel",
        material="",
        damage="",
        block="",
        boundary_condition="",
        bond_filter="",
        compute="",
        output="",
        solver="",
        username="",
    ):

        self.filename = filename
        self.scal = 1
        self.disc_type = disc_type
        self.two_d = two_d
        self.horizon = horizon
        self.dx_value = dx_value
        self.block_def = block
        self.username = username
        self.damage_dict = damage
        self.compute_dict = compute
        self.output_dict = output
        self.material_dict = material
        self.bondfilters = bond_filter
        self.bc_dict = boundary_condition
        self.solver_dict = solver

    def create_model(self):
        """doc"""

        writer = ModelWriter(model_class=self)
        self.write_file(writer=writer)

        return "Model created"

    def write_file(self, writer):
        """doc"""

        for _, block in enumerate(self.block_def):
            block["horizon"] = self.horizon

        writer.create_file(self.block_def)
