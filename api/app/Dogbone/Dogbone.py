import sys
import numpy as np
from numpy.core import numeric
from scipy import interpolate
from support.modelWriter import ModelWriter
from support.material import MaterialRoutines
from support.geometry import Geometry

class Dogbone(object):
    def __init__(self, xend = 0.115, h1 = 0.019, h2 = 0.013, zend = 0.003, dx=[0.0005,0.0005,0.0005], 
    filename = 'Dogbone', TwoD = False, rot = False, angle = [0,0], 
    material = '', damage = '', block = '', bc = '', compute = '', output = '', solver = '', username = ''):
        '''
            definition der blocks
            k =
            1 basisplatte
            2 Z Zero Node Set
            3 Min Y Up Node Set
            4 Min Y Down Node Set
        '''
        
        self.filename = filename
        self.scal = 4.01
        self.TwoD = TwoD
        self.nsList = [3,4]
        self.dx   = dx
        self.xend = xend
        self.h1 = h1
        self.h2 = h2
        self.zend = zend + dx[2]
        self.rot = rot
        self.blockDef = block
        self.username = username
        if self.TwoD:
            self.zbegin = 0
            self.zend = 0
            self.dx[2] = 1
        numberOfBlocks = 5
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
            self.damageDict[0] = {'Name': 'PMMADamage', 'damageModel': 'Critical Energy Correspondence', 'criticalEnergy':5.1, 'interblockdamageEnergy':0.01, 'onlyTension': True, 'detachedNodesCheck': True, 'thickness': 10, 'hourglassCoefficient': 1.0, 'stabilizatonType': 'Global Stiffness'}
        else:
            self.damageDict = damage
        
        if compute=='':
            self.computeDict[0] = {'Name':'External_Displacement','variable':'Displacement', 'calculationType':'Minimum','blockName':'block_3'}
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
                self.materialDict[i] = {'Name': material, 'MatType':'Linear Elastic Correspondence', 'youngsModulus': 210000.0, 'poissonsRatio': 0.3, 'tensionSeparation': False, 'materialSymmetry': 'Anisotropic', 'stabilizatonType': 'Global Stiffness', 'thickness': 10.0, 'hourglassCoefficient': 1.0, 'yieldStress': 200}
                if isotropic:
                    params =[200000.0,    #Density
                    1.5e9,                #Young's Modulus
                    0.3,                  #Poisson's Ratio
                    0,                    #Bulk Modulus
                    0]                    #Shear Modulus
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
        

        self.bondfilters = {}
        if(bc==''):
            self.bcDict = [{'Name': 'BC_1', 'boundarytype': 'Prescribed Displacement', 'blockId': 1, 'coordinate': 'x', 'value': '0*t'},
                           {'Name': 'BC_2', 'boundarytype': 'Prescribed Displacement', 'blockId': 5, 'coordinate': 'x', 'value': '10*t'},]   
        else:
            self.bcDict = bc

        if(solver==''):               
            self.solverDict = {'verbose': False, 'initialTime': 0.0, 'finalTime': 0.075, 'solvertype': 'Verlet', 'safetyFactor': 0.95, 'numericalDamping': 0.000005, 'filetype': 'xml'}
        else:
            self.solverDict = solver

        self.damBlock = ['']*numberOfBlocks
        self.damBlock[2] = 'PMMADamage'

        self.intBlockId = ['']*numberOfBlocks
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
        # dx = 0.001
        t = self.dx[0]
        # Lges = 0.115
        #print(dx)
        #self.dx[0] = self.xend/int(self.xend/self.dx[0])
        
        # h1=0.019; h2=0.013
        #dy = self.h1/int(self.h1/self.dx[0])
        
        #print(self.dx[0],self.dx[1])
        bc = 0.002
        R = 0.076; l2 = 0.057
        dl = np.sqrt(R*R-(R-(self.h1-self.h2)/2)**2)
        
        l1 = (self.xend - 2*dl - l2)/2;
        dh =  (self.h1-self.h2)/2
        alpha = np.arccos((R-dh)/R)*180/np.pi

        geo = Geometry()
        
        topSurf, bottomSurf = geo.createBoundaryCurve(h = self.h1, l1 = l1, R = R, l2 = l2, alphaMax = alpha, dl = dl, dh = dh)
        blockDef = np.array([0, bc, l1, l1+2*dl+l2, self.xend - bc])
        x0 = np.arange(0,self.xend+self.dx[0], self.dx[0])
        y0 = np.arange(0,self.h1+self.dx[1], self.dx[1])
        z0 = np.arange(0,t, self.dx[0])
        num = len(x0)*len(y0)*len(z0)
        x = []
        y = []
        z = []
        k = []
        vol = np.full((num), self.dx[0]*self.dx[0])
        matNum = 0
        xList = []
        yList = []
        #vol = dx*dx #*dx
        stringLeft = ''
        stringRight = ''
        string = '# x y z block_id volume\n'
        num = 0
        bccount = 0
        for xval in x0:
            for yval in y0:
                for zval in z0:
                    if geo.checkValGreater(yval,bottomSurf(xval)) and geo.checkValLower(yval,topSurf(xval)):
                        num += 1
                        for idx,val in enumerate(blockDef): 
                            if geo.checkValGreater(xval,val): matNum = idx + 1
                        if geo.checkValLower(xval,blockDef[0]):
                            stringLeft += str(num) + '\n'
                            bccount += 1
                        if geo.checkValGreater(xval,blockDef[-1]):
                            stringRight += str(num) + '\n'
                            bccount += 1
                        x.append(xval)
                        y.append(yval)
                        z.append(zval)
                        k.append(matNum)
                        # x[num-1] = xval
                        # y[num-1] = yval
                        # z[num-1] = zval
                        # k[num-1] = matNum
                        # string += str(xval) + ' ' + str(yval) + ' ' +  str(zval)  + ' ' + str(matNum) + ' ' + str(vol) + '\n'  
                        xList.append(xval);                yList.append(yval)
        
        #for zval in z0: 
            #string += str(l1+dl) + ' ' + str(0.5*(self.h1-self.h2)) + ' ' +  str(zval)  + ' ' + str(3) + ' ' + str(vol) + '\n' 
            
            # x[num-1] = l1+dl
            # y[num-1] = 0.5*(self.h1-self.h2)
            # z[num-1] = zval
            # k[num-1] = 3
            #x.append(l1+dl)
            #y.append(0.5*(self.h1-self.h2))
            #z.append(zval)
            #k.append(3)
        #xList.append(l1+dl);                yList.append(0.5*(self.h1-self.h2))

        #vol = np.(dx*dx)
        if self.rot:
            angle_x = np.zeros(len(x))
            angle_y = np.zeros(len(x))
            angle_z = np.zeros(len(x))
        #for idx in range(0, len(x)):
            # if rot:
            #     angle_x[idx], angle_y[idx], angle_z[idx] = self.createAngles(x[idx],y[idx], z[idx])
            # if y[idx] >= self.yend/2:
            #     k[idx] = self.createLoadBlock(x[idx],y[idx],k[idx])
            # else:
            #     k[idx] = self.createBoundaryConditionBlock(x[idx],y[idx],k[idx])
            #k[idx] = int(self.createBlock(y[idx],k[idx]))
            #k[idx] = int(self.createLoadIntroNode(x[idx], y[idx], k[idx]))
            

            #vol[idx] = self.dx[0] * self.dx[1] * self.dx[2]
        
        writer = ModelWriter(modelClass = self)
        
        if self.rot:
            model = {'x':x, 'y':y, 'z': z, 'k':k, 'vol':vol, 'angle_x':angle_x, 'angle_y':angle_y, 'angle_z': angle_z}
            writer.writeMeshWithAngles(model)
        else:
            model = {'x':x, 'y':y, 'z': z, 'k':np.array(k), 'vol':vol}
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
