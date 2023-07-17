# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import io
import os
import zipfile

import requests

# import smetana
from support.base_models import (
    Adapt,
    BoundaryCondition,
    BoundaryConditions,
    Compute,
    Contact,
    ContactModel,
    Damage,
    Interaction,
    Newton,
    Output,
    SmetanaData,
    Solver,
    Verlet,
)
from support.globals import log


class Smetana:
    bc1 = BoundaryCondition(
        conditionsId=1,
        name="BC_1",
        nodeSet=None,
        boundarytype="Prescribed Displacement",
        blockId=1,
        coordinate="x",
        value="3*t",
    )

    bc2 = BoundaryCondition(
        conditionsId=2,
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
        stabilizationType="Global Stiffness",
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
        model_folder_name="",
        mesh_res=30,
        xend=4.0,
        plyThickness=0.125,
        zend=1.5,
        dx_value=[0.1, 0.1, 0.1],
        damage=[damage_dict],
        contact=contact_dict,
        boundary_condition=BoundaryConditions(conditions=[bc1, bc2]),
        compute=[compute_dict],
        output=[output_dict1],
        solver=solver_dict,
        username="",
        ignore_mesh=False,
        amplitude_factor=0.75,
        wavelength=3.0,
        angle=[45, 90, -45, 0],
        two_d=True,
        model_data=None,
    ):
        self.filename = filename
        self.model_folder_name = model_folder_name
        self.mesh_res = mesh_res
        self.xend = xend
        self.plyThickness = plyThickness
        self.zend = zend
        self.dx_value = dx_value
        self.username = username
        self.ignore_mesh = ignore_mesh
        self.amplitude_factor = amplitude_factor
        self.wavelength = wavelength
        self.angle = angle
        self.two_d = two_d
        self.path = "/app/Output/" + os.path.join(username, filename + model_folder_name)

        self.bc_dict = boundary_condition
        self.damage_dict = damage
        self.compute_dict = compute
        self.output_dict = output
        self.contact_dict = contact
        self.solver_dict = solver
        self.model_data = model_data

    def create_model(self):
        """doc"""
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        prop_params = {
            "filename": self.filename,
            "username": self.username,
            "meshResolution": self.mesh_res,
            "xlength": self.xend,
            "plyThickness": self.plyThickness,
            "yLength": self.zend,
            "use_perihub": True,
            "amplitudeFactor": self.amplitude_factor,
            "wavelength": self.wavelength,
            "ignore_mesh": self.ignore_mesh,
        }

        data_params = SmetanaData(
            dx_value=self.dx_value,
            angleList=self.angle,
            damage=self.damage_dict,
            contact=self.contact_dict,
            boundary_condition=self.bc_dict,
            compute=self.compute_dict,
            output=self.output_dict,
            solver=self.solver_dict,
        )

        if self.two_d:
            url = "https://smetana-api.nimbus.dlr.de/generatePeridigm2DModel"

        else:
            url = "https://smetana-api.nimbus.dlr.de/generatePeridigm3DModel"

        response = requests.post(url, params=prop_params, data=data_params.json())
        log.info(response.text)

        prop_params = {
            "filename": self.filename,
            "username": self.username,
        }

        url = "https://smetana-api.nimbus.dlr.de/getModel"

        request = requests.get(url, params=prop_params)

        try:
            with zipfile.ZipFile(io.BytesIO(request.content)) as zip_file:
                localpath = "./Output/" + os.path.join(self.username, self.filename)

                if not os.path.exists(localpath):
                    os.makedirs(localpath)

                zip_file.extractall(localpath)

        except IOError:
            log.error("Smetana request failed")
            return "Smetana request failed"

        return "Model created"
