
import numpy as np
from scipy import interpolate
from support.modelWriter import ModelWriter
from support.geometry import Geometry
class GIICmodel(object):
    def __init__(self, xend = 1, yend = 1, dx=[0.1,0.1], filename = 'GIICmodel', filetype = 'xml', solvertype = 'Verlet'):
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
        '''
        

        
        self.filename = filename
        self.filetype = filetype
        self.solvertype = solvertype
        self.scal = 4.01
        # anriss
        self.a = 20
        self.nsList = [5,6,7]
        self.dx   = dx
        self.xend = xend
        self.yend = yend
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
        self.materialDict = {'DamName':['PMMADamage'],'Energy':[0.1],'MatName':['PMMA'],'MatType':['Linear Elastic Correspondence'],'EMod':[3184.5476165501973],'nu':[0.3824761153875444], 'dens':[5.2e-08]}
        self.bondfilters = {'Name':['bf_1'], 'Normal':[[0,1,0]],'Lower_Left_Corner':[[0,self.yend/2,-0.1]],'Bottom_Unit_Vector':[[1,0,0]],'Bottom_Length':[0.2],'Side_Length':[self.a]}
        self.bcDict = {'NNodesets': 3, 'BCDef': {'NS': [1,1,3,2], 'Type':['Prescribed Displacement','Prescribed Displacement','Body Force','Prescribed Displacement'], 'Direction':['x','y','y','y'], 'Value':[0,0,-500,0]}}    
        self.damBlock = ['']*9
        self.damBlock[7] = 'PMMADamage'
        self.damBlock[8] = 'PMMADamage'
        self.matBlock = ['PMMA']*9
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
        if  x > self.xend - self.dx[0]/2 and y == 0:
            k = 6
        return k
    def createBlock(self,y,k):
        #k = self.blockfuny(y)
        if  self.yend/2-5*self.dx[1] < y < self.yend/2:
            k = 8

        if  self.yend/2 <= y < self.yend/2+5*self.dx[1]:
            k = 9  
        return k
    def createModel(self):
        geo = Geometry()
        x,y = geo.createPoints(coor = [0,self.xend,0,self.yend], dx = self.dx)
        vol = np.zeros(len(x))
        k = np.ones(len(x))
        for idx in range(0, len(x)):

            if y[idx] >= self.yend/2:
                k[idx] = self.createLoadBlock(x[idx],y[idx],k[idx])
            else:
                k[idx] = self.createBoundaryConditionBlock(x[idx],y[idx],k[idx])
            k[idx] = int(self.createBCNode(x[idx],y[idx], k[idx]))
            k[idx] = int(self.createLoadIntroNode(x[idx],y[idx], k[idx]))
            k[idx] = int(self.createBlock(y[idx],k[idx]))

            vol[idx] = self.dx[0] * self.dx[1]
        model = {'x':x, 'y':y, 'k':k, 'vol':vol}
        writer = ModelWriter(filename = self.filename)
        writer.writeNodeSets(model,self.nsList)
        writer.writeMesh(model)
        self.writeFILE(filetype = self.filetype, solvertype= self.solvertype, writer = writer, model = model)
        
        return model
    
    def createBlockdef(self,model, materialDict):
        blockLen = int(max(model['k']))
        blockDef = {'Material':self.matBlock,'Damage':self.damBlock,'Horizon':np.zeros(blockLen)}
        for idx in range(0,blockLen):
            blockDef['Horizon'][idx] = self.scal*max([self.dx[0],self.dx[1]])

        return blockDef
    def writeFILE(self, filetype, solvertype, writer, model):
        
        blockDef = self.createBlockdef(model, self.materialDict)
        
            
        writer.createFile(filetype, solvertype, self.bcDict, self.materialDict,blockDef,self.bondfilters)

             

