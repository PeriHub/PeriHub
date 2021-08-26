import numpy as np
import ast
from scipy import interpolate
from support.modelWriter import ModelWriter
from support.material import MaterialRoutines
from support.geometry import Geometry
class GIICmodel(object):
    def __init__(self, xend = 1, yend = 1, zend = 1, dx=[0.1,0.1,0.1], filename = 'GIICmodel', filetype = 'yaml', solvertype = 'Verlet', finalTime = 0.075, TwoD = False, rot = 'False', angle = [0,0], material = '', damage = '', block = '', bc = '', output = '', solver = ''):
        '''
            definition der blocks
            k =
            1 basisplatte
            2 RB links
            3 RB rechts
            4 Last
            5 RB Node links 
            6 RB Node rechts
            7 Kraft Node
            8 Schadensbereich
            9 Schadensbereich
            10 RB Node links oben
            11 RB links oben - fehlt noch
        '''
        

        
        self.filename = filename
        self.filetype = filetype
        self.solvertype = solvertype
        self.finalTime = finalTime
        self.scal = 4.01
        self.TwoD = TwoD
        self.rot = rot
        # anriss
        self.a = 20/151*xend
        self.blockDef = block
        
        self.dx   = dx
        self.xend = xend
        self.yend = yend
        self.zend = zend
        self.rot = rot
        if TwoD:
            self.zend = 0
            self.dx[2] = 1
        numberOfBlocks = 10
        xbound = [0, 4*dx[0],5*dx[0], xend-5*dx[0],xend-4*dx[0],xend + dx[0]]
        ybound = [0, 4*dx[1],5*dx[1], yend + dx[1]]

        z = [2,2,1,1,3,3]
        self.boundfuncx = interpolate.interp1d(xbound,z, kind='linear')
        z = [1,1,0,0]
        self.boundfuncy = interpolate.interp1d(ybound,z, kind='linear')
        xload = [0, xend/2-2*dx[0],xend/2+2*dx[0], xend + dx[0]]
        z = [1,4,4,1]
        self.loadfuncx = interpolate.interp1d(xload,z, kind='linear')
        yload = [0, yend-5*dx[1],yend-4*dx[1], yend + dx[1]]
        z = [1,1,4,4]
        self.loadfuncy = interpolate.interp1d(yload,z, kind='linear')
        
        z = [1,1,8,8,9,9,1,1]
        yblock = [0,yend/2-5*dx[1],yend/2-4*dx[1],yend/2-dx[1]/4,yend/2+dx[1]/4, yend/2+4*dx[1],yend/2+5*dx[1], yend+dx[1]]

        self.blockfuny = interpolate.interp1d(yblock,z, kind='linear')
        ''' Definition of model
        '''
        
        isotropic = False
        matNameList = ['PMMA']
        self.materialDict = [{}]
        self.damageDict = [{}]
        self.outputDict = [{},{}]
        self.angle = [0,0]
        if damage=='':
            self.damageDict[0] = {'Name': 'PMMADamage', 'damageModel': 'Critical Energy Correspondence', 'criticalEnergy':5.1, 'interblockdamageEnergy':0.01, 'onlyTension': True, 'detachedNodesCheck': True, 'thickness': 10, 'hourglassCoefficient': 1.0, 'stabilizatonType': 'Global Stiffness'}
        else:
            self.damageDict = damage

        self.computeDict = {'Compute Class Parameters':[{'Name':'External_Displacement','Variable':'Displacement', 'Calculation Type':'Minimum','Block':'block_7'},
                                                      {'Name':'External_Force','Variable':'Force', 'Calculation Type':'Sum','Block':'block_7'}]}
        
        if output=='':
            self.outputDict[0] = {'Name': 'Output1', 'Displacement': True, 'Force': True, 'Damage': True, 'Partial_Stress': False, 'External_Force': False, 'External_Displacement': False, 'Number_Of_Neighbors': False, 'Frequency': 5000, 'InitStep': 0}
            self.outputDict[1] = {'Name': 'Output2', 'Displacement': False, 'Force': False, 'Damage': True, 'Partial_Stress': True, 'External_Force': True, 'External_Displacement': True, 'Number_Of_Neighbors': False, 'Frequency': 200, 'InitStep': 0}
        else:
            self.outputDict = output
        
        
        self.frequency = [5000, 200]
        self.initStep = [0, 0]

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
                            'Lower_Left_Corner':[[0.0,self.yend/2,-0.1]],
                            'Bottom_Unit_Vector':[[1.0,0.0,0.0]],
                            'Bottom_Length':[self.a],
                            'Side_Length':[zend + 0.5]}

        if(bc==''):               
            self.bcDict = [{'Name': 'BC_1', 'boundarytype': 'Prescribed Displacement', 'blockId': 5, 'coordinate': 'y', 'value': '0*t'},
                        {'Name': 'BC_2', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'y', 'value': '0*t'},
                        {'Name': 'BC_3', 'boundarytype': 'Prescribed Displacement', 'blockId': 7, 'coordinate': 'y', 'value': '-10*t'},]
        else:
            self.bcDict = bc

        # self.nsList = [5,6,7,10]
        # self.bcDict = {'NNodesets': 4, 
        #                 'BCDef': {'NS': [2,2,3,1,4], 
        #                 'Type':['Prescribed Displacement',
        #                 'Prescribed Displacement',
        #                 'Prescribed Displacement',
        #                 'Prescribed Displacement',
        #                 'Prescribed Displacement'], 
        #                 'Direction':['x','y','y','y','y'], 
        #                 'Value':[0,0,-10,0,0]}}    
        self.damBlock = ['']*numberOfBlocks
        self.damBlock[7] = 'PMMADamage'
        self.damBlock[8] = 'PMMADamage'
        self.intBlockId = ['']*numberOfBlocks
        self.intBlockId[7] = 9
        self.intBlockId[8] = 8
        self.matBlock = ['PMMA']*numberOfBlocks
    def createLoadBlock(self,x,y,k):
        if self.loadfuncx(x) == self.loadfuncy(y):
            k = self.loadfuncx(x)
        return k
    def createBoundaryConditionBlock(self,x,y,k):
        k = (self.boundfuncx(x)-1)*self.boundfuncy(y)+1
        return k
    def createLoadIntroNode(self,x,y, k):
        if (self.xend-self.dx[0])/2 < x < (self.xend+self.dx[0])/2:
            if y > self.yend-self.dx[1]/2:
                k = 7
        return k
    def createBCNode(self,x,y, k):
        if x == 0 and y == 0:
            k = 5
        if x > self.xend - self.dx[0]/3 and y == 0:
            k = 6
        if x == 0  and y > self.yend - self.dx[1]/3:
            k = 10
        return k
    def createBlock(self,y,k):
        #k = self.blockfuny(y)
        if  self.yend/2-5*self.dx[1] < y < self.yend/2:
            k = 8
        if  self.yend/2 <= y < self.yend/2+5*self.dx[1]:
            k = 9  
        return k
    def createAngles(self,x,y,z):
        '''tbd'''
        angle_x = 0
        if y<self.yend/2:
            angle_y = self.angle[0]
        else:
            angle_y = self.angle[1]
        angle_z = 0

        return angle_x, angle_y, angle_z
    def createModel(self):
        geo = Geometry()
        x,y,z = geo.createPoints(coor = [0,self.xend,0,self.yend,0,self.zend], dx = self.dx)
        vol = np.zeros(len(x))
        k = np.ones(len(x))
        if self.rot:
            angle_x = np.zeros(len(x))
            angle_y = np.zeros(len(x))
            angle_z = np.zeros(len(x))
        for idx in range(0, len(x)):
            if self.rot:
                angle_x[idx], angle_y[idx], angle_z[idx] = self.createAngles(x[idx],y[idx], z[idx])
            if y[idx] >= self.yend/2:
                k[idx] = self.createLoadBlock(x[idx],y[idx],k[idx])
            else:
                k[idx] = self.createBoundaryConditionBlock(x[idx],y[idx],k[idx])
            k[idx] = int(self.createBCNode(x[idx],y[idx], k[idx]))
            k[idx] = int(self.createLoadIntroNode(x[idx],y[idx], k[idx]))
            k[idx] = int(self.createBlock(y[idx],k[idx]))

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
  