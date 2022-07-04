"""
doc
"""
import os
import numpy as np
# import smetana
try:
    from smetana.control.peridigmcontrol import PeridigmControl
except ImportError:
    pass
from support.base_models import (
    Adapt,
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
        filename="Smetana",
        damage=[damage_dict],
        contact=contact_dict,
        compute=[compute_dict],
        output=[output_dict1],
        solver=solver_dict,
        username="",
        ignore_mesh=False,
        mesh_res=30,
        ):
        self.filename = filename
        self.username = username
        self.ignore_mesh = ignore_mesh
        self.mesh_res = mesh_res
        self.path = "Output/" + os.path.join(username, filename)

        self.damage_dict = damage
        self.compute_dict = compute
        self.output_dict = output
        self.contact_dict = contact
        self.solver_dict = solver

    def create_model(self):

        """doc"""
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        PeridigmControl.generateModel(self.filename, self.path, self.mesh_res, True, self.damage_dict, self.contact_dict, self.compute_dict, self.output_dict, self.solver_dict)
        
        return "Model created"