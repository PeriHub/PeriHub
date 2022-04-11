"""
doc
"""
import numpy as np
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
from support.geometry import Geometry


class KalthoffWinkler:

    bc1 = BoundaryConditions(
        id=1,
        Name="BC_1",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=2,
        coordinate="x",
        value="0*t",
    )
    bc2 = BoundaryConditions(
        id=2,
        Name="BC_2",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=3,
        coordinate="x",
        value="0*t",
    )
    bc3 = BoundaryConditions(
        id=3,
        Name="BC_3",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=4,
        coordinate="x",
        value="10*t",
    )
    mat_dict = Material(
        id=1,
        Name="PMMA",
        MatType="Elastic Bond Based",
        density=8.0e-6,
        bulkModulus=1.2666666666666667e5,
        shearModulus=None,
        youngsModulus=None,
        poissonsRatio=None,
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
        Properties=[],
        useCollocationNodes=True,
    )

    damage_dict = Damage(
        id=1,
        Name="PMMADamage",
        damageModel="Critical Stretch",
        criticalStretch=0.012358773175687088,
        criticalEnergy=0.0022170,
        interblockdamageEnergy=0.01,
        planeStress=True,
        onlyTension=False,
        detachedNodesCheck=True,
        thickness=10,
        hourglassCoefficient=1.0,
        stabilizatonType="Global Stiffness",
    )

    bf1 = BondFilters(
        id=1,
        Name="bf_1",
        type="Rectangular_Plane",
        normalX=0.0,
        normalY=1.0,
        normalZ=0.0,
        lowerLeftCornerX=-0.5,
        lowerLeftCornerY=25.125,
        lowerLeftCornerZ=-0.5,
        bottomUnitVectorX=1.0,
        bottomUnitVectorY=0.0,
        bottomUnitVectorZ=0.0,
        bottomLength=50.5,
        sideLength=1.0,
        centerX=0.0,
        centerY=1.0,
        centerZ=0.0,
        radius=1.0,
        show=True,
    )
    bf2 = BondFilters(
        id=1,
        Name="bf_2",
        type="Rectangular_Plane",
        normalX=0.0,
        normalY=1.0,
        normalZ=0.0,
        lowerLeftCornerX=-0.5,
        lowerLeftCornerY=-25.125,
        lowerLeftCornerZ=-0.5,
        bottomUnitVectorX=1.0,
        bottomUnitVectorY=0.0,
        bottomUnitVectorZ=0.0,
        bottomLength=50.5,
        sideLength=1.0,
        centerX=0.0,
        centerY=1.0,
        centerZ=0.0,
        radius=1.0,
        show=True,
    )

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
        Number_Of_Neighbors=True,
        Frequency=1,
        InitStep=0,
    )
    solver_dict = Solver(
        verbose=False,
        initialTime=0.0,
        finalTime=0.03,
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

    def __init__(
        self,
        xend=100,
        yend=100,
        zend=0.003,
        dx_value=[0.25, 0.25, 0.25],
        filename="Kalthoff-Winkler",
        two_d=False,
        rot=False,
        angle=[0, 0],
        material=[mat_dict],
        damage=[damage_dict],
        block=None,
        boundary_condition=[bc1, bc2, bc3],
        bond_filter=[bf1, bf2],
        compute=[compute_dict1, compute_dict2],
        output=[output_dict1],
        solver=solver_dict,
        username="",
        max_nodes=10000000,
        ignore_mesh=False,
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
        self.xbegin = 0.0
        self.ybegin = -yend / 2
        self.xend = xend + dx_value[0]
        self.yend = yend / 2 + dx_value[1]
        # self.xend = xend
        # self.yend = yend/2
        # self.zend = zend
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
        self.damage_dict = damage
        self.block_def = block
        self.compute_dict = compute
        self.output_dict = output
        self.material_dict = material
        self.bondfilters = bond_filter
        self.bc_dict = boundary_condition
        self.solver_dict = solver

        self.dam_block = [""] * number_of_blocks
        self.dam_block[0] = self.damage_dict[0].Name
        self.dam_block[1] = self.damage_dict[0].Name
        self.dam_block[2] = self.damage_dict[0].Name
        self.dam_block[3] = self.damage_dict[0].Name

        self.int_block_id = [""] * number_of_blocks
        self.mat_block = [self.material_dict[0].Name] * number_of_blocks

    def create_boundary_condition_block(self, x_value, y_value, k):
        k = np.where(
            np.logical_and(
                x_value > self.xend - self.dx_value[0] * 3,
                np.logical_and(
                    y_value < 90 + self.dx_value[0] * 3,
                    y_value > 90 - self.dx_value[0] * 3,
                ),
            ),
            2,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value > self.xend - self.dx_value[0] * 3,
                np.logical_and(
                    y_value < -90 + self.dx_value[0] * 3,
                    y_value > -90 - self.dx_value[0] * 3,
                ),
            ),
            3,
            k,
        )
        return k

    def create_load_intro_node(self, x_value, y_value, k):
        """doc"""
        k = np.where(
            np.logical_and(
                x_value < self.dx_value[0] * 3,
                np.logical_and(y_value <= 25, y_value >= -25),
            ),
            4,
            k,
        )
        return k

    def create_model(self):
        """doc"""

        geo = Geometry()

        x_value, y_value, z_value = geo.create_points(
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

            k = self.create_boundary_condition_block(x_value, y_value, k)
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
