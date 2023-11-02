# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
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
    def __init__(
        self,
        model_data,
        filename="Smetana",
        model_folder_name="",
        mesh_res=30,
        xend=4.0,
        plyThickness=0.125,
        zend=1.5,
        dx_value=[0.1, 0.1, 0.1],
        username="",
        ignore_mesh=False,
        amplitude_factor=0.75,
        wavelength=3.0,
        angle=[45, 90, -45, 0],
        two_d=True,
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
        self.software = model_data.job.software
        self.amplitude_factor = amplitude_factor
        self.wavelength = wavelength
        self.angle = angle
        self.two_d = two_d
        self.path = "/app/Output/" + os.path.join(username, filename + model_folder_name)

        self.bc_dict = model_data.model.boundaryConditions
        self.damage_dict = model_data.model.damages
        self.compute_dict = model_data.model.computes
        self.output_dict = model_data.model.outputs
        self.contact_dict = model_data.model.contact
        self.solver_dict = model_data.model.solver

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
            "software": self.software,
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
