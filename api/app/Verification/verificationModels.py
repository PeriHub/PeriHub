import numpy as np
# import ast
from scipy import interpolate
from support.modelWriter import ModelWriter
from support.material import MaterialRoutines
from support.geometry import Geometry


class VerificationModels(object):

    def __init__(self, TwoD = True):
        # https://wiki.dlr.de/display/PDWiki/Tests
        self.scal = 4.01
        self.l = 0.021
        self.h = 0.002
        self.B = 0.001
        self.E = 7e10
        self.nu = 0.3
        self.dx = [0.00005, 0.00005, 0.00005]
        self.Amp = '0.005*(-x/' + str(self.l) + '+ 1)'
        self.blockDef = ''
        self.computeDict = {}
        
        self.damageDict = ''
        
        self.bondfilters = {'Name':[]}
       # if compute=='':
       #     self.computeDict[0] = {'Name':'External_Displacement','variable':'Displacement', 'calculationType':'Minimum','blockName':'block_7'}
       #     self.computeDict[1] = {'Name':'External_Force','variable':'Force', 'calculationType':'Sum','blockName':'block_7'}
       # else:
       #     self.computeDict = compute
        self.solverDict = {}
        self.TwoD = True

        self.outputDict = [{}]*1
        self.outputDict[0] = {'Name': 'Output1', 'Displacement': True, 'Force': True, 'Damage': False, 'Partial_Stress': True, 'External_Force': False, 'External_Displacement': False, 'Number_Of_Neighbors': False, 'Frequency': 500, 'InitStep': 0}
        #self.outputDict[1] = {'Name': 'Output2', 'Displacement': False, 'Force': False, 'Damage': False, 'Partial_Stress': True, 'External_Force': False, 'External_Displacement': False, 'Number_Of_Neighbors': False, 'Frequency': 200, 'InitStep': 0}

        matNameList = ['isoMatOne','isoMatTwo', 'anisoMat']
        self.materialDict = [{}]*len(matNameList)
        i = 0
        for material in matNameList:
            self.materialDict[i] = {'Name': material, 'MatType':'Linear Elastic Correspondence', 'youngsModulus': 2.1e11, 'poissonsRatio': 0.3, 'tensionSeparation': False, 'materialSymmetry': 'Anisotropic', 'stabilizatonType': 'Global Stiffness', 'thickness': 10.0, 'hourglassCoefficient': 1.0}
            i+=1
        params =[270000, 7e10,0.3,0,0]
        mat = MaterialRoutines()
        self.materialDict[0]['Parameter'] = mat.stiffnessMatrix(type = 'isotropic', matParam = params)
        params =[270000, 2.1e11,0.3,0,0]
        self.materialDict[1]['Parameter'] = mat.stiffnessMatrix(type = 'isotropic', matParam = params)
        self.angle = [0,0]
        params = [195000, #dens
        165863e6,  #C11
        4090e6,  #C12
        2471e6,  #C13
        0.0,                #C14
        0.0,                #C15
        0.0,                #C16
        9217e6,  #C22
        2471e6,  #C23
        0.0,                #C24
        0.0,                #C25
        0.0,                #C26
        9217e6,  #C33
        0.0,                #C34
        0.0,                #C35
        0.0,                #C36
        3360e6,             #C44
        0.0,                #C45
        0.0,                #C46
        4200e6,             #C55
        0.0,                #C56
        4200e6]             #C66     
        self.materialDict[2]['Parameter'] = mat.stiffnessMatrix(type = 'anisotropic', matParam = params)
        self.bcDict = [{'Name': 'BC_1', 'boundarytype': 'Prescribed Displacement', 'blockId': 3, 'coordinate': 'x', 'value': str(self.Amp)+'*t'},
                       {'Name': 'BC_2', 'boundarytype': 'Prescribed Displacement', 'blockId': 4, 'coordinate': 'x', 'value': str(self.Amp)+'*t'},
                       {'Name': 'BC_3', 'boundarytype': 'Prescribed Displacement', 'blockId': 5, 'coordinate': 'x', 'value': '0'},
                       {'Name': 'BC_4', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'x', 'value': '0'},
                       {'Name': 'BC_5', 'boundarytype': 'Prescribed Displacement', 'blockId': 5, 'coordinate': 'y', 'value': '0'},
                       {'Name': 'BC_6', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'y', 'value': '0'}]
                       #{'Name': 'BC_5', 'boundarytype': 'Prescribed Displacement', 'blockId': 7, 'coordinate': 'x', 'value': '0'},
                       #{'Name': 'BC_6', 'boundarytype': 'Prescribed Displacement', 'blockId': 7, 'coordinate': 'y', 'value': '0'}]


           
        self.solverDict = {'verbose': False, 'initialTime': 0.0, 'finalTime': 0.002, 'solvertype': 'NOXQuasiStatic','Tolerance':1e-5, 'NumberOfLoadSteps':1000, 'safetyFactor': 0.5, 'numericalDamping': 0.00005, 'filetype': 'xml'}

        
    def createVerificationModels(self):

        self.dx[1] = self.avoidMiddleNode(self.h,self.dx[1])
        self.dx[0] = self.dx[1]
        self.dx[2] = self.dx[1]
        self.bcDict[0]['coordinate'] = 'x'
        self.bcDict[1]['coordinate'] = 'x'
        self.matBlock = ['isoMatOne','isoMatOne','isoMatOne','isoMatOne','isoMatOne','isoMatOne','isoMatOne']
        
        self.callModelbuilder(TwoD = True,angle = [0,0],filename = 'isoTension2D')
    
        self.bcDict.append( {'Name': 'BC_7', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'z', 'value': '0'})
        self.callModelbuilder(TwoD = False,angle = [0,0],filename = 'isoTension3D')
        del self.bcDict[-1]
        self.matBlock = ['isoMatOne','isoMatTwo','isoMatOne','isoMatTwo','isoMatOne','isoMatTwo','isoMatOne']
        self.callModelbuilder(TwoD = True,angle = [0,0],filename = 'twoLayerIsoTension2D')
        self.bcDict.append( {'Name': 'BC_7', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'z', 'value': '0'})
        self.callModelbuilder(TwoD = False,angle = [0,0],filename = 'twoLayerIsoTension3D')
        self.bcDict[0]['coordinate'] = 'y'
        self.bcDict[1]['coordinate'] = 'y'
        self.matBlock = ['isoMatOne','isoMatOne','isoMatOne','isoMatOne','isoMatOne','isoMatOne','isoMatOne']
        del self.bcDict[-1]
        self.callModelbuilder(TwoD = True,angle = [0,0],filename = 'isoBending2D')
        self.bcDict.append( {'Name': 'BC_7', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'z', 'value': '0'})
        self.callModelbuilder(TwoD = False,angle = [0,0],filename = 'isoBending3D')
        self.matBlock = ['isoMatOne','isoMatTwo','isoMatOne','isoMatTwo','isoMatOne','isoMatTwo','isoMatOne']
        del self.bcDict[-1]
        self.callModelbuilder(TwoD = True,angle = [0,0],filename = 'twoLayerIsoBending2D')
        self.bcDict.append( {'Name': 'BC_7', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'z', 'value': '0'})
        self.callModelbuilder(TwoD = False,angle = [0,0],filename = 'twoLayerIsoBending3D')
        self.matBlock = ['anisoMat','anisoMat','anisoMat','anisoMat','anisoMat','anisoMat','anisoMat']
        self.bcDict[0]['coordinate'] = 'x'
        self.bcDict[1]['coordinate'] = 'x'
        del self.bcDict[-1]
        self.callModelbuilder(TwoD = True,angle = [90,90],filename = 'twoLayerAniso090Tension2D')
        self.bcDict.append( {'Name': 'BC_7', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'z', 'value': '0'})
        self.callModelbuilder(TwoD = False,angle = [0,90],filename = 'twoLayerAniso090Tension3D')
        del self.bcDict[-1]
        self.callModelbuilder(TwoD = True,angle = [30,-30],filename = 'twoLayerAniso30m30Tension2D')
        self.bcDict.append( {'Name': 'BC_7', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'z', 'value': '0'})
        self.callModelbuilder(TwoD = False,angle = [30,-30],filename = 'twoLayerAniso30m30Tension3D')     
        self.bcDict[0]['coordinate'] = 'y'
        self.bcDict[1]['coordinate'] = 'y'
