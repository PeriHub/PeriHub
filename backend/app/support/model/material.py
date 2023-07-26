# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
Created on 13.12.2013
Routines taken from
@author: hein_fa
edited by @author will_cr
"""
import numpy as np

from support.base_models import Matrix

# from support.transformations import rotation_matrix


class MaterialRoutines:
    def __init__(self, angle=None):
        self.angle = angle

    def stiffness_matrix(self, mat_type, mat_param=None):
        if mat_type == "anisotropic":
            matrix = self.anisotropic(mat_param)
        # def isotropic(self, parameter, E, nu, K, G):
        #     if E !=0: parameter["Young's Modulus"] ={'value': E}
        #     if nu !=0: parameter["Poisson's Ratio"] = {'value':nu}
        #     if K !=0: parameter["Bulk Modulus"] = {'value':K}
        #     if G !=0: parameter["Shear Modulus"] = {'value':G}
        return matrix

    @staticmethod
    def anisotropic(mat_param):
        # CTensor = self.createStiffnessTensor()
        # CTensor = self.rotateStiffnessTensor(self.alpha, self.beta, self.gamma)
        # parameter = self.obtainTensorComponents()

        matrix = Matrix(
            C11=mat_param[0],
            C12=mat_param[1],
            C13=mat_param[2],
            C14=mat_param[3],
            C15=mat_param[4],
            C16=mat_param[5],
            C22=mat_param[6],
            C23=mat_param[7],
            C24=mat_param[8],
            C25=mat_param[9],
            C26=mat_param[10],
            C33=mat_param[11],
            C34=mat_param[12],
            C35=mat_param[13],
            C36=mat_param[14],
            C44=mat_param[15],
            C45=mat_param[16],
            C46=mat_param[17],
            C55=mat_param[18],
            C56=mat_param[19],
            C66=mat_param[20],
        )
        return matrix

    # def get_transformation_matrix_from_angle(
    #     self, angle, transformation_type="epsilon", rotationAxis="z"
    # ):
    #     """This method returns the transformation matrix for epsilon for the specified rotation angle.
    #     For more information refer to:
    #     .. [Alt1996] Einfuehrung in die Mechanik der Laminat- und Sandwichtragwerke:
    #     Modellierung und Berechnung von Balken und Platten aus Verbundwerkstoffen,  pages 29f.

    #     .. attention::

    #     The right order of the specified tensor components is important.
    #     ['s11', 's22', 's33', 's23', 's13', 's12']"""

    #     rot = np.identity(3, dtype=np.float64)
    #     if rotationAxis == "x":
    #         rot = rotation_matrix(angle, [1.0, 0.0, 0.0])
    #     elif rotationAxis == "y":
    #         rot = rotation_matrix(angle, [0.0, 1.0, 0.0])
    #     elif rotationAxis == "z":
    #         rot = rotation_matrix(angle, [0.0, 0.0, 1.0])

    #     return self.get_transformation_matrix_from_matrix(rot.T, transformation_type)

    @staticmethod
    def get_transformation_matrix_from_matrix(rotation_matrix, transformation_type="epsilon"):
        """This method returns the transformation matrix for epsilon for the specified rotation matrix.
        For more information refer to:
        .. [Alt1996] Einfuehrung in die Mechanik der Laminat- und Sandwichtragwerke:
        Modellierung und Berechnung von Balken und Platten aus Verbundwerkstoffen,  pages 29f.

        .. attention::

        The right order of the specified tensor components is important.
        ['s11', 's22', 's33', 's23', 's13', 's12']"""
        rot_m = rotation_matrix
        mask_array = np.array(
            [
                [True, True, False, False, False, True],
                [True, True, False, False, False, True],
                [False, False, False, False, False, False],
                [False, False, False, False, False, False],
                [False, False, False, False, False, False],
                [True, True, False, False, False, True],
            ]
        )

        if transformation_type == "epsilon":
            # CONVERT LOCAL REDUCED STIFFNESS INTO GLOBAL REDUCED STIFFNESS - TRANSFORMATION FOR EPSILON
            # CONVERT LOCAL STIFFNESS INTO GLOBAL STIFFNESS - TRANSFORMATION FOR EPSILON
            trafo2 = np.array(
                [
                    [
                        rot_m[0, 0] ** 2,
                        rot_m[0, 1] ** 2,
                        rot_m[0, 2] ** 2,
                        rot_m[0, 1] * rot_m[0, 2],
                        rot_m[0, 0] * rot_m[0, 2],
                        rot_m[0, 0] * rot_m[0, 1],
                    ],
                    [
                        rot_m[1, 0] ** 2,
                        rot_m[1, 1] ** 2,
                        rot_m[1, 2] ** 2,
                        rot_m[1, 1] * rot_m[1, 2],
                        rot_m[1, 0] * rot_m[1, 2],
                        rot_m[1, 0] * rot_m[1, 1],
                    ],
                    [
                        rot_m[2, 0] ** 2,
                        rot_m[2, 1] ** 2,
                        rot_m[2, 2] ** 2,
                        rot_m[2, 1] * rot_m[2, 2],
                        rot_m[2, 0] * rot_m[2, 2],
                        rot_m[2, 0] * rot_m[2, 1],
                    ],
                    [
                        2.0 * rot_m[1, 0] * rot_m[2, 0],
                        2.0 * rot_m[1, 1] * rot_m[2, 1],
                        2.0 * rot_m[1, 2] * rot_m[2, 2],
                        rot_m[1, 1] * rot_m[2, 2] + rot_m[1, 2] * rot_m[2, 1],
                        rot_m[1, 0] * rot_m[2, 2] + rot_m[1, 2] * rot_m[2, 0],
                        rot_m[1, 0] * rot_m[2, 1] + rot_m[1, 1] * rot_m[2, 0],
                    ],
                    [
                        2.0 * rot_m[0, 0] * rot_m[2, 0],
                        2.0 * rot_m[0, 1] * rot_m[2, 1],
                        2.0 * rot_m[0, 2] * rot_m[2, 2],
                        rot_m[0, 1] * rot_m[2, 2] + rot_m[0, 2] * rot_m[2, 1],
                        rot_m[0, 0] * rot_m[2, 2] + rot_m[0, 2] * rot_m[2, 0],
                        rot_m[0, 0] * rot_m[2, 1] + rot_m[0, 1] * rot_m[2, 0],
                    ],
                    [
                        2.0 * rot_m[0, 0] * rot_m[1, 0],
                        2.0 * rot_m[0, 1] * rot_m[1, 1],
                        2.0 * rot_m[0, 2] * rot_m[1, 2],
                        rot_m[0, 1] * rot_m[1, 2] + rot_m[0, 2] * rot_m[1, 1],
                        rot_m[0, 0] * rot_m[1, 2] + rot_m[0, 2] * rot_m[1, 0],
                        rot_m[0, 0] * rot_m[1, 1] + rot_m[0, 1] * rot_m[1, 0],
                    ],
                ]
            )
        elif transformation_type == "sigma":
            # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
            # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
            trafo2 = np.array(
                [
                    [
                        rot_m[0, 0] ** 2,
                        rot_m[0, 1] ** 2,
                        rot_m[0, 2] ** 2,
                        2.0 * rot_m[0, 1] * rot_m[0, 2],
                        2.0 * rot_m[0, 0] * rot_m[0, 2],
                        2.0 * rot_m[0, 0] * rot_m[0, 1],
                    ],
                    [
                        rot_m[1, 0] ** 2,
                        rot_m[1, 1] ** 2,
                        rot_m[1, 2] ** 2,
                        2.0 * rot_m[1, 1] * rot_m[1, 2],
                        2.0 * rot_m[1, 0] * rot_m[1, 2],
                        2.0 * rot_m[1, 0] * rot_m[1, 1],
                    ],
                    [
                        rot_m[2, 0] ** 2,
                        rot_m[2, 1] ** 2,
                        rot_m[2, 2] ** 2,
                        2.0 * rot_m[2, 1] * rot_m[2, 2],
                        2.0 * rot_m[2, 0] * rot_m[2, 2],
                        2.0 * rot_m[2, 0] * rot_m[2, 1],
                    ],
                    [
                        rot_m[1, 0] * rot_m[2, 0],
                        rot_m[1, 1] * rot_m[2, 1],
                        rot_m[1, 2] * rot_m[2, 2],
                        rot_m[1, 1] * rot_m[2, 2] + rot_m[1, 2] * rot_m[2, 1],
                        rot_m[1, 0] * rot_m[2, 2] + rot_m[1, 2] * rot_m[2, 0],
                        rot_m[1, 0] * rot_m[2, 1] + rot_m[1, 1] * rot_m[2, 0],
                    ],
                    [
                        rot_m[0, 0] * rot_m[2, 0],
                        rot_m[0, 1] * rot_m[2, 1],
                        rot_m[0, 2] * rot_m[2, 2],
                        rot_m[0, 1] * rot_m[2, 2] + rot_m[0, 2] * rot_m[2, 1],
                        rot_m[0, 0] * rot_m[2, 2] + rot_m[0, 2] * rot_m[2, 0],
                        rot_m[0, 0] * rot_m[2, 1] + rot_m[0, 1] * rot_m[2, 0],
                    ],
                    [
                        rot_m[0, 0] * rot_m[1, 0],
                        rot_m[0, 1] * rot_m[1, 1],
                        rot_m[0, 2] * rot_m[1, 2],
                        rot_m[0, 1] * rot_m[1, 2] + rot_m[0, 2] * rot_m[1, 1],
                        rot_m[0, 0] * rot_m[1, 2] + rot_m[0, 2] * rot_m[1, 0],
                        rot_m[0, 0] * rot_m[1, 1] + rot_m[0, 1] * rot_m[1, 0],
                    ],
                ]
            )

        trafo1 = np.reshape(trafo2[mask_array], (3, 3))
        return trafo1, trafo2

    # def transformStiffnessMatrixByAngle(
    #     self, input_array, angle, local_to_global=True, rotationAxis="z"
    # ):
    #     """This method is intended to transform the provided array (2-D)
    #     according to the specified angle into a new coordinate system."""
    #     input_array = np.asarray(input_array)
    #     if local_to_global:
    #         # CONVERT LOCAL REDUCED STIFFNESS INTO GLOBAL REDUCED STIFFNESS - TRANSFORMATION FOR EPSILON
    #         if input_array.shape == (3, 3):
    #             trafo = self.get_transformation_matrix_from_angle(
    #                 angle, "epsilon", rotationAxis
    #             )[0]

    #         # CONVERT LOCAL STIFFNESS INTO GLOBAL STIFFNESS - TRANSFORMATION FOR EPSILON
    #         elif input_array.shape == (6, 6):
    #             trafo = self.get_transformation_matrix_from_angle(
    #                 angle, "epsilon", rotationAxis
    #             )[1]

    #         return np.dot(trafo.T, np.dot(input_array, trafo))

    #     # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
    #     if input_array.shape == (3, 3):
    #         trafo = self.get_transformation_matrix_from_angle(
    #             angle, "sigma", rotationAxis
    #         )[0]

    #     # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
    #     if input_array.shape == (6, 6):
    #         trafo = self.get_transformation_matrix_from_angle(
    #             angle, "sigma", rotationAxis
    #         )[1]

    #     return np.dot(trafo, np.dot(input_array, trafo.T))

    # def transform_stiffness_matrix_by_matrix(
    #     self, input_array, rotation_matrix, local_to_global=True
    # ):
    #     """This method is intended to transform the provided array (2-D)
    #     according to the specified rotation matrix into a new coordinate system."""
    #     input_array = np.asarray(input_array)
    #     if local_to_global:
    #         # CONVERT LOCAL REDUCED STIFFNESS INTO GLOBAL REDUCED STIFFNESS - TRANSFORMATION FOR EPSILON
    #         if input_array.shape == (3, 3):
    #             trafo = self.get_transformation_matrix_from_matrix(
    #                 rotation_matrix, "epsilon"
    #             )[0]

    #         # CONVERT LOCAL STIFFNESS INTO GLOBAL STIFFNESS - TRANSFORMATION FOR EPSILON
    #         elif input_array.shape == (6, 6):
    #             trafo = self.get_transformation_matrix_from_matrix(
    #                 rotation_matrix, "epsilon"
    #             )[1]

    #         return np.dot(trafo.T, np.dot(input_array, trafo))

    #     # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
    #     if input_array.shape == (3, 3):
    #         trafo = self.get_transformation_matrix_from_matrix(
    #             rotation_matrix, "sigma"
    #         )[0]

    #     # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
    #     if input_array.shape == (6, 6):
    #         trafo = self.get_transformation_matrix_from_matrix(
    #             rotation_matrix, "sigma"
    #         )[1]

    #     return np.dot(trafo, np.dot(input_array, trafo.T))
