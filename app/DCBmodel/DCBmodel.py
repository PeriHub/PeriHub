import sys
import numpy as np
from scipy import interpolate
from support.modelWriter import ModelWriter
from support.material import MaterialRoutines
from support.geometry import Geometry

class DCBmodel(object):
    def __init__(self, xend = 0.045, yend = 0.01, zend = 0.003, dx=[0.001,0.001,0.001], filename = 'DCBmodel', filetype = 'yaml', solvertype = 'Verlet', TwoD = False, rot = 'False'):
        '''
            definition der blocks
            k =
            1 basisplatte
            2 Z Zero Node Set
            3 Min Y Up Node Set
            4 Min Y Down Node Set
        '''
        
        self.filename = filename
        self.filetype = filetype
        self.frequency = 1000
        self.solvertype = solvertype
        self.finalTime = 0.075
        self.scal = 4.01
        self.TwoD = TwoD
        self.onlyTension = True
        self.nsList = [3,4]
        self.dx   = dx
        self.xbegin = -0.005
        self.ybegin = -0.01
        self.zbegin = -0.003
        self.xend = xend + dx[0]
        self.yend = yend + dx[1]
        self.zend = zend + dx[2]
        self.rot = rot
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
        self.materialDict = {}
        self.angle = [0,0]
        self.damageDict = {'PMMADamage':{'Energy':5.1, 'InferaceEnergy':0.01}}
        
        self.outputDict = {'Output1':{'Displacement','Partial_Stress','Damage','Force'},
        'Output2':{'Damage','External_Displacement','External_Force'}, 
        'Compute Class Parameters':[{'Name':'External_Displacement','Variable':'Displacement', 'Calculation Type':'Minimum','Block':'block_3'},
                                    {'Name':'External_Force','Variable':'Force', 'Calculation Type':'Sum','Block':'block_3'}]}
        self.frequency = [50, 20]
        self.initStep = [0, 0]
        
        for material in matNameList:
            self.materialDict[material] = {'MatType':'Linear Elastic Correspondence'}
            if isotropic:
                params =[2000.0,    #Density
                0,                  #Young's Modulus
                0,                  #Poisson's Ratio
                1.7500e09,          #Bulk Modulus
                8.08e8]             #Shear Modulus
                self.materialDict[material]['Parameter'] = mat.stiffnessMatrix(type = 'isotropic', matParam = params)
            else:
                self.angle = [30,-30]
                params = [1.95e-07, #Density
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
                self.materialDict[material]['Parameter'] = mat.stiffnessMatrix(type = 'anisotropic', matParam = params)
        
        

        self.bondfilters = {'Name':['bf_1'], 
                            'Normal':[[0.0,1.0,0.0]],
                            'Lower_Left_Corner':[[-16.0,0.0,-16.0]],
                            'Bottom_Unit_Vector':[[1.0,0.0,0.0]],
                            'Bottom_Length':[16.0],
                            'Side_Length':[32.0]}
        self.bcDict = {'NNodesets': 2, 
                        'BCDef': {'NS': [1,2], 
                        'Type':['Prescribed Displacement','Prescribed Displacement'], 
                        'Direction':['y','y'], 
                        'Value':[0.004,-0.004]}}    
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
        blockDef = {'Material':self.matBlock,'Damage':self.damBlock,'Horizon':np.zeros(blockLen),'Interface':self.intBlockId}
        for idx in range(0,blockLen):
            blockDef['Horizon'][idx] = self.scal*max([self.dx[0],self.dx[1]])
        # 3d tbd
        return blockDef
    def writeFILE(self, writer, model):
        
        blockDef = self.createBlockdef(model)

        writer.createFile(blockDef)
