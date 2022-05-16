"""
doc
"""
import numpy as np
from support.base_models import (
    Adapt,
    Block,
    BondFilters,
    BoundaryConditions,
    Contact,
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


class DCBmodel:

    contact_dict = Contact(
        enabled=False,
        searchRadius=0,
        searchFrequency=0,
        contactModels=[],
        interactions=[],
    )

    def __init__(
        self,
        xend=0.045,
        yend=0.01,
        zend=0.003,
        dx_value=None,
        filename="DCBmodel",
        two_d=False,
        rot="False",
        angle=None,
        material=None,
        damage=None,
        block=None,
        contact=contact_dict,
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
        2 Z Zero Node Set
        3 Min Y Up Node Set
        4 Min Y Down Node Set
        """

        self.filename = filename
        self.scal = 4.01
        self.disc_type = "txt"
        self.two_d = two_d
        self.ns_list = [3, 4]
        if not dx_value:
            dx_value = [0.001, 0.001, 0.001]
        self.dx_value = dx_value
        if not angle:
            angle = [0, 0]
        self.angle = angle
        self.xbegin = -0.005
        self.ybegin = -yend
        self.xend = xend + dx_value[0]
        self.yend = yend + dx_value[1]
        self.rot = rot
        self.block_def = block
        self.username = username
        self.max_nodes = max_nodes
        self.ignore_mesh = ignore_mesh
        if self.two_d:
            self.zbegin = 0
            self.zend = 0
            self.dx_value[2] = 1
        else:
            self.zbegin = -zend
            self.zend = zend + dx_value[2]

        number_of_blocks = 4

        """ Definition of model
        """
        mat_name_list = ["PMMA"]
        self.material_dict = []
        if not damage:
            damage_dict = Damage(
                id=1,
                name="PMMADamage",
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

        if not compute:
            compute_dict1 = Compute(
                id=1,
                name="External_Displacement",
                variable="Displacement",
                calculationType="Minimum",
                blockName="block_3",
            )
            compute_dict2 = Compute(
                id=2,
                name="External_Force",
                variable="Force",
                calculationType="Sum",
                blockName="block_3",
            )
            self.compute_dict = [compute_dict1, compute_dict2]
        else:
            self.compute_dict = compute

        if not output:
            output_dict1 = Output(
                id=1,
                name="Output1",
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
                name="Output2",
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
                    name=material_name,
                    matType="Linear Elastic Correspondence",
                    density=1.95e-07,
                    bulkModulus=None,
                    shearModulus=None,
                    youngsModulus=2.1e5,
                    poissonsRatio=0.3,
                    tensionSeparation=False,
                    nonLinear=True,
                    planeStress=True,
                    materialSymmetry="Isotropic",
                    stabilizatonType="Global Stiffness",
                    thickness=10.0,
                    hourglassCoefficient=1.0,
                    actualHorizon=None,
                    yieldStress=None,
                    Parameter=[],
                    properties=[],
                )
                i += 1
                self.material_dict.append(mat_dict)
        else:
            self.material_dict = material

        if not bond_filter:
            bf1 = BondFilters(
                id=1,
                name="bf_1",
                type="Rectangular_Plane",
                normalX=0.0,
                normalY=1.0,
                normalZ=0.0,
                lowerLeftCornerX=-0.06,
                lowerLeftCornerY=0.0,
                lowerLeftCornerZ=-0.01,
                bottomUnitVectorX=1.0,
                bottomUnitVectorY=0.0,
                bottomUnitVectorZ=0.0,
                bottomLength=0.01,
                sideLength=0.01,
                centerX=0.0,
                centerY=1.0,
                centerZ=0.0,
                radius=1.0,
                show=True,
            )
            self.bondfilters = [bf1]
        else:
            self.bondfilters = bond_filter
        self.contact_dict = contact

        if not boundary_condition:
            bc1 = BoundaryConditions(
                id=1,
                name="BC_1",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=3,
                coordinate="y",
                value="0.004*t",
            )
            bc2 = BoundaryConditions(
                id=2,
                name="BC_2",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=4,
                coordinate="y",
                value="-0.004*t",
            )
            bc3 = BoundaryConditions(
                id=3,
                name="BC_3",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=1,
                coordinate="z",
                value="0*t",
            )
            bc4 = BoundaryConditions(
                id=3,
                name="BC_4",
                NodeSets=None,
                boundarytype="Prescribed Displacement",
                blockId=2,
                coordinate="z",
                value="0*t",
            )
            self.bc_dict = [bc1, bc2, bc3, bc4]
        else:
            self.bc_dict = boundary_condition

        if not solver:
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
                numberOfLoadSteps=100,
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
        self.dam_block[0] = "PMMADamage"
        self.dam_block[1] = "PMMADamage"

        self.int_block_id = [""] * number_of_blocks
        self.mat_block = ["PMMA"] * number_of_blocks

    def create_load_intro_node(self, x_value, y_value, k):
        """doc"""
        k = np.where(
            np.logical_and(x_value < self.xbegin + self.dx_value[0] * 3, y_value > 0),
            3,
            k,
        )
        k = np.where(
            np.logical_and(x_value < self.xbegin + self.dx_value[0] * 3, y_value < 0),
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

            vol = np.zeros(len(x_value))
            k = np.ones(len(x_value))
            if self.rot:
                angle_x = np.zeros(len(x_value))
                angle_y = np.zeros(len(x_value))
                angle_z = np.zeros(len(x_value))

            k = self.create_block(y_value, k)
            k = self.create_load_intro_node(x_value, y_value, k)

            vol = np.full_like(
                x_value, self.dx_value[0] * self.dx_value[1] * self.dx_value[2]
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

        try:
            writer.create_file(block_def)
        except TypeError as exception:
            return str(exception)
        return 0
