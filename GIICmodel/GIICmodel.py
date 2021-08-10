import numpy as np
from scipy import interpolate
from support.modelWriter import ModelWriter
from support.material import MaterialRoutines
from support.geometry import Geometry
class GIICmodel(object):
    def __init__(self, xend = 1, yend = 1, zend = 1, dx=[0.1,0.1,0.1], filename = 'GIICmodel', filetype = 'xml', solvertype = 'Verlet', TwoD = False):
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
        self.scal = 4.01
        self.TwoD = TwoD
        # anriss
        self.a = 20/151*xend
        
        self.dx   = dx
        self.xend = xend
        self.yend = yend
        self.zend = zend
        if TwoD:
            self.zend = 0
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
        yblock = [0,yend/2-7*dx[1],yend/2-6*dx[1],yend/2-dx[1]/4,yend/2+dx[1]/4, yend/2+6*dx[1],yend/2+7*dx[1], yend+dx[1]]

        self.blockfuny = interpolate.interp1d(yblock,z, kind='linear')
        ''' Definition of model
        '''
        
        isotropic = False
        matNameList = ['PMMA']
        self.materialDict = {}
        self.angle = [0,0]
        self.damageDict = {'PMMADamage':{'Energy':5.1, 'Interface':{'InterfaceEnergy':0.01, 'InterfaceBlockIDs':[8,9]}}}
        
        for material in matNameList:
            self.materialDict[material] = {'MatType':'Linear Elastic Correspondence'}
            if isotropic:
                params =[5.2e-08, 3184.5476165501973,0.3824761153875444]
                mat = MaterialRoutines()
                self.materialDict[material]['Parameter'] = mat.stiffnessMatrix(type = 'isotropic', matParam = params)
            else:
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
                self.materialDict[material]['Parameter'] = mat.stiffnessMatrix(type = 'anisotropic', matParam = params)


        self.bondfilters = {'Name':['bf_1'], 'Normal':[[0,1,0]],'Lower_Left_Corner':[[0,self.yend/2,-0.1]],'Bottom_Unit_Vector':[[1,0,0]],'Bottom_Length':[self.a],'Side_Length':[zend + 0.5]}
        self.nsList = [5,6,7,10]
        self.bcDict = {'NNodesets': 4, 'BCDef': {'NS': [2,2,3,1,4], 'Type':['Prescribed Displacement','Prescribed Displacement','Prescribed Displacement','Prescribed Displacement','Prescribed Displacement'], 'Direction':['x','y','y','y','y'], 'Value':[0,0,-1,0,0]}}    
        self.damBlock = ['']*numberOfBlocks
        self.damBlock[7] = 'PMMADamage'
        self.damBlock[8] = 'PMMADamage'
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
    def createModel(self, rot = False):
        geo = Geometry()
        x,y,z = geo.createPoints(coor = [0,self.xend,0,self.yend,0,self.zend], dx = self.dx)
        vol = np.zeros(len(x))
        k = np.ones(len(x))
        if rot:
            angle_x = np.zeros(len(x))
            angle_y = np.zeros(len(x))
            angle_z = np.zeros(len(x))
        for idx in range(0, len(x)):
            if rot:
                angle_x[idx], angle_y[idx], angle_z[idx] = self.createAngles(x[idx],y[idx], z[idx])
            if y[idx] >= self.yend/2:
                k[idx] = self.createLoadBlock(x[idx],y[idx],k[idx])
            else:
                k[idx] = self.createBoundaryConditionBlock(x[idx],y[idx],k[idx])
            k[idx] = int(self.createBCNode(x[idx],y[idx], k[idx]))
            k[idx] = int(self.createLoadIntroNode(x[idx],y[idx], k[idx]))
            k[idx] = int(self.createBlock(y[idx],k[idx]))

            vol[idx] = self.dx[0] * self.dx[1] * self.dx[2]
        
        writer = ModelWriter(filename = self.filename)
        
        if rot:
            model = {'x':x, 'y':y, 'z': z, 'k':k, 'vol':vol, 'angle_x':angle_x, 'angle_y':angle_y, 'angle_z': angle_z}
            writer.writeMeshWithAngles(model)
        else:
            model = {'x':x, 'y':y, 'z': z, 'k':k, 'vol':vol}
            writer.writeMesh(model)
        writer.writeNodeSets(model,self.nsList)
        self.writeFILE(filetype = self.filetype, solvertype= self.solvertype, writer = writer, model = model)
        
        return model
    
    def createBlockdef(self,model, materialDict):
        blockLen = int(max(model['k']))
        blockDef = {'Material':self.matBlock,'Damage':self.damBlock,'Horizon':np.zeros(blockLen)}
        for idx in range(0,blockLen):
            blockDef['Horizon'][idx] = self.scal*max([self.dx[0],self.dx[1]])
        # 3d tbd
        return blockDef
    def writeFILE(self, filetype, solvertype, writer, model):
        
        blockDef = self.createBlockdef(model, self.materialDict)

        writer.createFile(filetype, solvertype, self.bcDict, self.damageDict, self.materialDict,blockDef,self.bondfilters, self.TwoD)
  