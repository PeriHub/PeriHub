import numpy as np
from support.baseModels import Adapt, Block, BondFilters, BoundaryConditions, Compute, Damage, Material, Output, Newton, Solver, Verlet
from support.modelWriter import ModelWriter
from support.geometry import Geometry
import matplotlib.pyplot as plt
import time
class Dogbone(object):
    def __init__(self, xend = 0.15, h1 = 0.02, h2 = 0.01, zend = 0.001, dx=[0.0005,0.0005,0.0005], 
    filename = 'Dogbone', TwoD = False, structured = True, rot = False, angle = [0,0], 
    material = '', damage = '', block = '', bc = '', bf = '', compute = '', output = '', solver = '', username = '', maxNodes = 100000, ignoreMesh = False):
        '''
            definition der blocks
            k =
            1 X Zero Node Set
            2 No Damage
            3 Damage
            4 No Damage
            5 Load Node Set
        '''
        start_time = time.time()
        
        self.filename = filename
        self.scal = 4.01
        self.DiscType = 'txt'
        self.TwoD = TwoD
        self.nsList = [3,4]
        self.dx   = dx
        self.xend = xend
        self.h1 = h1
        self.h2 = h2
        self.structured = structured
        self.rot = rot
        self.blockDef = block
        self.username = username
        self.maxNodes = maxNodes
        self.ignoreMesh = ignoreMesh
        if self.TwoD:
            self.zend = 1
            self.dx[2] = 1
        else:
            self.zend = zend + dx[2]

        numberOfBlocks = 5

        ''' Definition of model
        '''

        matNameList = ['PMMA']
        self.materialDict = []
        self.angle = [0,0]
        if damage=='':
            damageDict = Damage(id=1, Name='PMMADamage', damageModel='Critical Energy Correspondence', criticalStretch=10,criticalEnergy=5.1, interblockdamageEnergy=0.01, planeStress=True, onlyTension=True, detachedNodesCheck=True, thickness=10, hourglassCoefficient=1.0, stabilizatonType='Global Stiffness')
            self.damageDict = [damageDict]
        else:
            self.damageDict = damage
        
        if compute=='':
            computeDict1 = Compute(id=1, Name='External_Displacement', variable='Displacement', calculationType='Minimum', blockName='block_3')
            computeDict2 = Compute(id=2, Name='External_Force', variable='Force', calculationType='Sum', blockName='block_3')
            self.computeDict = [computeDict1, computeDict2]
        else:
            self.computeDict = compute
       
        if output=='':
            outputDict1 = Output(id=1, Name='Output1', Displacement=True, Force=True, Damage=True, Velocity=True, Partial_Stress=False, External_Force=False, External_Displacement=False, Number_Of_Neighbors=False, Frequency=500, InitStep=0)
            outputDict2 = Output(id=2, Name='Output2', Displacement=False, Force=False, Damage=True, Velocity=False, Partial_Stress=True, External_Force=True, External_Displacement=True, Number_Of_Neighbors=False, Frequency=200, InitStep=0)
            self.outputDict = [outputDict1,outputDict2]
        else:
            self.outputDict = output
        
        if material=='':
            i=0
            for material in matNameList:
                matDict = Material(id=i+1, Name=material, MatType='Linear Elastic Correspondence', density=200000.0, bulkModulus=None, shearModulus=None, youngsModulus=1.5e9, poissonsRatio=0.3, tensionSeparation=False, nonLinear=True, planeStress=True, materialSymmetry='Isotropic', stabilizatonType='Global Stiffness', thickness=10.0, hourglassCoefficient=1.0, actualHorizon=None, yieldStress=31.3e4, Parameter=[] ,Properties=[])
                i+=1
                self.materialDict.append(matDict)
        else:
            self.angle = angle
            self.materialDict = material
        

        if(bf==''): 
            self.bondfilters = []
        else:
            self.bondfilters = bf

        if(bc==''): 
            bc1 = BoundaryConditions(id=1, Name='BC_1', NodeSets=None, boundarytype='Prescribed Displacement', blockId=1, coordinate='x', value='0*t')
            bc2 = BoundaryConditions(id=2, Name='BC_2', NodeSets=None, boundarytype='Prescribed Displacement', blockId=5, coordinate='x', value='10*t')
            self.bcDict = [bc1,bc2]
        else:
            self.bcDict = bc

        if(solver==''):
            self.solverDict = Solver(verbose=False, initialTime=0.0, finalTime=0.075, fixedDt=None, solvertype='Verlet', safetyFactor=0.95, numericalDamping=0.000005, peridgimPreconditioner='None', nonlinearSolver='Line Search Based', numberofLoadSteps=100, maxSolverIterations=50, relativeTolerance=1e-8, maxAgeOfPrec=100, directionMethod='Newton', newton=Newton(), lineSearchMethod='Polynomial', verletSwitch=False, verlet=Verlet(), stopAfterDamageInitation=False, stopBeforeDamageInitation=False, adaptivetimeStepping=False, adapt=Adapt(), filetype='yaml')
        else:
            self.solverDict = solver

        self.damBlock = ['']*numberOfBlocks
        self.damBlock[2] = 'PMMADamage'

        self.intBlockId = ['']*numberOfBlocks
        self.matBlock = ['PMMA']*numberOfBlocks
        
        print('Initialized in ' + "%.2f seconds" % (time.time() - start_time) )

    def createModel(self):
        
        geo = Geometry()
        bc = 0.002
        R = 0.076; l2 = 0.057
        dh =  (self.h1-self.h2)/2
        dl = np.sqrt(R*R-(R-dh)**2)
        l1 = (self.xend - 2*dl - l2)/2
        alpha = np.arccos((R-dh)/R)*180/np.pi

        x0 = np.arange(0,self.xend, self.dx[0])
        y0 = np.arange(-self.h1/2 - self.dx[1],self.h1/2 + self.dx[1], self.dx[1])
        z0 = np.arange(0,self.zend, self.dx[2])
            
        num = len(x0)*len(y0)*len(z0)
        
        if num>self.maxNodes:
            return 'The number of nodes (' + str(num) + ') is larger than the allowed ' + str(self.maxNodes)

        if self.ignoreMesh == True and self.blockDef!='':
        
            writer = ModelWriter(modelClass = self)
            for idx in range(0,len(self.blockDef)):
                self.blockDef[idx].horizon= self.scal*max([self.dx[0],self.dx[1]])
            blockDef = self.blockDef

            try:
                writer.createFile(blockDef)
            except TypeError as e:
                return str(e)

        else:

            if self.structured:
                nn = 2*int((self.h1/self.dx[1])/2)+1
                numRows = int((nn-1)/2)
                fh2 = ((2*self.dx[1]*(numRows)+self.h2-self.h1)/(self.dx[1]*(numRows)))
                x = []
                y = []
                z = []
                k = []
                for zval in z0:
                    for i in range(0,numRows):
                        h1 = self.h1-self.dx[1]*i*2
                        h2 = self.h2-self.dx[1]*i*fh2
                        # R1 = R+0.03*i
                        dh1 =  (h1-h2)/2
                        
                        alpha1 = np.arccos((R-dh1)/R)*180/np.pi

                        
                        topSurf, bottomSurf = geo.createBoundaryCurve(h = h1/2, l1 = l1, R = R, l2 = l2, alphaMax = alpha, alphaMax1 = alpha1, dl = dl, dh = dh1)
                        blockDef = np.array([0, bc, l1, l1+2*dl+l2, self.xend - bc])

                        x = np.concatenate((x,x0))
                        x = np.concatenate((x,x0))
                        y = np.concatenate((y,topSurf(x0)))
                        y = np.concatenate((y,bottomSurf(x0)))
                        z = np.concatenate((z,np.full_like(x0, zval)))
                        z = np.concatenate((z,np.full_like(x0, zval)))
                        for xval in x0:
                            for idx,val in enumerate(blockDef): 
                                if geo.checkValGreater(xval,val): matNum = idx + 1
                            k.append(matNum)
                        for xval in x0:
                            for idx,val in enumerate(blockDef): 
                                if geo.checkValGreater(xval,val): matNum = idx + 1
                            k.append(matNum)
                        plt.scatter(x0, topSurf(x0))
                        plt.scatter(x0, bottomSurf(x0))

                    x = np.concatenate((x,x0))
                    y = np.concatenate((y,np.zeros_like(x0)))
                    z = np.concatenate((z,np.full_like(x0, zval)))
                # plt.scatter(x0, np.zeros_like(x0))
                    for xval in x0:
                        for idx,val in enumerate(blockDef): 
                            if geo.checkValGreater(xval,val): matNum = idx + 1
                        k.append(matNum)


                # plt.show()

                vol = np.full_like(x, self.dx[0]*self.dx[0])

            else:
                topSurf, bottomSurf = geo.createBoundaryCurveOld(h = self.h1/2, l1 = l1, R = R, l2 = l2, alphaMax = alpha, dl = dl, dh = dh)
                blockDef = np.array([0, bc, l1, l1+2*dl+l2, self.xend - bc])
                
                # plt.scatter(x0, topSurf(x0))
                # plt.scatter(x0, bottomSurf(x0))
                # plt.show()
                # num = len(x0)*len(y0)*len(z0)
                x = []
                y = []
                z = []
                k = []
                matNum = 0
                for xval in x0:
                    for yval in y0:
                        for zval in z0:
                            if geo.checkValGreater(yval,bottomSurf(xval)) and geo.checkValLower(yval,topSurf(xval)):
                                for idx,val in enumerate(blockDef):
                                    if geo.checkValGreater(xval,val): matNum = idx + 1
                                x.append(xval)
                                y.append(yval)
                                z.append(zval)
                                k.append(matNum)
                
                # plt.scatter(x0, np.zeros_like(x0))
                # plt.scatter(np.zeros_like(y0),y0)
                plt.scatter(x, y)
                plt.show()
                vol = np.full_like(x, self.dx[0]*self.dx[0])

            if self.rot:
                angle_x = np.zeros(len(x))
                angle_y = np.zeros(len(x))
                angle_z = np.zeros(len(x))
            
            writer = ModelWriter(modelClass = self)
            
            if self.rot:
                model = np.transpose(np.vstack([np.array(x).ravel(), np.array(y).ravel(), np.array(z).ravel(), np.array(k).ravel(), vol.ravel(), angle_x.ravel(), angle_y.ravel(), angle_z.ravel()]))
                writer.writeMeshWithAngles(model)
            else:
                model = np.transpose(np.vstack([np.array(x).ravel(), np.array(y).ravel(), np.array(z).ravel(), np.array(k).ravel(), vol.ravel()]))
                writer.writeMesh(model)
            writer.writeNodeSets(model)
            
            blockLen = int(max(k))
            
            writeReturn = self.writeFILE(writer = writer, blockLen = blockLen)

            if writeReturn!=0:
                return writeReturn
        
        return 'Model created'

    def createBlockdef(self,blockLen):
        blockDict=[]
        for idx in range(0,blockLen):
            blockDef = Block(id=1, Name= 'block_' + str(idx+1), material=self.matBlock[idx], damageModel=self.damBlock[idx], horizon= self.scal*max([self.dx[0],self.dx[1]]), interface=self.intBlockId[idx], show=False)
            blockDict.append(blockDef)
        # 3d tbd
        return blockDict
    def writeFILE(self, writer, blockLen):
        
        if self.blockDef=='':
            blockDef = self.createBlockdef(blockLen)
        else:
            for idx in range(0,len(self.blockDef)):
                self.blockDef[idx].horizon= self.scal*max([self.dx[0],self.dx[1]])
            blockDef = self.blockDef

        try:
            writer.createFile(blockDef)
        except TypeError as e:
            return str(e)
        return 0
