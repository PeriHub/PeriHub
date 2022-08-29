"""
doc
"""
import time
import numpy as np

# import ast
from support.base_models import (
    Adapt,
    Block,
    BondFilters,
    BoundaryConditions,
    Contact,
    ContactModel,
    Compute,
    Damage,
    InterBlock,
    Interaction,
    Material,
    Output,
    Newton,
    Solver,
    Verlet,
)
from support.model_writer import ModelWriter
from support.geometry import Geometry

from support.globals import log

class GICmodel:

    bc1 = BoundaryConditions(
        id=1,
        name="BC_1",
        NodeSets=None,
        boundarytype="Body Force",
        blockId=4,
        coordinate="y",
        value="-10000*t",
    )
    bc2 = BoundaryConditions(
        id=2,
        name="BC_2",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=5,
        coordinate="y",
        value="0*t",
    )
    bc3 = BoundaryConditions(
        id=3,
        name="BC_3",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=6,
        coordinate="y",
        value="0*t",
    )
    bc4 = BoundaryConditions(
        id=4,
        name="BC_4",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=4,
        coordinate="x",
        value="0",
    )
    bc5 = BoundaryConditions(
        id=5,
        name="BC_5",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=5,
        coordinate="x",
        value="0",
    )
    bc6 = BoundaryConditions(
        id=6,
        name="BC_6",
        NodeSets=None,
        boundarytype="Prescribed Displacement",
        blockId=6,
        coordinate="x",
        value="0",
    )
    contact_model = ContactModel(
        id=1,
        name="Contact Model",
        contactType="Short Range Force",
        contactRadius=0.000775,
        springConstant=1.0e12,
    )
    interaction_1 = Interaction(firstBlockId=1, secondBlockId=2, contactModelId=1)
    # interaction_2 = Interaction(firstBlockId=4, secondBlockId=3, contactModelId=1)
    # interaction_3 = Interaction(firstBlockId=5, secondBlockId=3, contactModelId=1)
    # interaction_4 = Interaction(firstBlockId=6, secondBlockId=3, contactModelId=1)
    contact_dict = Contact(
        enabled=True,
        searchRadius=0.01,
        searchFrequency=100,
        contactModels=[contact_model],
        interactions=[interaction_1],
    )

    mat_dict = Material(
        id=1,
        name="IM7/8552",
        matType="Linear Elastic Correspondence",
        density=1570,
        bulkModulus=None,
        shearModulus=None,
        youngsModulus=1.520291e11,
        poissonsRatio=0.356,
        tensionSeparation=True,
        nonLinear=False,
        planeStress=True,
        materialSymmetry="Isotropic",
        stabilizatonType="Global Stiffness",
        thickness=10.0,
        hourglassCoefficient=1.0,
        actualHorizon=None,
        yieldStress=None,
        Parameter=[],
        properties=[],
        useCollocationNodes=False,
    )

    inter_block1 = InterBlock(
        firstBlockId=1,
        secondBlockId=2,
        value=0.01,
    )
    inter_block2 = InterBlock(
        firstBlockId=2,
        secondBlockId=1,
        value=0.01,
    )

    damage_dict = Damage(
        id=1,
        name="Damage",
        damageModel="Critical Energy Correspondence",
        criticalStretch=None,
        criticalEnergy=0.01,
        interBlockDamage=True,
        numberOfBlocks=6,
        interBlocks=[inter_block1, inter_block2],
        planeStress=True,
        onlyTension=False,
        detachedNodesCheck=True,
        thickness=10,
        hourglassCoefficient=1.0,
        stabilizatonType="Global Stiffness",
    )

    compute_dict_1 = Compute(
        id=1,
        name="Crosshead_Force",
        variable="Force",
        calculationType="Sum",
        blockName="block_4",
    )
    compute_dict_2 = Compute(
        id=2,
        name="Crosshead_Displacement",
        variable="Displacement",
        calculationType="Maximum",
        blockName="block_4",
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
        Write_After_Damage=True,
        Frequency=100,
        InitStep=0,
    )

    solver_dict = Solver(
        verbose=False,
        initialTime=0.0,
        finalTime=1.0,
        fixedDt=2.0e-05,
        solvertype="Verlet",
        safetyFactor=1.0,
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
        stopAfterDamageInitation=True,
        stopBeforeDamageInitation=False,
        adaptivetimeStepping=False,
        adapt=Adapt(),
        filetype="yaml",
    )

    def __init__(
        self,
        xend=1,
        crack_length=1,
        yend=1,
        zend=1,
        dx_value=None,
        filename="GICmodel",
        two_d=True,
        rot=False,
        angle=[0, 0],
        material=[mat_dict],
        damage=[damage_dict],
        block=None,
        contact=contact_dict,
        boundary_condition=[bc1, bc2, bc3],
        bond_filter=None,
        compute=[compute_dict_1, compute_dict_2],
        output=[output_dict1],
        solver=solver_dict,
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
        self.crack_length = crack_length
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

        number_of_blocks = 6

        """ Definition of model
        """

        self.damage_dict = damage
        self.block_def = block
        self.compute_dict = compute
        self.output_dict = output
        self.material_dict = material
        self.bondfilters = bond_filter
        self.contact_dict = contact
        self.bc_dict = boundary_condition
        self.solver_dict = solver

        self.contact_dict.searchRadius = self.dx_value[1] * 3
        self.contact_dict.contactModels[0].contactRadius = self.dx_value[1] * 0.95

        bf1 = BondFilters(
            id=1,
            name="bf_1",
            type="Rectangular_Plane",
            normalX=0.0,
            normalY=1.0,
            normalZ=0.0,
            lowerLeftCornerX=0.0,
            lowerLeftCornerY=self.yend / 2,
            lowerLeftCornerZ=-1.0,
            bottomUnitVectorX=1.0,
            bottomUnitVectorY=0.0,
            bottomUnitVectorZ=0.0,
            bottomLength=self.crack_length + 0.1,
            sideLength=self.zend + 2.0,
            centerX=0.0,
            centerY=1.0,
            centerZ=0.0,
            radius=1.0,
            show=True,
        )
        if not bond_filter:
            self.bondfilters = [bf1]
        else:
            bond_filter.append(bf1)
            self.bondfilters = bond_filter

        self.dam_block = [""] * number_of_blocks
        self.dam_block[0] = self.damage_dict[0].name
        self.dam_block[1] = self.damage_dict[0].name

        self.int_block_id = [""] * number_of_blocks
        self.int_block_id[0] = 2
        self.int_block_id[1] = 1
        self.mat_block = [self.material_dict[0].name] * number_of_blocks

        log.info(f"Initialized in {(time.time() - start_time):.2f} seconds")


    def create_block(self, y_value, k):
        k = np.where( y_value < self.yend / 2,
            1,
            k,
        )
        k = np.where( y_value >= self.yend / 2,
            2,
            k,
        )
        return k

    def create_bc_node(self, x_value, y_value, k):
        k = np.where(
            np.logical_and(
                x_value <= self.dx_value[0] * 5,
                y_value < self.dx_value[0] * 2
            ),
            3,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value <= self.dx_value[0] * 5,
                y_value >= self.yend - self.dx_value[0] * 2
            ),
            4,
            k,
        )
        return k

    def create_crack_node(self, x_value, y_value, k):
        k = np.where(
            np.logical_and(
                x_value < self.dx_value[0] * 1,
                np.logical_and(
                    y_value < self.yend / 2,
                    y_value >= self.yend / 2 - self.dx_value[0] * 1
                )
            ),
            5,
            k,
        )
        k = np.where(
            np.logical_and(
                x_value < self.dx_value[0] * 1,
                np.logical_and(
                    y_value >= self.yend / 2,
                    y_value < self.yend / 2 + self.dx_value[0] * 1
                )
            ),
            6,
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
        x_value1, y_value1, z_value1 = geo.create_rectangle(
            coor=[0, self.xend, 0, self.yend, 0, self.zend], dx_value=self.dx_value
        )
        # x_value2, y_value2, z_value2 = geo.create_cylinder(
        #     coor=[self.xend / 2, self.yend + 13.0, self.zend],
        #     dx_value=self.dx_value,
        #     radius=12.5,
        # )

        # condition = np.where(y_value2 <= self.yend + self.dx_value[0] * 5, 1.0, 0)

        # x_value2 = np.extract(condition, x_value2)
        # y_value2 = np.extract(condition, y_value2)
        # z_value2 = np.extract(condition, z_value2)

        # x_value3, y_value3, z_value3 = geo.create_cylinder(
        #     coor=[self.xend / 22, -5.1, self.zend], dx_value=self.dx_value, radius=5
        # )

        # condition = np.where(y_value3 >= -self.dx_value[0] * 5, 1.0, 0)

        # x_value3 = np.extract(condition, x_value3)
        # y_value3 = np.extract(condition, y_value3)
        # z_value3 = np.extract(condition, z_value3)

        # x_value4, y_value4, z_value4 = geo.create_cylinder(
        #     coor=[self.xend * 21 / 22, -5.1, self.zend],
        #     dx_value=self.dx_value,
        #     radius=5,
        # )

        # condition = np.where(y_value4 >= -self.dx_value[0] * 5, 1.0, 0)

        # x_value4 = np.extract(condition, x_value4)
        # y_value4 = np.extract(condition, y_value4)
        # z_value4 = np.extract(condition, z_value4)

        x_value = x_value1
        # x_value = np.concatenate((x_value, x_value2))
        # x_value = np.concatenate((x_value, x_value3))
        # x_value = np.concatenate((x_value, x_value4))
        y_value = y_value1
        # y_value = np.concatenate((y_value, y_value2))
        # y_value = np.concatenate((y_value, y_value3))
        # y_value = np.concatenate((y_value, y_value4))
        z_value = z_value1
        # z_value = np.concatenate((z_value, z_value2))
        # z_value = np.concatenate((z_value, z_value3))
        # z_value = np.concatenate((z_value, z_value4))

        if len(x_value) > self.max_nodes:
            return (
                "The number of nodes ("
                + str(len(x_value))
                + ") is larger than the allowed "
                + str(self.max_nodes)
            )

        if self.ignore_mesh and self.block_def != "" and self.block_def != None:

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

            # vol = np.zeros(len(x_value))
            # k = np.ones(len(x_value))
            if self.rot:
                angle_x = np.zeros(len(x_value))
                angle_y = np.zeros(len(x_value))
                angle_z = np.zeros(len(x_value))

            log.info(f"Angles assigned in {(time.time() - start_time):.2f} seconds")
            start_time = time.time()
            if self.rot:
                angle_x, angle_y, angle_z = self.create_angles(x_value, y_value)

            k = np.full_like(x_value1, 3)
            # k = np.concatenate((k, np.full_like(x_value2, 4)))
            # k = np.concatenate((k, np.full_like(x_value3, 5)))
            # k = np.concatenate((k, np.full_like(x_value4, 6)))

            # k = np.where(
            #     y_value >= self.yend / 2,
            #     self.create_load_block(x_value, y_value, k),
            #     self.create_boundary_condition_block(x_value, y_value, k),
            # )
            k = self.create_block(y_value, k)
            k = self.create_bc_node(x_value, y_value, k)
            k = self.create_crack_node(x_value, y_value, k)
            # k = self.create_load_intro_node(x_value, y_value, k)

            vol = np.full_like(
                x_value, self.dx_value[0] * self.dx_value[1] * self.dx_value[2]
            )

            log.info(f"BC and Blocks created in {(time.time() - start_time):.2f} seconds")

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

        if self.block_def == "" or self.block_def == None:
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
