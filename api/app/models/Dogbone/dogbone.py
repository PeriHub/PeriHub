"""
doc
"""
import time
import numpy as np
import matplotlib.pyplot as plt
from support.base_models import (
    Adapt,
    Block,
    BoundaryConditions,
    Compute,
    Damage,
    Material,
    Output,
    Newton,
    Solver,
    Verlet,
)
from support.model_writer import ModelWriter
from support.geometry import Geometry


class Dogbone:
    """doc"""

    def __init__(
        self,
        xend=0.15,
        height1=0.02,
        height2=0.01,
        zend=0.001,
        dx_value=[0.0005, 0.0005, 0.0005],
        filename="Dogbone",
        two_d=False,
        structured=True,
        rot=False,
        angle=[0, 0],
        material="",
        damage="",
        block="",
        boundary_condition="",
        bond_filter="",
        compute="",
        output="",
        solver="",
        username="",
        max_nodes=100000,
        ignore_mesh=False,
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
        self.scal = 4.01
        self.disc_type = "txt"
        self.two_d = two_d
        self.ns_list = [3, 4]
        self.dx_value = dx_value
        self.xend = xend
        self.height1 = height1
        self.height2 = height2
        self.structured = structured
        self.rot = rot
        self.block_def = block
        self.username = username
        self.max_nodes = max_nodes
        self.ignore_mesh = ignore_mesh
        if self.two_d:
            self.zend = 1
            self.dx_value[2] = 1
        else:
            self.zend = zend + dx_value[2]

        number_of_blocks = 5

        """ Definition of model
        """

        mat_name_list = ["PMMA"]
        self.material_dict = []
        self.angle = [0, 0]
        if damage == "":
            damage_dict = Damage(
                id=1,
                Name="PMMADamage",
                damageModel="Critical Energy Correspondence",
                criticalStretch=10,
                criticalEnergy=5.1,
                interblockdamageEnergy=0.01,
                planeStress=True,
                onlyTension=True,
                detachedNodesCheck=True,
                thickness=10,
                hourglassCoefficient=1.0,
                stabilizatonType="Global Stiffness",
            )
            self.damage_dict = [damage_dict]
        else:
            self.damage_dict = damage

        if compute == "":
            compute_dict1 = Compute(
                id=1,
                Name="External_Displacement",
                variable="Displacement",
                calculationType="Minimum",
                blockName="block_3",
            )
            compute_dict2 = Compute(
                id=2,
                Name="External_Force",
                variable="Force",
                calculationType="Sum",
                blockName="block_3",
            )
            self.compute_dict = [compute_dict1, compute_dict2]
        else:
            self.compute_dict = compute

        if output == "":
            output_dict1 = Output(
                id=1,
                Name="Output1",
                Displacement=True,
                Force=True,
                Damage=True,
                Velocity=True,
                Partial_Stress=False,
                External_Force=False,
                External_Displacement=False,
                Number_Of_Neighbors=False,
                Frequency=500,
                InitStep=0,
            )
            output_dict2 = Output(
                id=2,
                Name="Output2",
                Displacement=False,
                Force=False,
                Damage=True,
                Velocity=False,
                Partial_Stress=True,
                External_Force=True,
                External_Displacement=True,
                Number_Of_Neighbors=False,
                Frequency=200,
                InitStep=0,
            )
            self.output_dict = [output_dict1, output_dict2]
        else:
            self.output_dict = output

        if material == "":
            i = 0
            for material_name in mat_name_list:
                mat_dict = Material(
                    id=i + 1,
                    Name=material_name,
                    MatType="Linear Elastic Correspondence",
                    density=200000.0,
                    bulkModulus=None,
                    shearModulus=None,
                    youngsModulus=1.5e9,
                    poissonsRatio=0.3,
                    tensionSeparation=False,
                    nonLinear=True,
                    planeStress=True,
                    materialSymmetry="Isotropic",
                    stabilizatonType="Global Stiffness",
                    thickness=10.0,
                    hourglassCoefficient=1.0,
                    actualHorizon=None,
                    yieldStress=31.3e4,
                    Parameter=[],
                    Properties=[],
                )
                i += 1
                self.material_dict.append(mat_dict)
        else:
            self.angle = angle
            self.material_dict = material

        if bond_filter == "":
            self.bondfilters = []
        else:
            self.bondfilters = bond_filter

        if boundary_condition == "":
            bc1 = BoundaryConditions(
                id=1,
                Name="BC_1",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=1,
                coordinate="x",
                value="0*t",
            )
            bc2 = BoundaryConditions(
                id=2,
                Name="BC_2",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=5,
                coordinate="x",
                value="10*t",
            )
            self.bc_dict = [bc1, bc2]
        else:
            self.bc_dict = boundary_condition

        if solver == "":
            self.solver_dict = Solver(
                verbose=False,
                initialTime=0.0,
                finalTime=0.075,
                fixedDt=None,
                solvertype="Verlet",
                safetyFactor=0.95,
                numericalDamping=0.000005,
                peridgimPreconditioner="None",
                nonlinearSolver="Line Search Based",
                numberofLoadSteps=100,
                maxSolverIterations=50,
                relativeTolerance=1e-8,
                maxAgeOfPrec=100,
                directionMethod="Newton",
                newton=Newton(),
                lineSearchMethod="Polynomial",
                verletSwitch=False,
                verlet=Verlet(),
                stopAfterDamageInitation=False,
                stopBeforeDamageInitation=False,
                adaptivetimeStepping=False,
                adapt=Adapt(),
                filetype="yaml",
            )
        else:
            self.solver_dict = solver

        self.dam_block = [""] * number_of_blocks
        self.dam_block[2] = "PMMADamage"

        self.int_block_id = [""] * number_of_blocks
        self.mat_block = ["PMMA"] * number_of_blocks

        print(f"Initialized in {(time.time() - start_time):.2f} seconds")

    def create_model(self):
        """doc"""

        geo = Geometry()
        boundary_condition = 0.002
        radius = 0.076
        length2 = 0.057
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
            return (
                "The number of nodes ("
                + str(num)
                + ") is larger than the allowed "
                + str(self.max_nodes)
            )

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
                fh2 = (
                    2 * self.dx_value[1] * (num_rows) + self.height2 - self.height1
                ) / (self.dx_value[1] * (num_rows))
                x_value = []
                y_value = []
                z_value = []
                k = []
                for zval in z_value_0:
                    for i in range(0, num_rows):
                        height1 = self.height1 - self.dx_value[1] * i * 2
                        height2 = self.height2 - self.dx_value[1] * i * fh2
                        # R1 = radius+0.03*i
                        dh1 = (height1 - height2) / 2

                        alpha1 = np.arccos((radius - dh1) / radius) * 180 / np.pi

                        top_surf, bottom_surf = geo.create_boundary_curve(
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

                        x_value = np.concatenate((x_value, x_value_0))
                        x_value = np.concatenate((x_value, x_value_0))
                        y_value = np.concatenate((y_value, top_surf(x_value_0)))
                        y_value = np.concatenate((y_value, bottom_surf(x_value_0)))
                        z_value = np.concatenate(
                            (z_value, np.full_like(x_value_0, zval))
                        )
                        z_value = np.concatenate(
                            (z_value, np.full_like(x_value_0, zval))
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
                        plt.scatter(x_value_0, top_surf(x_value_0))
                        plt.scatter(x_value_0, bottom_surf(x_value_0))

                    x_value = np.concatenate((x_value, x_value_0))
                    y_value = np.concatenate((y_value, np.zeros_like(x_value_0)))
                    z_value = np.concatenate((z_value, np.full_like(x_value_0, zval)))
                    # plt.scatter(x_value_0, np.zeros_like(x_value_0))
                    for xval in x_value_0:
                        for idx, val in enumerate(block_def):
                            if geo.check_val_greater(xval, val):
                                mat_num = idx + 1
                        k.append(mat_num)

                # plt.show()

                vol = np.full_like(x_value, self.dx_value[0] * self.dx_value[0])

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

                # plt.scatter(x_value_0, top_surf(x_value_0))
                # plt.scatter(x_value_0, bottom_surf(x_value_0))
                # plt.show()
                # num = len(x_value_0)*len(y_value_0)*len(z_value_0)
                x_value = []
                y_value = []
                z_value = []
                k = []
                mat_num = 0
                for xval in x_value_0:
                    for yval in y_value_0:
                        for zval in z_value_0:
                            if geo.check_val_greater(
                                yval, bottom_surf(xval)
                            ) and geo.check_val_lower(yval, top_surf(xval)):
                                for idx, val in enumerate(block_def):
                                    if geo.check_val_greater(xval, val):
                                        mat_num = idx + 1
                                x_value.append(xval)
                                y_value.append(yval)
                                z_value.append(zval)
                                k.append(mat_num)

                # plt.scatter(x_value_0, np.zeros_like(x_value_0))
                # plt.scatter(np.zeros_like(y_value_0),y_value_0)
                plt.scatter(x_value, y_value)
                plt.show()
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
                writer.write_mesh_with_angles(model)
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
                writer.write_mesh(model)
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
                Name="block_" + str(idx + 1),
                material=self.mat_block[idx],
                damageModel=self.dam_block[idx],
                horizon=self.scal * max([self.dx_value[0], self.dx_value[1]]),
                interface=self.int_block_id[idx],
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

        try:
            writer.create_file(block_def)
        except TypeError as exception:
            return str(exception)
        return 0
