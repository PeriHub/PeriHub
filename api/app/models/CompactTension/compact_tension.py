"""
doc
"""
import numpy as np
from support.base_models import (
    Adapt,
    Block,
    BondFilters,
    BoundaryCondition,
    BoundaryConditions,
    Compute,
    Contact,
    ContactModel,
    Damage,
    Interaction,
    Material,
    Newton,
    Output,
    Solver,
    Verlet,
)
from support.geometry import Geometry
from support.model_writer import ModelWriter


class CompactTension:
    bc1 = BoundaryCondition(
        conditionsId=1,
        name="BC_1",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=2,
        coordinate="y",
        value="1*t",
    )
    bc2 = BoundaryCondition(
        conditionsId=2,
        name="BC_2",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=3,
        coordinate="y",
        value="-1*t",
    )
    bc3 = BoundaryCondition(
        conditionsId=3,
        name="BC_3",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=2,
        coordinate="x",
        value="0",
    )
    bc4 = BoundaryCondition(
        conditionsId=4,
        name="BC_4",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=3,
        coordinate="z",
        value="0",
    )
    bc5 = BoundaryCondition(
        conditionsId=5,
        name="BC_5",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=2,
        coordinate="x",
        value="0",
    )
    bc6 = BoundaryCondition(
        conditionsId=6,
        name="BC_6",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=3,
        coordinate="z",
        value="0",
    )

    bf1 = BondFilters(
        id=1,
        name="bf_1",
        type="Rectangular_Plane",
        normalX=0.0,
        normalY=1.0,
        normalZ=0.0,
        lowerLeftCornerX=-0.5,
        lowerLeftCornerY=0,
        lowerLeftCornerZ=-0.5,
        bottomUnitVectorX=1.0,
        bottomUnitVectorY=0.0,
        bottomUnitVectorZ=0.0,
        bottomLength=25.5,
        sideLength=1.0,
        centerX=0.0,
        centerY=1.0,
        centerZ=0.0,
        radius=1.0,
        show=True,
    )
    contact_model = ContactModel(
        id=1,
        name="Contact Model",
        contactType="Short Range Force",
        contactRadius=0.000775,
        springConstant=1.0e12,
    )
    interaction_1 = Interaction(firstBlockId=4, secondBlockId=2, contactModelId=1)
    interaction_2 = Interaction(firstBlockId=5, secondBlockId=3, contactModelId=1)
    contact_dict = Contact(
        enabled=True,
        searchRadius=0.01,
        searchFrequency=100,
        contactModels=[contact_model],
        interactions=[interaction_1, interaction_2],
    )
    mat_dict = Material(
        id=1,
        name="Aluminum",
        matType="Linear Elastic Correspondence",
        density=2700,
        bulkModulus=None,
        shearModulus=None,
        youngsModulus=72400000000,
        poissonsRatio=0.33,
        tensionSeparation=True,
        nonLinear=False,
        planeStress=True,
        materialSymmetry="Isotropic",
        stabilizatonType="Global Stiffness",
        thickness=10.0,
        hourglassCoefficient=1.0,
        actualHorizon=None,
        yieldStress=None,
        Parameter=None,
        properties=None,
        useCollocationNodes=False,
    )

    damage_dict = Damage(
        id=1,
        name="Damage",
        damageModel="Critical Energy Correspondence",
        criticalStretch=None,
        criticalEnergy=1.0e6,
        interblockdamageEnergy=None,
        planeStress=True,
        onlyTension=True,
        detachedNodesCheck=True,
        thickness=10,
        hourglassCoefficient=1.0,
        stabilizatonType="Global Stiffness",
    )

    compute_dict = Compute(
        id=1,
        computeClass="Block_Data",
        name="External_Force",
        variable="Force",
        calculationType="Sum",
        blockName="block_3",
    )
    output_dict1 = Output(
        id=1,
        name="Output1",
        Displacement=True,
        Force=True,
        Damage=True,
        Velocity=True,
        Partial_Stress=True,
        Number_Of_Neighbors=True,
        Write_After_Damage=False,
        Frequency=15,
        InitStep=0,
    )

    solver_dict = Solver(
        verbose=False,
        initialTime=0.0,
        finalTime=0.1,
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
        xend=50,
        zend=0.003,
        crack_length=25,
        notch_enabled=True,
        dx_value=[0.25, 0.25, 0.25],
        filename="CompactTension",
        model_folder_name="",
        model_data=None,
        two_d=True,
        rot=False,
        angle=[0, 0],
        material=[mat_dict],
        damage=[damage_dict],
        block=None,
        boundary_condition=BoundaryConditions(conditions=[bc1, bc2]),
        contact=contact_dict,
        bond_filter=[bf1],
        compute=[compute_dict],
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
        self.model_folder_name = model_folder_name
        self.scal = 4.01
        self.disc_type = "txt"
        self.mesh_file = None
        self.two_d = two_d
        self.ns_list = [3, 4]
        if not dx_value:
            dx_value = [0.001, 0.001, 0.001]
        self.dx_value = dx_value
        if not angle:
            angle = [0, 0]
        self.angle = angle
        self.length = xend
        self.xbegin = 0.0
        self.ybegin = -0.6 * xend
        self.xend = 1.25 * xend
        self.yend = 0.6 * xend
        # self.xend = xend
        # self.yend = yend/2
        # self.zend = zend
        self.rot = rot
        self.block_def = block
        self.username = username
        self.max_nodes = max_nodes
        self.ignore_mesh = ignore_mesh
        self.notch_enabled = notch_enabled
        if self.two_d:
            self.zbegin = 0
            self.zend = 0
            self.dx_value[2] = 1
        else:
            self.zbegin = -zend / 2
            self.zend = zend / 2

        number_of_blocks = 5

        """ Definition of model
        """
        self.damage_dict = damage
        self.block_def = block
        self.compute_dict = compute
        self.output_dict = output
        self.material_dict = material
        bond_filter[0].bottomLength = crack_length + 0.5 + 0.25 * self.length
        bond_filter[0].sideLength = self.zend + 2.0
        bond_filter[0].lowerLeftCornerZ = (-self.zend / 2) - 1
        self.bondfilters = bond_filter
        self.contact_dict = contact
        self.bc_dict = boundary_condition
        self.solver_dict = solver
        self.model_data = model_data

        self.dam_block = [""] * number_of_blocks
        self.dam_block[0] = self.damage_dict[0].name

        self.int_block_id = [""] * number_of_blocks
        self.mat_block = [self.material_dict[0].name] * number_of_blocks

    def create_load_intro_node(self, x_value, y_value, k):
        """doc"""
        k = np.where(
            np.logical_and(
                np.logical_and(
                    x_value <= 0.45 * self.length,
                    x_value >= 0,
                ),
                y_value >= 0,
            ),
            4,
            k,
        )
        k = np.where(
            np.logical_and(
                np.logical_and(
                    x_value <= 0.45 * self.length,
                    x_value >= 0,
                ),
                y_value <= 0,
            ),
            5,
            k,
        )
        condition = np.where(
            ((x_value - 0.25 * self.length) ** 2)
            + ((y_value - 0.275 * self.length) ** 2)
            <= (0.125 * self.length) ** 2,
            1.0,
            0,
        )
        k = np.where(
            condition,
            2,
            k,
        )
        condition = np.where(
            ((x_value - 0.25 * self.length) ** 2)
            + ((y_value + 0.275 * self.length) ** 2)
            <= (0.125 * self.length) ** 2,
            1.0,
            0,
        )
        k = np.where(
            condition,
            3,
            k,
        )
        # k = np.where(
        #     np.logical_and(
        #         np.logical_and(
        #             x_value <= 0.25 * self.length + 3 * self.dx_value[0],
        #             x_value >= 0.25 * self.length - 3 * self.dx_value[0],
        #         ),
        #         np.logical_and(
        #             y_value <= 0.275 * self.length + 3 * self.dx_value[1],
        #             y_value >= 0.275 * self.length - 3 * self.dx_value[1],
        #         ),
        #     ),
        #     2,
        #     k,
        # )
        # k = np.where(
        #     np.logical_and(
        #         np.logical_and(
        #             x_value <= 0.25 * self.length + 3 * self.dx_value[0],
        #             x_value >= 0.25 * self.length - 3 * self.dx_value[0],
        #         ),
        #         np.logical_and(
        #             y_value <= -0.275 * self.length + 3 * self.dx_value[1],
        #             y_value >= -0.275 * self.length - 3 * self.dx_value[1],
        #         ),
        #     ),
        #     3,
        #     k,
        # )
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

        if self.notch_enabled:
            x_value, y_value, z_value = geo.check_val_in_notch(
                x_value,
                y_value,
                z_value,
                0.0,
                self.xend,
                0.45 * self.length,
                1.6,
                self.dx_value[0],
                60,
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
