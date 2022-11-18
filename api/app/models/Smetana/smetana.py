"""
doc
"""
import os
import numpy as np
# import smetana
try:
    from smetana.control.peridigmcontrol import PeridigmControl
    from smetana.control.peridigmcontrol3D import PeridigmControl3D
except ImportError:
    pass
from support.base_models import (
    Adapt,
    BoundaryConditions,
    Contact,
    ContactModel,
    Compute,
    Damage,
    Interaction,
    Output,
    Newton,
    Solver,
    Verlet,
)
from support.model_writer import ModelWriter
from support.geometry import Geometry


class Smetana:

    bc1 = BoundaryConditions(
        id=1,
        name="BC_1",
        nodeSet=None,
        boundarytype="Prescribed Displacement",
        blockId=1,
        coordinate="x",
        value="3*t",
    )

    bc2 = BoundaryConditions(
        id=2,
        name="BC_2",
        nodeSet=None,
        boundarytype="Prescribed Displacement",
        blockId=4,
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
    
    interaction_1 = Interaction(firstBlockId=4, secondBlockId=2, contactModelId=1)
    interaction_2 = Interaction(firstBlockId=5, secondBlockId=3, contactModelId=1)
    contact_dict = Contact(
        enabled=False,
        searchRadius=0.01,
        searchFrequency=100,
        contactModels=[contact_model],
        interactions=[interaction_1, interaction_2],
    )

    damage_dict = Damage(
        id=1,
        name="dam_1",
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
        finalTime=0.002,
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
        filename="Smetana",
        mesh_res=30,
        xend=4.0,
        plyThickness=0.125,
        zend=1.5,
        dx_value=[0.1,0.1,0.1],
        damage=[damage_dict],
        contact=contact_dict,
        boundary_condition=[bc1, bc2],
        compute=[compute_dict],
        output=[output_dict1],
        solver=solver_dict,
        username="",
        ignore_mesh=False,
        amplitude_factor=0.75,
        wavelength=3.0,
        angle=[45, 90, -45, 0],
        two_d=True,
        ):

        self.filename = filename
        self.mesh_res = mesh_res
        self.xend=xend
        self.plyThickness=plyThickness
        self.zend=zend
        self.dx_value=dx_value
        self.username = username
        self.ignore_mesh = ignore_mesh
        self.amplitude_factor = amplitude_factor
        self.wavelength = wavelength
        self.angle = angle
        self.two_d = two_d
        self.path = "Output/" + os.path.join(username, filename)

        self.bc_dict = boundary_condition
        self.damage_dict = damage
        self.compute_dict = compute
        self.output_dict = output
        self.contact_dict = contact
        self.solver_dict = solver

    def create_model(self):

        """doc"""
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if self.two_d:
            PeridigmControl.generateModel(self.filename, self.path, self.mesh_res, self.xend, self.plyThickness, self.zend, self.dx_value, True, self.amplitude_factor, self.wavelength, self.angle, self.damage_dict, self.contact_dict, self.bc_dict, self.compute_dict, self.output_dict, self.solver_dict, self.ignore_mesh)
        else:
            PeridigmControl3D.generateModel(self.filename, self.path, self.mesh_res, self.xend, self.plyThickness, self.zend, self.dx_value, True, self.amplitude_factor, self.wavelength, self.angle, self.damage_dict, self.contact_dict, self.bc_dict, self.compute_dict, self.output_dict, self.solver_dict, self.ignore_mesh)
        return "Model created"