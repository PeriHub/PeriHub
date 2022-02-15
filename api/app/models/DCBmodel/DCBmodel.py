import numpy as np
from support.baseModels import Adapt, Block, BondFilters, BoundaryConditions, Compute, Damage, Material, Output, Newton, Solver, Verlet
from support.modelWriter import ModelWriter
from support.geometry import Geometry

class DCBmodel(object):
    def __init__(self, xend = 0.045, yend = 0.01, zend = 0.003, dx=[0.001,0.001,0.001], 
    filename = 'DCBmodel', TwoD = False, rot = 'False', angle = [0,0], 
    material = '', damage = '', block = '', bc = '', bf = '', compute = '', output = '', solver = '', username = '', maxNodes = 100000, ignoreMesh = False):
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
        self.DiscType = 'txt'
        self.TwoD = TwoD
        self.nsList = [3,4]
        self.dx   = dx
        self.xbegin = -0.005
        self.ybegin = -yend
        self.zbegin = -zend
        self.xend = xend + dx[0]
        self.yend = yend + dx[1]
        self.zend = zend + dx[2]
        self.rot = rot
        self.blockDef = block
        self.username = username
        self.maxNodes = maxNodes
        self.ignoreMesh = ignoreMesh
        if self.TwoD:
            self.zbegin = 0
            self.zend = 0
            self.dx[2] = 1
        numberOfBlocks = 4

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
            self.outputDict = [outputDict1, outputDict2]
        else:
            self.outputDict = output
        
        if material=='':
            i=0
            for material in matNameList:
                matDict = Material(id=i+1, Name=material, MatType='Linear Elastic Correspondence', density=1.95e-07, bulkModulus=None, shearModulus=None, youngsModulus=2.1e+5, poissonsRatio=0.3, tensionSeparation=False, nonLinear=True, planeStress=True, materialSymmetry='Isotropic', stabilizatonType='Global Stiffness', thickness=10.0, hourglassCoefficient=1.0, actualHorizon=None, yieldStress=None, Parameter=[] ,Properties=[])
                i+=1
                self.materialDict.append(matDict)
        else:
            self.angle = angle
            self.materialDict = material
        
        if(bf==''): 
            bf1 = BondFilters(id=1, Name='bf_1', type='Rectangular_Plane', normalX=0.0, normalY=1.0, normalZ=0.0, lowerLeftCornerX=-0.06, lowerLeftCornerY=0.0, lowerLeftCornerZ=-0.01, bottomUnitVectorX=1.0, bottomUnitVectorY=0.0, bottomUnitVectorZ=0.0, bottomLength=0.01, sideLength=0.01, centerX=0.0, centerY=1.0, centerZ=0.0, radius=1.0, show=True)
            self.bondfilters = [bf1]
        else:
            self.bondfilters = bf

        if(bc==''):
            bc1 = BoundaryConditions(id=1, Name='BC_1', NodeSets=None, boundarytype='Prescribed Displacement', blockId=3, coordinate='y', value='0.004*t')
            bc2 = BoundaryConditions(id=2, Name='BC_2', NodeSets=None, boundarytype='Prescribed Displacement', blockId=4, coordinate='y', value='-0.004*t')
            bc3 = BoundaryConditions(id=3, Name='BC_3', NodeSets=None, boundarytype='Prescribed Displacement', blockId=1, coordinate='z', value='0*t')
            bc4 = BoundaryConditions(id=3, Name='BC_4', NodeSets=None, boundarytype='Prescribed Displacement', blockId=2, coordinate='z', value='0*t')
            self.bcDict = [bc1,bc2,bc3,bc4]
        else:
            self.bcDict = bc

        if(solver==''):
            self.solverDict = Solver(verbose=False, initialTime=0.0, finalTime=0.075, fixedDt=None, solvertype='Verlet', safetyFactor=0.95, numericalDamping=0.000005, peridgimPreconditioner='None', nonlinearSolver='Line Search Based', numberofLoadSteps=100, maxSolverIterations=50, relativeTolerance=1e-8, maxAgeOfPrec=100, directionMethod='Newton', newton=Newton(), lineSearchMethod='Polynomial', verletSwitch=False, verlet=Verlet(), stopAfterDamageInitation=False, stopBeforeDamageInitation=False, adaptivetimeStepping=False, adapt=Adapt(), filetype='yaml')
        else:
            self.solverDict = solver

        self.damBlock = ['']*numberOfBlocks
        self.damBlock[0] = 'PMMADamage'
        self.damBlock[1] = 'PMMADamage'

        self.intBlockId = ['']*numberOfBlocks
        self.matBlock = ['PMMA']*numberOfBlocks

    def createLoadIntroNode(self,x,y, k):
        k = np.where(np.logical_and(x < self.xbegin+self.dx[0]*3, y > 0), 3, k)
        k = np.where(np.logical_and(x < self.xbegin+self.dx[0]*3, y < 0), 4, k)
        return k

    def createBlock(self,y,k):
        k = np.where(y > 0, 1, k)
        k = np.where(y > 0, 2, k)
        return k
        
    def createModel(self):
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
            geo = Geometry()
            
            x,y,z = geo.createPoints(coor = [self.xbegin, self.xend, self.ybegin, self.yend, self.zbegin, self.zend], dx = self.dx)

            if len(x)>self.maxNodes:
                return 'The number of nodes (' + str(len(x)) + ') is larger than the allowed ' + str(self.maxNodes)

            vol = np.zeros(len(x))
            k = np.ones(len(x))
            if self.rot:
                angle_x = np.zeros(len(x))
                angle_y = np.zeros(len(x))
                angle_z = np.zeros(len(x))

            k = self.createBlock(y, k)
            k = self.createLoadIntroNode(x, y, k)

            vol =  np.full_like(x, self.dx[0] * self.dx[1] * self.dx[2])
            
            writer = ModelWriter(modelClass = self)
            
            if self.rot:
                model = np.transpose(np.vstack([x.ravel(), y.ravel(), z.ravel(), k.ravel(), vol.ravel(), angle_x.ravel(), angle_y.ravel(), angle_z.ravel()]))
                writer.writeMeshWithAngles(model)
            else:
                model = np.transpose(np.vstack([x.ravel(), y.ravel(), z.ravel(), k.ravel(), vol.ravel()]))
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
