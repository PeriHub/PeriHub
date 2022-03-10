"""
doc
"""
import time
import numpy as np

# import ast
from scipy import interpolate
from support.base_models import (
    Adapt,
    Block,
    BondFilters,
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
from support.material import MaterialRoutines
from support.geometry import Geometry


class GIICmodel:
    def __init__(
        self,
        xend=1,
        yend=1,
        zend=1,
        dx_value=None,
        filename="GIICmodel",
        two_d=False,
        rot="False",
        angle=None,
        material=None,
        damage=None,
        block=None,
        boundary_condition=None,
        bond_filter=None,
        compute=None,
        output=None,
        solver=None,
        username="",
        max_nodes=100000,
        ignore_mesh=False,
    ):
        """
        definition der blocks
        k =
        1 basisplatte
        2 RB links
        3 RB rechts
        4 Last
        5 RB Node links
        6 RB Node rechts
        7 Kraft Node
        8 Schadensbereich
        9 Schadensbereich
        10 RB Node links oben
        11 RB links oben - fehlt noch
        """
        start_time = time.time()

        self.filename = filename
        self.scal = 4.01
        self.disc_type = "txt"
        self.two_d = two_d
        self.rot = rot
        # anriss
        self.length = 20 / 151 * xend
        self.block_def = block

        if not dx_value:
            dx_value = [0.1, 0.1, 0.1]
        self.dx_value = dx_value
        if not angle:
            angle = [0, 0]
        self.angle = angle
        self.xend = xend
        self.yend = yend
        self.rot = rot
        self.username = username
        self.max_nodes = max_nodes
        self.ignore_mesh = ignore_mesh
        if two_d:
            self.zend = 0
            self.dx_value[2] = 1
        else:
            self.zend = zend

        number_of_blocks = 10
        xbound = [
            0,
            4 * dx_value[0],
            5 * dx_value[0],
            xend - 4 * dx_value[0],
            xend - 3 * dx_value[0],
            xend + dx_value[0],
        ]
        ybound = [0, 4 * dx_value[1], 5 * dx_value[1], yend + dx_value[1]]

        z_value = [2, 2, 1, 1, 3, 3]
        self.boundfuncx = interpolate.interp1d(xbound, z_value, kind="linear")
        z_value = [1, 1, 0, 0]
        self.boundfuncy = interpolate.interp1d(ybound, z_value, kind="linear")
        xload = [
            0,
            xend / 2 - 2 * dx_value[0],
            xend / 2 + 3 * dx_value[0],
            xend + dx_value[0],
        ]
        z_value = [1, 4, 4, 1]
        self.loadfuncx = interpolate.interp1d(xload, z_value, kind="linear")
        yload = [0, yend - 5 * dx_value[1], yend - 4 * dx_value[1], yend + dx_value[1]]
        z_value = [1, 1, 4, 4]
        self.loadfuncy = interpolate.interp1d(yload, z_value, kind="linear")

        z_value = [1, 1, 8, 8, 9, 9, 1, 1]
        # yblock = [
        #     0,
        #     yend / 2 - 5 * dx_value[1],
        #     yend / 2 - 4 * dx_value[1],
        #     yend / 2 - dx_value[1] / 4,
        #     yend / 2 + dx_value[1] / 4,
        #     yend / 2 + 4 * dx_value[1],
        #     yend / 2 + 5 * dx_value[1],
        #     yend + dx_value[1],
        # ]

        # self.blockfuny = interpolate.interp1d(yblock, z_value, kind="linear")
        """ Definition of model
        """

        mat_name_list = ["PMMA"]
        self.material_dict = []
        if not damage:
            damage_dict = Damage(
                id=1,
                Name="PMMADamage",
                damageModel="Critical Energy Correspondence",
                criticalStretch=10.0,
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

        if not compute:
            compute_dict1 = Compute(
                id=1,
                Name="External_Displacement",
                variable="Displacement",
                calculationType="Minimum",
                blockName="block_7",
            )
            compute_dict2 = Compute(
                id=2,
                Name="External_Force",
                variable="Force",
                calculationType="Sum",
                blockName="block_7",
            )
            self.compute_dict = [compute_dict1, compute_dict2]
        else:
            self.compute_dict = compute

        if not output:
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
                Frequency=5000,
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

        if not material:
            i = 0
            for material_name in mat_name_list:
                mat_dict = Material(
                    id=i + 1,
                    Name=material_name,
                    MatType="Linear Elastic Correspondence",
                    density=1.95e-07,
                    bulkModulus=None,
                    shearModulus=None,
                    youngsModulus=210000.0,
                    poissonsRatio=0.3,
                    tensionSeparation=False,
                    nonLinear=True,
                    planeStress=True,
                    materialSymmetry="Anisotropic",
                    stabilizatonType="Global Stiffness",
                    thickness=10.0,
                    hourglassCoefficient=1.0,
                    actualHorizon=None,
                    yieldStress=None,
                    Parameter=[],
                    Properties=[],
                )
                if mat_dict.materialSymmetry == "Anisotropic":
                    # self.angle = [60, -60]
                    params = [
                        165863.6296530634,  # C11
                        4090.899504376252,  # C12
                        2471.126276093059,  # C13
                        0.0,  # C14
                        0.0,  # C15
                        0.0,  # C16
                        9217.158022124806,  # C22
                        2471.126276093059,  # C23
                        0.0,  # C24
                        0.0,  # C25
                        0.0,  # C26
                        9217.158022124804,  # C33
                        0.0,  # C34
                        0.0,  # C35
                        0.0,  # C36
                        3360.0,  # C44
                        0.0,  # C45
                        0.0,  # C46
                        4200.0,  # C55
                        0.0,  # C56
                        4200.0,
                    ]  # C66
                    mat = MaterialRoutines(angle=self.angle)
                    mat_dict.Parameter = mat.stiffness_matrix(
                        mat_type="anisotropic", mat_param=params
                    )
                i += 1
                self.material_dict.append(mat_dict)
        else:
            # self.angle = angle
            self.material_dict = material

        if not bond_filter:
            bf1 = BondFilters(
                id=1,
                Name="bf_1",
                type="Rectangular_Plane",
                normalX=0.0,
                normalY=1.0,
                normalZ=0.0,
                lowerLeftCornerX=0.0,
                lowerLeftCornerY=self.yend,
                lowerLeftCornerZ=-0.1,
                bottomUnitVectorX=1.0,
                bottomUnitVectorY=0.0,
                bottomUnitVectorZ=0.0,
                bottomLength=self.length,
                sideLength=zend + 0.5,
                centerX=0.0,
                centerY=1.0,
                centerZ=0.0,
                radius=1.0,
                show=True,
            )
            self.bondfilters = [bf1]
        else:
            self.bondfilters = bond_filter

        if not boundary_condition:
            bc1 = BoundaryConditions(
                id=1,
                Name="BC_1",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=5,
                coordinate="y",
                value="0*t",
            )
            bc2 = BoundaryConditions(
                id=2,
                Name="BC_2",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=6,
                coordinate="y",
                value="0*t",
            )
            bc3 = BoundaryConditions(
                id=3,
                Name="BC_3",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=7,
                coordinate="y",
                value="-10*t",
            )
            bc4 = BoundaryConditions(
                id=4,
                Name="BC_4",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=10,
                coordinate="y",
                value="0*t",
            )
            self.bc_dict = [bc1, bc2, bc3, bc4]
        else:
            self.bc_dict = boundary_condition

        if not solver:
            self.solver_dict = Solver(
                verbose=False,
                initialTime=0.0,
                finalTime=0.03,
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
        self.dam_block[7] = "PMMADamage"
        self.dam_block[8] = "PMMADamage"
        self.int_block_id = [""] * number_of_blocks
        self.int_block_id[7] = 9
        self.int_block_id[8] = 8
        self.mat_block = ["PMMA"] * number_of_blocks

        print(f"Initialized in {(time.time() - start_time):.2f} seconds")

    def create_load_block(self, x_value, y_value, k):
        k = np.where(
            self.loadfuncx(x_value) == self.loadfuncy(y_value),
            self.loadfuncx(x_value),
            k,
        )
        return k

    def create_boundary_condition_block(self, x_value, y_value, k):
        k = np.array(
            ((self.boundfuncx(x_value) - 1) * self.boundfuncy(y_value) + 1), dtype="int"
        )
        return k

    def create_load_intro_node(self, x_value, y_value, k):
        k = np.where(
            np.logical_and(
                (self.xend - self.dx_value[0]) / 2 < x_value,
                np.logical_and(
                    x_value < (self.xend + self.dx_value[0]) / 2,
                    y_value > self.yend - self.dx_value[1] / 2,
                ),
            ),
            7,
            k,
        )
        return k

    def create_bc_node(self, x_value, y_value, k):
        k = np.where(
            np.logical_and(x_value <= 0 + self.dx_value[0], y_value == 0), 5, k
        )
        k = np.where(
            np.logical_and(x_value > self.xend - self.dx_value[0] / 3, y_value == 0),
            6,
            k,
        )
        k = np.where(
            np.logical_and(x_value == 0, y_value > self.yend - self.dx_value[1] / 3),
            10,
            k,
        )
        return k

    def create_block(self, y_value, k):
        k = np.where(
            np.logical_and(
                self.yend / 2 - 5 * self.dx_value[1] < y_value, y_value < self.yend / 2
            ),
            8,
            k,
        )
        k = np.where(
            np.logical_and(
                self.yend / 2 <= y_value, y_value < self.yend / 2 + 5 * self.dx_value[1]
            ),
            9,
            k,
        )
        return k

    def create_angles(self, x_value, y_value):
        """doc"""
        angle_x = np.zeros_like(x_value)
        angle_y = np.where(y_value < self.yend / 2, self.angle[0], self.angle[1])
        angle_z = np.zeros_like(x_value)

        return angle_x, angle_y, angle_z

    def create_model(self):
        """doc"""

        geo = Geometry()
        x_value, y_value, z_value = geo.create_points(
            coor=[0, self.xend, 0, self.yend, 0, self.zend], dx_value=self.dx_value
        )

        if len(x_value) > self.max_nodes:
            return (
                "The number of nodes ("
                + str(len(x_value))
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
            start_time = time.time()

            vol = np.zeros(len(x_value))
            k = np.ones(len(x_value))
            if self.rot:
                angle_x = np.zeros(len(x_value))
                angle_y = np.zeros(len(x_value))
                angle_z = np.zeros(len(x_value))

            print(f"Angles assigned in {(time.time() - start_time):.2f} seconds")
            start_time = time.time()
            if self.rot:
                angle_x, angle_y, angle_z = self.create_angles(x_value, y_value)

            k = np.ones_like(x_value)

            k = np.where(
                y_value >= self.yend / 2,
                self.create_load_block(x_value, y_value, k),
                self.create_boundary_condition_block(x_value, y_value, k),
            )
            k = self.create_bc_node(x_value, y_value, k)
            k = self.create_load_intro_node(x_value, y_value, k)
            k = self.create_block(y_value, k)

            vol = np.full_like(
                x_value, self.dx_value[0] * self.dx_value[1] * self.dx_value[2]
            )

            print(f"BC and Blocks created in {(time.time() - start_time):.2f} seconds")

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
                writer.write_mesh_with_angles(model)
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
