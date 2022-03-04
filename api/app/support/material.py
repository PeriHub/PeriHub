"""
Created on 13.12.2013
Routines taken from
@author: hein_fa
edited by @author will_cr
"""
import numpy as np
from support.base_models import Parameter

# from support.transformations import rotation_matrix


class MaterialRoutines:
    def __init__(self, angle=None):
        self.angle = angle

    def stiffnessMatrix(self, mat_type, matParam=None):
        parameter = {}
        if mat_type == "anisotropic":
            parameter = self.anisotropic(parameter, matParam)
        # def isotropic(self, parameter, E, nu, K, G):
        #     if E !=0: parameter["Young's Modulus"] ={'value': E}
        #     if nu !=0: parameter["Poisson's Ratio"] = {'value':nu}
        #     if K !=0: parameter["Bulk Modulus"] = {'value':K}
        #     if G !=0: parameter["Shear Modulus"] = {'value':G}
        return parameter

    @staticmethod
    def anisotropic(parameter, matParam):
        # CTensor = self.createStiffnessTensor()
        # CTensor = self.rotateStiffnessTensor(self.alpha, self.beta, self.gamma)
        # parameter = self.obtainTensorComponents()
        parameter = []

        parameter.append(Parameter(Name="C11", value=matParam[0]))
        parameter.append(Parameter(Name="C12", value=matParam[1]))
        parameter.append(Parameter(Name="C13", value=matParam[2]))
        parameter.append(Parameter(Name="C14", value=matParam[3]))
        parameter.append(Parameter(Name="C15", value=matParam[4]))
        parameter.append(Parameter(Name="C16", value=matParam[5]))
        parameter.append(Parameter(Name="C22", value=matParam[6]))
        parameter.append(Parameter(Name="C23", value=matParam[7]))
        parameter.append(Parameter(Name="C24", value=matParam[8]))
        parameter.append(Parameter(Name="C25", value=matParam[9]))
        parameter.append(Parameter(Name="C26", value=matParam[10]))
        parameter.append(Parameter(Name="C33", value=matParam[11]))
        parameter.append(Parameter(Name="C34", value=matParam[12]))
        parameter.append(Parameter(Name="C35", value=matParam[13]))
        parameter.append(Parameter(Name="C36", value=matParam[14]))
        parameter.append(Parameter(Name="C44", value=matParam[15]))
        parameter.append(Parameter(Name="C45", value=matParam[16]))
        parameter.append(Parameter(Name="C46", value=matParam[17]))
        parameter.append(Parameter(Name="C55", value=matParam[18]))
        parameter.append(Parameter(Name="C56", value=matParam[19]))
        parameter.append(Parameter(Name="C66", value=matParam[20]))
        return parameter

    def get_transformation_matrix_from_angle(
        self, angle, transformation_type="epsilon", rotationAxis="z"
    ):
        """This method returns the transformation matrix for epsilon for the specified rotation angle.
        For more information refer to:
        .. [Alt1996] Einfuehrung in die Mechanik der Laminat- und Sandwichtragwerke:
        Modellierung und Berechnung von Balken und Platten aus Verbundwerkstoffen,  pages 29f.

        .. attention::

        The right order of the specified tensor components is important.
        ['s11', 's22', 's33', 's23', 's13', 's12']"""

        rot = np.identity(3, dtype=np.float64)
        if rotationAxis == "x":
            rot = rotation_matrix(angle, [1.0, 0.0, 0.0])
        elif rotationAxis == "y":
            rot = rotation_matrix(angle, [0.0, 1.0, 0.0])
        elif rotationAxis == "z":
            rot = rotation_matrix(angle, [0.0, 0.0, 1.0])

        return self.get_transformation_matrix_from_matrix(rot.T, transformation_type)

    @staticmethod
    def get_transformation_matrix_from_matrix(
        rotation_matrix, transformation_type="epsilon"
    ):
        """This method returns the transformation matrix for epsilon for the specified rotation matrix.
        For more information refer to:
        .. [Alt1996] Einfuehrung in die Mechanik der Laminat- und Sandwichtragwerke:
        Modellierung und Berechnung von Balken und Platten aus Verbundwerkstoffen,  pages 29f.

        .. attention::

        The right order of the specified tensor components is important.
        ['s11', 's22', 's33', 's23', 's13', 's12']"""
        rM = rotation_matrix
        maskArray = np.array(
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
                        rM[0, 0] ** 2,
                        rM[0, 1] ** 2,
                        rM[0, 2] ** 2,
                        rM[0, 1] * rM[0, 2],
                        rM[0, 0] * rM[0, 2],
                        rM[0, 0] * rM[0, 1],
                    ],
                    [
                        rM[1, 0] ** 2,
                        rM[1, 1] ** 2,
                        rM[1, 2] ** 2,
                        rM[1, 1] * rM[1, 2],
                        rM[1, 0] * rM[1, 2],
                        rM[1, 0] * rM[1, 1],
                    ],
                    [
                        rM[2, 0] ** 2,
                        rM[2, 1] ** 2,
                        rM[2, 2] ** 2,
                        rM[2, 1] * rM[2, 2],
                        rM[2, 0] * rM[2, 2],
                        rM[2, 0] * rM[2, 1],
                    ],
                    [
                        2.0 * rM[1, 0] * rM[2, 0],
                        2.0 * rM[1, 1] * rM[2, 1],
                        2.0 * rM[1, 2] * rM[2, 2],
                        rM[1, 1] * rM[2, 2] + rM[1, 2] * rM[2, 1],
                        rM[1, 0] * rM[2, 2] + rM[1, 2] * rM[2, 0],
                        rM[1, 0] * rM[2, 1] + rM[1, 1] * rM[2, 0],
                    ],
                    [
                        2.0 * rM[0, 0] * rM[2, 0],
                        2.0 * rM[0, 1] * rM[2, 1],
                        2.0 * rM[0, 2] * rM[2, 2],
                        rM[0, 1] * rM[2, 2] + rM[0, 2] * rM[2, 1],
                        rM[0, 0] * rM[2, 2] + rM[0, 2] * rM[2, 0],
                        rM[0, 0] * rM[2, 1] + rM[0, 1] * rM[2, 0],
                    ],
                    [
                        2.0 * rM[0, 0] * rM[1, 0],
                        2.0 * rM[0, 1] * rM[1, 1],
                        2.0 * rM[0, 2] * rM[1, 2],
                        rM[0, 1] * rM[1, 2] + rM[0, 2] * rM[1, 1],
                        rM[0, 0] * rM[1, 2] + rM[0, 2] * rM[1, 0],
                        rM[0, 0] * rM[1, 1] + rM[0, 1] * rM[1, 0],
                    ],
                ]
            )
        elif transformation_type == "sigma":
            # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
            # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
            trafo2 = np.array(
                [
                    [
                        rM[0, 0] ** 2,
                        rM[0, 1] ** 2,
                        rM[0, 2] ** 2,
                        2.0 * rM[0, 1] * rM[0, 2],
                        2.0 * rM[0, 0] * rM[0, 2],
                        2.0 * rM[0, 0] * rM[0, 1],
                    ],
                    [
                        rM[1, 0] ** 2,
                        rM[1, 1] ** 2,
                        rM[1, 2] ** 2,
                        2.0 * rM[1, 1] * rM[1, 2],
                        2.0 * rM[1, 0] * rM[1, 2],
                        2.0 * rM[1, 0] * rM[1, 1],
                    ],
                    [
                        rM[2, 0] ** 2,
                        rM[2, 1] ** 2,
                        rM[2, 2] ** 2,
                        2.0 * rM[2, 1] * rM[2, 2],
                        2.0 * rM[2, 0] * rM[2, 2],
                        2.0 * rM[2, 0] * rM[2, 1],
                    ],
                    [
                        rM[1, 0] * rM[2, 0],
                        rM[1, 1] * rM[2, 1],
                        rM[1, 2] * rM[2, 2],
                        rM[1, 1] * rM[2, 2] + rM[1, 2] * rM[2, 1],
                        rM[1, 0] * rM[2, 2] + rM[1, 2] * rM[2, 0],
                        rM[1, 0] * rM[2, 1] + rM[1, 1] * rM[2, 0],
                    ],
                    [
                        rM[0, 0] * rM[2, 0],
                        rM[0, 1] * rM[2, 1],
                        rM[0, 2] * rM[2, 2],
                        rM[0, 1] * rM[2, 2] + rM[0, 2] * rM[2, 1],
                        rM[0, 0] * rM[2, 2] + rM[0, 2] * rM[2, 0],
                        rM[0, 0] * rM[2, 1] + rM[0, 1] * rM[2, 0],
                    ],
                    [
                        rM[0, 0] * rM[1, 0],
                        rM[0, 1] * rM[1, 1],
                        rM[0, 2] * rM[1, 2],
                        rM[0, 1] * rM[1, 2] + rM[0, 2] * rM[1, 1],
                        rM[0, 0] * rM[1, 2] + rM[0, 2] * rM[1, 0],
                        rM[0, 0] * rM[1, 1] + rM[0, 1] * rM[1, 0],
                    ],
                ]
            )

        trafo1 = np.reshape(trafo2[maskArray], (3, 3))
        return trafo1, trafo2

    def transformStiffnessMatrixByAngle(
        self, inputArray, angle, localToGlobal=True, rotationAxis="z"
    ):
        """This method is intended to transform the provided array (2-D)
        according to the specified angle into a new coordinate system."""
        inputArray = np.asarray(inputArray)
        if localToGlobal:
            # CONVERT LOCAL REDUCED STIFFNESS INTO GLOBAL REDUCED STIFFNESS - TRANSFORMATION FOR EPSILON
            if inputArray.shape == (3, 3):
                trafo = self.get_transformation_matrix_from_angle(
                    angle, "epsilon", rotationAxis
                )[0]

            # CONVERT LOCAL STIFFNESS INTO GLOBAL STIFFNESS - TRANSFORMATION FOR EPSILON
            elif inputArray.shape == (6, 6):
                trafo = self.get_transformation_matrix_from_angle(
                    angle, "epsilon", rotationAxis
                )[1]

            return np.dot(trafo.T, np.dot(inputArray, trafo))

        # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
        if inputArray.shape == (3, 3):
            trafo = self.get_transformation_matrix_from_angle(
                angle, "sigma", rotationAxis
            )[0]

        # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
        if inputArray.shape == (6, 6):
            trafo = self.get_transformation_matrix_from_angle(
                angle, "sigma", rotationAxis
            )[1]

        return np.dot(trafo, np.dot(inputArray, trafo.T))

    def transformStiffnessMatrixByMatrix(
        self, inputArray, rotation_matrix, localToGlobal=True
    ):
        """This method is intended to transform the provided array (2-D)
        according to the specified rotation matrix into a new coordinate system."""
        inputArray = np.asarray(inputArray)
        if localToGlobal:
            # CONVERT LOCAL REDUCED STIFFNESS INTO GLOBAL REDUCED STIFFNESS - TRANSFORMATION FOR EPSILON
            if inputArray.shape == (3, 3):
                trafo = self.get_transformation_matrix_from_matrix(
                    rotation_matrix, "epsilon"
                )[0]

            # CONVERT LOCAL STIFFNESS INTO GLOBAL STIFFNESS - TRANSFORMATION FOR EPSILON
            elif inputArray.shape == (6, 6):
                trafo = self.get_transformation_matrix_from_matrix(
                    rotation_matrix, "epsilon"
                )[1]

            return np.dot(trafo.T, np.dot(inputArray, trafo))

        # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
        if inputArray.shape == (3, 3):
            trafo = self.get_transformation_matrix_from_matrix(
                rotation_matrix, "sigma"
            )[0]

        # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
        if inputArray.shape == (6, 6):
            trafo = self.get_transformation_matrix_from_matrix(
                rotation_matrix, "sigma"
            )[1]

        return np.dot(trafo, np.dot(inputArray, trafo.T))