# fehlt noch was
        del self.bcDict[-1]
        self.callModelbuilder(TwoD = True,angle = [0,90],filename = 'twoLayerAniso090Bending2D')
        self.bcDict.append( {'Name': 'BC_7', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'z', 'value': '0'})
        self.callModelbuilder(TwoD = False,angle = [9,90],filename = 'twoLayerAniso090Bending3D')
        del self.bcDict[-1]
        self.callModelbuilder(TwoD = True,angle = [30,-30],filename = 'twoLayerAniso30m30Bending2D')
        self.bcDict.append( {'Name': 'BC_7', 'boundarytype': 'Prescribed Displacement', 'blockId': 6, 'coordinate': 'z', 'value': '0'})
        self.callModelbuilder(TwoD = False,angle = [30,-30],filename = 'twoLayerAniso30m30Bending3D')     
    
    def callModelbuilder(self,TwoD = True,angle = [0,0],filename = 'isoTension'):
        self.filename = filename
        self.angle = angle
        self.TwoD = TwoD
        self.createModel(TwoD = TwoD, xend = self.l, yend = self.h, zend = self.B, dx = self.dx, angle = angle)
        
    def avoidMiddleNode(self,yend,dx):
        n = int(yend / dx)
        if not n % 2:
            n += 1
        dx = yend/n
        return dx
    def createBlocks(self,x,y,k):
        if x<0.0:
            if y>self.h/2:
                k=3
            elif y<self.h/2:
                k=4
        elif x>self.l:
            if y>self.h/2:
                k=5
            elif y<self.h/2:
                k=6
            
            #if z==0
            #tbd
        else:
            if y>self.h/2:
                k=1
            elif y<self.h/2:
                k=2
        return k
    def createAngles(self,y,angle):

        if y<self.h/2:
            angle_y = angle[0]
        else:
            angle_y = angle[1]

        return angle_y
    def createModel(self, TwoD, xend, yend, zend, dx, angle = [0,0]):
        geo = Geometry()
        rot = True
        if angle[0]==angle[1] and angle[1] == 0:
            rot = False

        if TwoD:
            x,y,z = geo.createPoints(coor = [-3*dx[0],xend+3*dx[0],0,yend,0,0], dx = [dx[0],dx[1],1])
        else:
            x,y,z = geo.createPoints(coor = [-3*dx[0],xend+3*dx[0],0,yend,0,zend], dx = [dx[0],dx[1],dx[2]])

        vol = np.zeros(len(x))
        k = np.ones(len(x))
        if rot:
            angle_x = np.zeros(len(x))
            angle_y = np.zeros(len(x))
            angle_z = np.zeros(len(x))
        for idx in range(0, len(x)):
            
            k[idx] = self.createBlocks(x[idx],y[idx],k[idx])
            
            if rot:
                angle_y[idx] = self.createAngles(y[idx], angle = angle)
 
            vol[idx] = dx[0]*dx[1]*dx[2]
            if TwoD:
                vol[idx] = dx[0]*dx[1]
        writer = ModelWriter(modelClass = self)

        if rot:
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
        if self.damageDict == '':
            for idx in range(0,blockLen):
                blockDef[idx] = {'Name': 'block_' + str(idx+1), 'material':self.matBlock[idx], 'horizon': self.scal*max([self.dx[0],self.dx[1]]),'damageModel':'','interface':''}
        else:
            for idx in range(0,blockLen):
                blockDef[idx] = {'Name': 'block_' + str(idx+1), 'material':self.matBlock[idx], 'horizon': self.scal*max([self.dx[0],self.dx[1]]),'damageModel':self.damageDict[idx]}
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