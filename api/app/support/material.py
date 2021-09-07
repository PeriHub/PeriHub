import numpy as np

'''
Created on 13.12.2013
Routines taken from
@author: hein_fa
edited by @author will_cr
'''
class MaterialRoutines(object):
    def __init__(self, angle = [0]):
        self.angle = angle
    
    def stiffnessMatrix(self,type, matParam = [0]):
        parameter = {'Density': {'value': matParam[0]}}
        if type == 'isotropic':parameter = self.isotropic(parameter, matParam[1], matParam[2], matParam[3], matParam[4])
        if type == 'anisotropic': parameter = self.anisotropic(parameter,matParam)
        return parameter
    def isotropic(self, parameter, E, nu, K, G):
        if E !=0: parameter["Young's Modulus"] = E
        if nu !=0: parameter["Poisson's Ratio"] = nu
        if K !=0: parameter["Bulk Modulus"] = K
        if G !=0: parameter["Shear Modulus"] = G
        return parameter
    def anisotropic(self, parameter, matParam):
        #CTensor = self.createStiffnessTensor()
        #CTensor = self.rotateStiffnessTensor(self.alpha, self.beta, self.gamma)
        #parameter = self.obtainTensorComponents()
        parameter["C11"] = {'value': matParam[1]} 
        parameter["C12"] = {'value': matParam[2]}
        parameter["C13"] = {'value': matParam[3]}
        parameter["C14"] = {'value': matParam[4]}
        parameter["C15"] = {'value': matParam[5]}
        parameter["C16"] = {'value': matParam[6]}
        parameter["C22"] = {'value': matParam[7]}
        parameter["C23"] = {'value': matParam[8]}
        parameter["C24"] = {'value': matParam[9]}
        parameter["C25"] = {'value': matParam[10]}
        parameter["C26"] = {'value': matParam[11]}
        parameter["C33"] = {'value': matParam[12]}
        parameter["C34"] = {'value': matParam[13]}
        parameter["C35"] = {'value': matParam[14]}
        parameter["C36"] = {'value': matParam[15]}
        parameter["C44"] = {'value': matParam[16]}
        parameter["C45"] = {'value': matParam[17]}
        parameter["C46"] = {'value': matParam[18]}
        parameter["C55"] = {'value': matParam[19]}
        parameter["C56"] = {'value': matParam[20]}
        parameter["C66"] = {'value': matParam[21]}
        return parameter

    def getTransformationMatrixFromAngle(self,angle, transformationType = 'epsilon', rotationAxis = 'z'):
        """This method returns the transformation matrix for epsilon for the specified rotation angle.        
        For more information refer to:
        .. [Alt1996] Einfuehrung in die Mechanik der Laminat- und Sandwichtragwerke: Modellierung und Berechnung von Balken und Platten aus Verbundwerkstoffen,  pages 29f.
        
        .. attention::
            
        The right order of the specified tensor components is important.
        ['s11', 's22', 's33', 's23', 's13', 's12']"""
        from support.transformations import rotation_matrix
        rot = np.identity(3, dtype=np.float64)
        if rotationAxis == 'x':
            rot = rotation_matrix(angle,[1.,0.,0.])
        elif rotationAxis == 'y':
            rot = rotation_matrix(angle,[0.,1.,0.])
        elif rotationAxis == 'z':
            rot = rotation_matrix(angle,[0.,0.,1.])

        return self.getTransformationMatrixFromMatrix(rot.T, transformationType)


    def getTransformationMatrixFromMatrix(self,rotationMatrix, transformationType = 'epsilon'):
        """This method returns the transformation matrix for epsilon for the specified rotation matrix.        
        For more information refer to:
        .. [Alt1996] Einfuehrung in die Mechanik der Laminat- und Sandwichtragwerke: Modellierung und Berechnung von Balken und Platten aus Verbundwerkstoffen,  pages 29f.
        
        .. attention::
            
        The right order of the specified tensor components is important.
        ['s11', 's22', 's33', 's23', 's13', 's12']"""
        rM = rotationMatrix
        maskArray = np.array([[ True , True , False, False, False, True  ],
                            [ True , True , False, False, False, True  ],
                            [ False, False, False, False, False, False ],
                            [ False, False, False, False, False, False ],
                            [ False, False, False, False, False, False ],
                            [ True , True , False, False, False, True  ],
                            ])

        if transformationType == 'epsilon':
            # CONVERT LOCAL REDUCED STIFFNESS INTO GLOBAL REDUCED STIFFNESS - TRANSFORMATION FOR EPSILON
            # CONVERT LOCAL STIFFNESS INTO GLOBAL STIFFNESS - TRANSFORMATION FOR EPSILON
            trafo2 = np.array([[ rM[0,0]**2        , rM[0,1]**2        , rM[0,2]**2        , rM[0,1]*rM[0,2]                , rM[0,0]*rM[0,2]                , rM[0,0]*rM[0,1]                 ],
                            [ rM[1,0]**2        , rM[1,1]**2        , rM[1,2]**2        , rM[1,1]*rM[1,2]                , rM[1,0]*rM[1,2]                , rM[1,0]*rM[1,1]                 ],
                            [ rM[2,0]**2        , rM[2,1]**2        , rM[2,2]**2        , rM[2,1]*rM[2,2]                , rM[2,0]*rM[2,2]                , rM[2,0]*rM[2,1]                 ],
                            [ 2.*rM[1,0]*rM[2,0], 2.*rM[1,1]*rM[2,1], 2.*rM[1,2]*rM[2,2], rM[1,1]*rM[2,2]+rM[1,2]*rM[2,1], rM[1,0]*rM[2,2]+rM[1,2]*rM[2,0], rM[1,0]*rM[2,1]+rM[1,1]*rM[2,0] ],
                            [ 2.*rM[0,0]*rM[2,0], 2.*rM[0,1]*rM[2,1], 2.*rM[0,2]*rM[2,2], rM[0,1]*rM[2,2]+rM[0,2]*rM[2,1], rM[0,0]*rM[2,2]+rM[0,2]*rM[2,0], rM[0,0]*rM[2,1]+rM[0,1]*rM[2,0] ],
                            [ 2.*rM[0,0]*rM[1,0], 2.*rM[0,1]*rM[1,1], 2.*rM[0,2]*rM[1,2], rM[0,1]*rM[1,2]+rM[0,2]*rM[1,1], rM[0,0]*rM[1,2]+rM[0,2]*rM[1,0], rM[0,0]*rM[1,1]+rM[0,1]*rM[1,0] ],
                            ])
        elif transformationType == 'sigma':
            # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
            # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
            trafo2 = np.array([[ rM[0,0]**2     , rM[0,1]**2     , rM[0,2]**2     , 2.*rM[0,1]*rM[0,2]             , 2.*rM[0,0]*rM[0,2]             , 2.*rM[0,0]*rM[0,1]              ],
                            [ rM[1,0]**2     , rM[1,1]**2     , rM[1,2]**2     , 2.*rM[1,1]*rM[1,2]             , 2.*rM[1,0]*rM[1,2]             , 2.*rM[1,0]*rM[1,1]              ],
                            [ rM[2,0]**2     , rM[2,1]**2     , rM[2,2]**2     , 2.*rM[2,1]*rM[2,2]             , 2.*rM[2,0]*rM[2,2]             , 2.*rM[2,0]*rM[2,1]              ],
                            [ rM[1,0]*rM[2,0], rM[1,1]*rM[2,1], rM[1,2]*rM[2,2], rM[1,1]*rM[2,2]+rM[1,2]*rM[2,1], rM[1,0]*rM[2,2]+rM[1,2]*rM[2,0], rM[1,0]*rM[2,1]+rM[1,1]*rM[2,0] ],
                            [ rM[0,0]*rM[2,0], rM[0,1]*rM[2,1], rM[0,2]*rM[2,2], rM[0,1]*rM[2,2]+rM[0,2]*rM[2,1], rM[0,0]*rM[2,2]+rM[0,2]*rM[2,0], rM[0,0]*rM[2,1]+rM[0,1]*rM[2,0] ],
                            [ rM[0,0]*rM[1,0], rM[0,1]*rM[1,1], rM[0,2]*rM[1,2], rM[0,1]*rM[1,2]+rM[0,2]*rM[1,1], rM[0,0]*rM[1,2]+rM[0,2]*rM[1,0], rM[0,0]*rM[1,1]+rM[0,1]*rM[1,0] ],
                            ])

        trafo1 = np.reshape(trafo2[maskArray], (3,3))
        return trafo1, trafo2


    def transformStiffnessMatrixByAngle(self,inputArray, angle, localToGlobal = True, rotationAxis = 'z'):
        """This method is intended to transform the provided array (2-D) according to the specified angle into a new coordinate system."""
        inputArray = np.asarray(inputArray)
        if localToGlobal:
            # CONVERT LOCAL REDUCED STIFFNESS INTO GLOBAL REDUCED STIFFNESS - TRANSFORMATION FOR EPSILON
            if inputArray.shape == (3, 3):
                trafo = self.getTransformationMatrixFromAngle(angle, 'epsilon', rotationAxis)[0]
        
            # CONVERT LOCAL STIFFNESS INTO GLOBAL STIFFNESS - TRANSFORMATION FOR EPSILON
            elif inputArray.shape == (6, 6):
                trafo = self.getTransformationMatrixFromAngle(angle, 'epsilon', rotationAxis)[1]

            return np.dot(trafo.T,np.dot(inputArray,trafo))
        
        else:
            # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
            if inputArray.shape == (3, 3):
                trafo = self.getTransformationMatrixFromAngle(angle, 'sigma', rotationAxis)[0]

            # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
            if inputArray.shape == (6, 6):
                trafo = self.getTransformationMatrixFromAngle(angle, 'sigma', rotationAxis)[1]

            return np.dot(trafo,np.dot(inputArray,trafo.T))


    def transformStiffnessMatrixByMatrix(self,inputArray, rotationMatrix, localToGlobal = True):
        """This method is intended to transform the provided array (2-D) according to the specified rotation matrix into a new coordinate system."""
        inputArray = np.asarray(inputArray)
        if localToGlobal:
            # CONVERT LOCAL REDUCED STIFFNESS INTO GLOBAL REDUCED STIFFNESS - TRANSFORMATION FOR EPSILON
            if inputArray.shape == (3, 3):
                trafo = self.getTransformationMatrixFromMatrix(rotationMatrix, 'epsilon')[0]
        
            # CONVERT LOCAL STIFFNESS INTO GLOBAL STIFFNESS - TRANSFORMATION FOR EPSILON
            elif inputArray.shape == (6, 6):
                trafo = self.getTransformationMatrixFromMatrix(rotationMatrix, 'epsilon')[1]
    
            return np.dot(trafo.T,np.dot(inputArray,trafo))
        
        else:
            # CONVERT GLOBAL REDUCED STIFFNESS INTO LOCAL REDUCED STIFFNESS - TRANSFORMATION FOR SIGMA
            if inputArray.shape == (3, 3):
                trafo = self.getTransformationMatrixFromMatrix(rotationMatrix, 'sigma')[0]
    
            # CONVERT GLOBAL STIFFNESS INTO LOCAL STIFFNESS - TRANSFORMATION FOR SIGMA
            if inputArray.shape == (6, 6):
                trafo = self.getTransformationMatrixFromMatrix(rotationMatrix, 'sigma')[1]
    
            return np.dot(trafo,np.dot(inputArray,trafo.T))
