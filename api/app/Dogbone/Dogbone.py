import sys
import numpy as np
from scipy import interpolate
from support.modelWriter import ModelWriter
from support.material import MaterialRoutines
from support.geometry import Geometry

class Dogbone(object):
    def __init__(self, xend = 18, yend = 2, zend = 0.4, dx=[0.2,0.2,0.2], 
    filename = 'Dogbone', TwoD = False, rot = 'False', angle = [0,0], 
    material = '', damage = '', block = '', bc = '', compute = '', output = '', solver = ''):
        '''
            definition der blocks
            k =
            1 basisplatte
            2 Z Zero Node Set
            3 Min Y Up Node Set
            4 Min Y Down Node Set
        '''
        self.a
        self.b
        self.c
        self.length = 2*a+c
        self.filename = filename
        self.scal = 4.01
        self.TwoD = TwoD
        self.nsList = [3,4]
        self.dx   = dx
        self.xbegin = -xend/2 - dx[0]
        self.ybegin = -yend/2 - dx[1]
        self.zbegin = -zend/2 - dx[2]
        self.xend = xend/2 + dx[0]
        self.yend = yend/2 + dx[1]
        self.zend = zend/2 + dx[2]
        self.rot = rot
        self.blockDef = block
        if self.TwoD:
            self.zbegin = 0
            self.zend = 0
            self.dx[2] = 1
        numberOfBlocks = 4
        # xbound = [0, 4*dx[0],5*dx[0], xend-5*dx[0],xend-4*dx[0],xend + dx[0]]
        # ybound = [0, 4*dx[1],5*dx[1], yend + dx[1]]

        # z = [2,2,1,1,3,3]
        # self.boundfuncx = interpolate.interp1d(xbound,z, kind='linear')
        # z = [1,1,0,0]
        # self.boundfuncy = interpolate.interp1d(ybound,z, kind='linear')
        # xload = [0, xend/2-2*dx[0],xend/2+2*dx[0], xend + dx[0]]
        # z = [1,4,4,1]
        # self.loadfuncx = interpolate.interp1d(xload,z, kind='linear')
        # yload = [0, yend-5*dx[1],yend-4*dx[1], yend + dx[1]]
        # z = [1,1,4,4]
        # self.loadfuncy = interpolate.interp1d(yload,z, kind='linear')
        
        # z = [1,1,8,8,9,9,1,1]
        # yblock = [0,yend/2-5*dx[1],yend/2-4*dx[1],yend/2-dx[1]/4,yend/2+dx[1]/4, yend/2+4*dx[1],yend/2+5*dx[1], yend+dx[1]]

        # self.blockfuny = interpolate.interp1d(yblock,z, kind='linear')
        ''' Definition of model
        '''
        mat = MaterialRoutines()
        isotropic = True
        matNameList = ['PMMA']
        self.materialDict = [{}]
        self.damageDict = [{}]
        self.computeDict = [{},{}]
        self.outputDict = [{},{}]
        self.angle = [0,0]
        if damage=='':
            self.damageDict = {'PMMADamage':{'Energy':5.1, 'InferaceEnergy':0.01}}
        else:
            self.damageDict = damage
        
        if compute=='':
            self.computeDict[0] = {'Name':'External_Displacement','variable':'Displacement', 'calculationType':'Minimum','blockName':'block_3'},
            self.computeDict[1] = {'Name':'External_Force','variable':'Force', 'calculationType':'Sum','blockName':'block_3'}
        else:
            self.computeDict = compute
       
        if output=='':
            self.outputDict[0] = {'Name': 'Output1', 'Displacement': True, 'Force': True, 'Damage': True, 'Partial_Stress': False, 'External_Force': False, 'External_Displacement': False, 'Number_Of_Neighbors': False, 'Frequency': 500, 'InitStep': 0}
            self.outputDict[1] = {'Name': 'Output2', 'Displacement': False, 'Force': False, 'Damage': True, 'Partial_Stress': True, 'External_Force': True, 'External_Displacement': True, 'Number_Of_Neighbors': False, 'Frequency': 200, 'InitStep': 0}
        else:
            self.outputDict = output
        
        if material=='':
            i=0
            for material in matNameList:
                self.materialDict[i] = {'Name': material, 'MatType':'Linear Elastic Correspondence', 'youngsModulus': 210000.0, 'poissonsRatio': 0.3, 'tensionSeparation': False, 'materialSymmetry': 'Anisotropic', 'stabilizatonType': 'Global Stiffness', 'thickness': 10.0, 'hourglassCoefficient': 1.0}
                if isotropic:
                    params =[5.2e-08, 3184.5476165501973,0.3824761153875444]
                    mat = MaterialRoutines()
                    self.materialDict[i]['Parameter'] = mat.stiffnessMatrix(type = 'isotropic', matParam = params)
                else:
                    self.angle = [60,-60]
                    params = [1.95e-07, #dens
                    165863.6296530634,  #C11
                    4090.899504376252,  #C12
                    2471.126276093059,  #C13
                    0.0,                #C14
                    0.0,                #C15
                    0.0,                #C16
                    9217.158022124806,  #C22
                    2471.126276093059,  #C23
                    0.0,                #C24
                    0.0,                #C25
                    0.0,                #C26
                    9217.158022124804,  #C33
                    0.0,                #C34
                    0.0,                #C35
                    0.0,                #C36
                    3360.0,             #C44
                    0.0,                #C45
                    0.0,                #C46
                    4200.0,             #C55
                    0.0,                #C56
                    4200.0]             #C66     
                    mat = MaterialRoutines(angle = self.angle)   
                    self.materialDict[i]['Parameter'] = mat.stiffnessMatrix(type = 'anisotropic', matParam = params)
                i+=1
        else:
            self.angle = angle
            self.materialDict = material
        

        self.bondfilters = {'Name':['bf_1'], 
                            'Normal':[[0.0,1.0,0.0]],
                            'Lower_Left_Corner':[[-0.06,0.0,-0.01]],
                            'Bottom_Unit_Vector':[[1.0,0.0,0.0]],
                            'Bottom_Length':[0.01],
                            'Side_Length':[0.01]}
        if(bc==''):
            self.bcDict = [{'Name': 'BC_1', 'boundarytype': 'Prescribed Displacement', 'blockId': 3, 'coordinate': 'y', 'value': '0.004*t'},
                           {'Name': 'BC_2', 'boundarytype': 'Prescribed Displacement', 'blockId': 4, 'coordinate': 'y', 'value': '-0.004*t'},
                           {'Name': 'BC_3', 'boundarytype': 'Prescribed Displacement', 'blockId': 1, 'coordinate': 'z', 'value': '0*t'},
                           {'Name': 'BC_4', 'boundarytype': 'Prescribed Displacement', 'blockId': 2, 'coordinate': 'z', 'value': '0*t'},]   
        else:
            self.bcDict = bc

        if(solver==''):               
            self.solverDict = {'verbose': False, 'initialTime': 0.0, 'finalTime': 0.075, 'solvertype': 'Verlet', 'safetyFactor': 0.95, 'numericalDamping': 0.000005, 'filetype': 'yaml'}
        else:
            self.solverDict = solver

        self.damBlock = ['']*numberOfBlocks
        self.damBlock[0] = 'PMMADamage'
        self.damBlock[1] = 'PMMADamage'

        self.intBlockId = [-1]*numberOfBlocks
        self.matBlock = ['PMMA']*numberOfBlocks
    # def createLoadBlock(self,x,y,k):
    #     if self.loadfuncx(x) == self.loadfuncy(y):
    #         k = self.loadfuncx(x)
    #     return k
    # def createBoundaryConditionBlock(self,x,y,k):
    #     k = (self.boundfuncx(x)-1)*self.boundfuncy(y)+1
    #     return k
    def createLoadIntroNode(self,x,y, k):
        if x < self.xbegin+self.dx[0]*3:
            if y > 0:
                k = 3
            if y < 0:
                k = 4
        return k

    def createBlock(self,y,k):
         #k = self.blockfuny(y)
        if y > 0:
            k = 1
        if y < 0:
            k = 2
        return k
    # def createAngles(self,x,y,z):
    #     '''tbd'''
    #     angle_x = 0
    #     if y<self.yend/2:
    #         angle_y = self.angle[0]
    #     else:
    #         angle_y = self.angle[1]
    #     angle_z = 0

    #     return angle_x, angle_y, angle_z
    def createModel(self):
        geo = Geometry()
        
        x,y,z = geo.createPoints(coor = [self.xbegin, self.xend, self.ybegin, self.yend, self.zbegin, self.zend], dx = self.dx)
        vol = np.zeros(len(x))
        k = np.ones(len(x))
        if self.rot:
            angle_x = np.zeros(len(x))
            angle_y = np.zeros(len(x))
            angle_z = np.zeros(len(x))
        for idx in range(0, len(x)):
            # if rot:
            #     angle_x[idx], angle_y[idx], angle_z[idx] = self.createAngles(x[idx],y[idx], z[idx])
            # if y[idx] >= self.yend/2:
            #     k[idx] = self.createLoadBlock(x[idx],y[idx],k[idx])
            # else:
            #     k[idx] = self.createBoundaryConditionBlock(x[idx],y[idx],k[idx])
            k[idx] = int(self.createBlock(y[idx],k[idx]))
            k[idx] = int(self.createLoadIntroNode(x[idx], y[idx], k[idx]))
            

            vol[idx] = self.dx[0] * self.dx[1] * self.dx[2]
        
        writer = ModelWriter(modelClass = self)
        
        if self.rot:
            model = {'x':x, 'y':y, 'z': z, 'k':k, 'vol':vol, 'angle_x':angle_x, 'angle_y':angle_y, 'angle_z': angle_z}
            writer.writeMeshWithAngles(model)
        else:
            model = {'x':x, 'y':y, 'z': z, 'k':k, 'vol':vol}
            writer.writeMesh(model)
        writer.writeNodeSets(model)
        self.writeFILE(writer = writer, model = model)
        
        return model

    def createBlockdef(self,model):
        blockLen = int(max(model['k']))
        blockDef=[{}]*blockLen
        for idx in range(0,blockLen):
            blockDef[idx] = {'Name': 'block_' + str(idx+1), 'material':self.matBlock[idx], 'damageModel':self.damBlock[idx], 'horizon': self.scal*max([self.dx[0],self.dx[1]]),'interface':self.intBlockId[idx]}
        # 3d tbd
        return blockDef
    def writeFILE(self, writer, model):
        
        if self.blockDef=='':
            blockDef = self.createBlockdef(model)
        else:
            for idx in range(0,len(self.blockDef)):
                self.blockDef[idx]['horizon']= self.scal*max([self.dx[0],self.dx[1]])
            blockDef = self.blockDef

        writer.createFile(blockDef)
