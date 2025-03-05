# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""
import numpy as np

from ..support.model.geometry import Geometry
from ..support.model.material import MaterialRoutines

# import ast
from ..support.writer.model_writer import ModelWriter


class VerificationModels:
    def __init__(self):
        # https://wiki.dlr.de/display/PDWiki/Tests
        self.scal = 3.01
        self.length = 0.021
        self.height = 0.002
        self.thickness = 0.001
        self.young = 7e10
        self.poisson = 0.3
        self.dx_value = [0.00005, 0.00005, 0.00005]
        self.amp = "0.005*(-x/" + str(self.length) + "+ 1)"
        self.block_def = ""
        self.compute_dict = {}

        self.damage_dict = ""

        self.bondfilters = {"name": []}
        self.solver_dict = {}
        self.two_d = True

        self.output_dict = [{}] * 1
        self.output_dict[0] = {
            "name": "Output1",
            "Displacement": True,
            "Force": True,
            "Damage": False,
            "Partial_Stress": True,
            "External_Force": False,
            "External_Displacement": False,
            "Number_Of_Neighbors": False,
            "Frequency": 500,
            "InitStep": 0,
        }

        mat_name_list = ["isoMatOne", "isoMatTwo", "anisoMat"]
        self.material_dict = [{}] * len(mat_name_list)
        i = 0
        for material in mat_name_list:
            self.material_dict[i] = {
                "name": material,
                "matType": ["Correspondence Elastic"],
                "youngsModulus": 2.1e11,
                "poissonsRatio": 0.3,
                "tensionSeparation": False,
                "materialSymmetry": "Anisotropic",
                "stabilizationType": "Global Stiffness",
                "thickness": 10.0,
                "hourglassCoefficient": 1.0,
            }
            i += 1
        params = [270000, 7e10, 0.3, 0, 0]
        mat = MaterialRoutines()
        self.material_dict[0]["stiffnessMatrix"]["matrix"] = mat.stiffness_matrix(
            mat_type="isotropic", mat_param=params
        )
        params = [270000, 2.1e11, 0.3, 0, 0]
        self.material_dict[1]["stiffnessMatrix"]["matrix"] = mat.stiffness_matrix(
            mat_type="isotropic", mat_param=params
        )
        self.angle = [0, 0]
        params = [
            195000,  # dens
            165863e6,  # C11
            4090e6,  # C12
            2471e6,  # C13
            0.0,  # C14
            0.0,  # C15
            0.0,  # C16
            9217e6,  # C22
            2471e6,  # C23
            0.0,  # C24
            0.0,  # C25
            0.0,  # C26
            9217e6,  # C33
            0.0,  # C34
            0.0,  # C35
            0.0,  # C36
            3360e6,  # C44
            0.0,  # C45
            0.0,  # C46
            4200e6,  # C55
            0.0,  # C56
            4200e6,
        ]  # C66
        self.material_dict[2]["stiffnessMatrix"]["matrix"] = mat.stiffness_matrix(
            mat_type="anisotropic", mat_param=params
        )
        self.bc_dict = [
            {
                "name": "BC_1",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 3,
                "coordinate": "x",
                "value": str(self.amp) + "*t",
            },
            {
                "name": "BC_2",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 4,
                "coordinate": "x",
                "value": str(self.amp) + "*t",
            },
            {
                "name": "BC_3",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 5,
                "coordinate": "x",
                "value": "0",
            },
            {
                "name": "BC_4",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "x",
                "value": "0",
            },
            {
                "name": "BC_5",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 5,
                "coordinate": "y",
                "value": "0",
            },
            {
                "name": "BC_6",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "y",
                "value": "0",
            },
        ]
        # {'name': 'BC_5', 'boundarytype': 'Prescribed Displacement', 'blockId': 7, 'coordinate': 'x', 'value': '0'},
        # {'name': 'BC_6', 'boundarytype': 'Prescribed Displacement', 'blockId': 7, 'coordinate': 'y', 'value': '0'}]

        self.solver_dict = {
            "verbose": False,
            "initialTime": 0.0,
            "finalTime": 0.002,
            "solvertype": "NOXQuasiStatic",
            "relativeTolerance": 1e-5,
            "NumberOfLoadSteps": 1000,
            "safetyFactor": 0.5,
            "numericalDamping": 0.00005,
        }

    def create_verification_models(self):
        self.dx_value[1] = self.avoid_middle_node(self.height, self.dx_value[1])
        self.dx_value[0] = self.dx_value[1]
        self.dx_value[2] = self.dx_value[1]
        self.bc_dict[0]["coordinate"] = "x"
        self.bc_dict[1]["coordinate"] = "x"
        self.mat_block = [
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
        ]

        self.call_modelbuilder(two_d=True, angle=[0, 0], filename="isoTension2D")

        self.bc_dict.append(
            {
                "name": "BC_7",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "z",
                "value": "0",
            }
        )
        self.call_modelbuilder(two_d=False, angle=[0, 0], filename="isoTension3D")
        del self.bc_dict[-1]
        self.mat_block = [
            "isoMatOne",
            "isoMatTwo",
            "isoMatOne",
            "isoMatTwo",
            "isoMatOne",
            "isoMatTwo",
            "isoMatOne",
        ]
        self.call_modelbuilder(two_d=True, angle=[0, 0], filename="twoLayerIsoTension2D")
        self.bc_dict.append(
            {
                "name": "BC_7",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "z",
                "value": "0",
            }
        )
        self.call_modelbuilder(two_d=False, angle=[0, 0], filename="twoLayerIsoTension3D")
        self.bc_dict[0]["coordinate"] = "y"
        self.bc_dict[1]["coordinate"] = "y"
        self.mat_block = [
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
            "isoMatOne",
        ]
        del self.bc_dict[-1]
        self.call_modelbuilder(two_d=True, angle=[0, 0], filename="isoBending2D")
        self.bc_dict.append(
            {
                "name": "BC_7",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "z",
                "value": "0",
            }
        )
        self.call_modelbuilder(two_d=False, angle=[0, 0], filename="isoBending3D")
        self.mat_block = [
            "isoMatOne",
            "isoMatTwo",
            "isoMatOne",
            "isoMatTwo",
            "isoMatOne",
            "isoMatTwo",
            "isoMatOne",
        ]
        del self.bc_dict[-1]
        self.call_modelbuilder(two_d=True, angle=[0, 0], filename="twoLayerIsoBending2D")
        self.bc_dict.append(
            {
                "name": "BC_7",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "z",
                "value": "0",
            }
        )
        self.call_modelbuilder(two_d=False, angle=[0, 0], filename="twoLayerIsoBending3D")
        self.mat_block = [
            "anisoMat",
            "anisoMat",
            "anisoMat",
            "anisoMat",
            "anisoMat",
            "anisoMat",
            "anisoMat",
        ]
        self.bc_dict[0]["coordinate"] = "x"
        self.bc_dict[1]["coordinate"] = "x"
        del self.bc_dict[-1]
        self.call_modelbuilder(
            two_d=True,
            angle=[90, 90],
            filename="twoLayerAniso090Tension2D",
        )
        self.bc_dict.append(
            {
                "name": "BC_7",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "z",
                "value": "0",
            }
        )
        self.call_modelbuilder(
            two_d=False,
            angle=[0, 90],
            filename="twoLayerAniso090Tension3D",
        )
        del self.bc_dict[-1]
        self.call_modelbuilder(
            two_d=True,
            angle=[30, -30],
            filename="twoLayerAniso30m30Tension2D",
        )
        self.bc_dict.append(
            {
                "name": "BC_7",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "z",
                "value": "0",
            }
        )
        self.call_modelbuilder(
            two_d=False,
            angle=[30, -30],
            filename="twoLayerAniso30m30Tension3D",
        )
        self.bc_dict[0]["coordinate"] = "y"
        self.bc_dict[1]["coordinate"] = "y"
        # fehlt noch was
        del self.bc_dict[-1]
        self.call_modelbuilder(
            two_d=True,
            angle=[0, 90],
            filename="twoLayerAniso090Bending2D",
        )
        self.bc_dict.append(
            {
                "name": "BC_7",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "z",
                "value": "0",
            }
        )
        self.call_modelbuilder(
            two_d=False,
            angle=[9, 90],
            filename="twoLayerAniso090Bending3D",
        )
        del self.bc_dict[-1]
        self.call_modelbuilder(
            two_d=True,
            angle=[30, -30],
            filename="twoLayerAniso30m30Bending2D",
        )
        self.bc_dict.append(
            {
                "name": "BC_7",
                "boundarytype": "Dirichlet",
                "variable": "Displacements",
                "blockId": 6,
                "coordinate": "z",
                "value": "0",
            }
        )
        self.call_modelbuilder(
            two_d=False,
            angle=[30, -30],
            filename="twoLayerAniso30m30Bending3D",
        )

    def call_modelbuilder(self, two_d=True, angle=None, filename="isoTension"):
        self.filename = filename
        self.angle = angle
        self.two_d = two_d
        self.create_model(
            two_d=two_d,
            xend=self.length,
            yend=self.height,
            zend=self.thickness,
            dx_value=self.dx_value,
            angle=self.angle,
        )

    @staticmethod
    def avoid_middle_node(yend, dx_value):
        discretization = int(yend / dx_value)
        if not discretization % 2:
            discretization += 1
        dx_value = yend / discretization
        return dx_value

    def create_blocks(self, x_value, y_value, k):
        if x_value < 0.0:
            if y_value > self.height / 2:
                k = 3
            elif y_value < self.height / 2:
                k = 4
        elif x_value > self.length:
            if y_value > self.height / 2:
                k = 5
            elif y_value < self.height / 2:
                k = 6

            # if z_value==0
            # tbd
        elif y_value > self.height / 2:
            k = 1
        elif y_value < self.height / 2:
            k = 2
        return k

    def create_angles(self, y_value, angle):
        if y_value < self.height / 2:
            angle_y = angle[0]
        else:
            angle_y = angle[1]

        return angle_y

    def create_model(self, two_d, xend, yend, zend, dx_value, angle=None):
        geo = Geometry()
        rot = True
        if angle[0] == angle[1] and angle[1] == 0:
            rot = False

        if two_d:
            x_value, y_value, z_value = geo.create_rectangle(
                coor=[
                    -3 * dx_value[0],
                    xend + 3 * dx_value[0],
                    0,
                    yend,
                    0,
                    0,
                ],
                dx_value=[dx_value[0], dx_value[1], 1],
            )
        else:
            x_value, y_value, z_value = geo.create_rectangle(
                coor=[
                    -3 * dx_value[0],
                    xend + 3 * dx_value[0],
                    0,
                    yend,
                    0,
                    zend,
                ],
                dx_value=[dx_value[0], dx_value[1], dx_value[2]],
            )

        vol = np.zeros(len(x_value))
        k = np.ones(len(x_value))
        if rot:
            angle_x = np.zeros(len(x_value))
            angle_y = np.zeros(len(x_value))
            angle_z = np.zeros(len(x_value))
        for idx in enumerate(x_value):
            k[idx] = self.create_blocks(x_value[idx], y_value[idx], k[idx])

            if rot:
                angle_y[idx] = self.create_angles(y_value[idx], angle=angle)

            vol[idx] = dx_value[0] * dx_value[1] * dx_value[2]
            if two_d:
                vol[idx] = dx_value[0] * dx_value[1]
        writer = ModelWriter(model_class=self)

        if rot:
            model = {
                "x": x_value,
                "y": y_value,
                "z": z_value,
                "k": k,
                "vol": vol,
                "angle_x": angle_x,
                "angle_y": angle_y,
                "angle_z": angle_z,
            }
            writer.write_mesh_with_angles(model, self.two_d)
        else:
            model = {
                "x": x_value,
                "y": y_value,
                "z": z_value,
                "k": k,
                "vol": vol,
            }
            writer.write_mesh(model, self.two_d)
        writer.write_node_sets(model)
        self.write_file(writer=writer, model=model)

        return model

    def create_blockdef(self, model):
        block_len = int(max(model["k"]))
        block_def = [{}] * block_len
        if self.damage_dict == "":
            for idx in range(0, block_len):
                block_def[idx] = {
                    "name": "block_" + str(idx + 1),
                    "material": self.mat_block[idx],
                    "horizon": self.scal * max([self.dx_value[0], self.dx_value[1]]),
                    "damageModel": "",
                }
        else:
            for idx in range(0, block_len):
                block_def[idx] = {
                    "name": "block_" + str(idx + 1),
                    "material": self.mat_block[idx],
                    "horizon": self.scal * max([self.dx_value[0], self.dx_value[1]]),
                    "damageModel": self.damage_dict[idx],
                }
        # 3d tbd
        return block_def

    def write_file(self, writer, model):
        if self.block_def == "":
            block_def = self.create_blockdef(model)
        else:
            for _, block in enumerate(self.block_def):
                block["horizon"] = self.scal * max([self.dx_value[0], self.dx_value[1]])
            block_def = self.block_def

        writer.create_file(block_def)
