import numpy as np

class YAMLcreator(object):
    def __init__(self, modelWriter, blockDef = {}):
        self.filename = modelWriter.filename
        self.finalTime = modelWriter.finalTime
        self.materialDict = modelWriter.materialDict
        self.damageDict = modelWriter.damageDict
        self.computeDict = modelWriter.computeDict
        self.outputDict = modelWriter.outputDict
        self.blockDef = blockDef
        self.bondfilters = modelWriter.bondfilters
        self.bc = modelWriter.bcDict
        self.nsName = modelWriter.nsName
        self.TwoD = modelWriter.TwoD
        self.solvertype = modelWriter.solvertype
        self.frequency = modelWriter.frequency
        self.initStep = modelWriter.initStep              
    def loadMesh(self):
        string = '    Discretization:\n'
        string += '        Type: "Text File"\n'
        string += '        Input Mesh File: "' + self.filename +'.txt"\n'    
        return string
    def createBondFilter(self):
        string = '        Bond Filters:\n'

        for idx in range(0, len(self.bondfilters['Name'])):
            string += '            ' + self.bondfilters['Name'][idx] +':\n'
            string += '                Type: "Rectangular_Plane"\n'
            string += '                Normal_X: ' + str(self.bondfilters['Normal'][idx][0]) + '\n'
            string += '                Normal_Y: ' + str(self.bondfilters['Normal'][idx][1]) + '\n'
            string += '                Normal_Z: ' + str(self.bondfilters['Normal'][idx][2]) + '\n'
            string += '                Lower_Left_Corner_X: ' + str(self.bondfilters['Lower_Left_Corner'][idx][0]) + '\n'
            string += '                Lower_Left_Corner_Y: ' + str(self.bondfilters['Lower_Left_Corner'][idx][1]) + '\n'
            string += '                Lower_Left_Corner_Z: ' + str(self.bondfilters['Lower_Left_Corner'][idx][2]) + '\n'
            string += '                Bottom_Unit_Vector_X: ' + str(self.bondfilters['Bottom_Unit_Vector'][idx][0]) + '\n'
            string += '                Bottom_Unit_Vector_Y: ' + str(self.bondfilters['Bottom_Unit_Vector'][idx][1]) + '\n'
            string += '                Bottom_Unit_Vector_Z: ' + str(self.bondfilters['Bottom_Unit_Vector'][idx][2]) + '\n'
            string += '                Bottom_Length: ' + str(self.bondfilters['Bottom_Length'][idx]) + '\n'
            string += '                Side_Length: ' + str(self.bondfilters['Side_Length'][idx]) + '\n'
        return string
    def material(self):
        string = '    Materials:\n'
        aniso = False
        for mat in self.materialDict:
            string += '        ' + mat['Name'] +':\n'
            string += '            Material Model: "' + mat['MatType'] + '"\n'
            string += '            Tension pressure separation for damage model: ' + str(mat['tensionSeparation']) + '\n'
            string += '            Plane Stress: ' + str(self.TwoD) + '\n'
            for param in mat['Parameter']:
                string += '            ' + param + ': ' + str(np.format_float_scientific(mat['Parameter'][param]['value'])) + '\n'
                if param == 'C11':
                    aniso = True
            if aniso:
                # needed for time step estimation
                string += '            Young' + "'" + 's Modulus: ' + str(float(mat['youngsModulus'])) + '\n'  
                string += '            Poisson' + "'" + 's Ratio: ' + str(float(mat['poissonsRatio'])) + '\n'  
                string += '            Material Symmetry: "' + mat['materialSymmetry'] + '"\n'  
            string += '            Stabilizaton Type: "' + mat['stabilizatonType'] + '"\n'
            string += '            Thickness: ' + str(float(mat['thickness'])) + '\n'
            string += '            Hourglass Coefficient: ' + str(float(mat['hourglassCoefficient'])) + '\n'
        return string  
    def blocks(self):
        string = '    Blocks:\n'
        for block in self.blockDef:
            string += '        ' + block['Name'] + ':\n'
            string += '            Block Names: "' + block['Name'] + '"\n'
            string += '            Material: "' + block['material'] + '"\n'
            if block['damageModel'] != '':
                string += '            Damage Model: "' + block['damageModel'] + '"\n'
            string += '            Horizon: ' + str(block['horizon']) + '\n'
            if block['interface'] != '':
                string += '            Interface: ' + str(block['interface']) + '\n'
        return string
    def damage(self):
        string = '    Damage Models:\n'
        for dam in self.damageDict:
            string += '        ' + dam['Name'] + ':\n'
            string += '            Damage Model: "' + str(dam['damageModel']) + '"\n'
            if dam['damageModel'] =='Critical Energy Correspondence':
                string += '            Critical Energy: ' + str(float(dam['criticalEnergy'])) + '\n'
                if "interblockdamageEnergy" in dam:
                    string += '            Interblock damage energy: ' + str(float(dam['interblockdamageEnergy'])) + '\n'
            else:
                string += '            Critical Stretch: ' + str(float(dam['criticalStretch'])) + '\n'
            string += '            Plane Stress: '+ str(self.TwoD) +'\n'
            string += '            Only Tension: '+ str(dam['onlyTension']) +'\n'
            string += '            Detached Nodes Check: '+ str(dam['detachedNodesCheck']) +'\n'
            string += '            Thickness: ' + str(float(dam['thickness'])) + '\n'
            string += '            Hourglass Coefficient: ' + str(float(dam['hourglassCoefficient'])) + '\n'
            string += '            Stabilizaton Type: "' + str(dam['stabilizatonType']) + '"\n'
        return string
    def solver(self):
        string = '    Solver:\n'
        string += '        Verbose: false\n'
        string += '        Initial Time: 0.0\n'
        string += '        Final Time: '+ str(self.finalTime) +'\n'
        if(self.solvertype=='Verlet'):
            string += '        Verlet:\n'
            string += '            Safety Factor: 0.95\n'
            string += '            Numerical Damping: 0.000005\n'
        elif(self.solvertype=='NOXQuasiStatic'):
            string += '        Peridigm Preconditioner: "None"\n'
            string += '        NOXQuasiStatic:\n'
            string += '            Nonlinear Solver: "Line Search Based"\n'
            string += '            Number of Load Steps: 100\n'
            string += '            Max Solver Iterations: 50\n'
            string += '            Relative Tolerance: 1.0e-8\n'
            string += '            Max Age Of Prec: 100\n'
            string += '            Direction:\n'
            string += '                 Method: "Newton"\n'
            string += '                 Newton:\n'
            string += '                      Linear Solver:\n'
            string += '                           Jacobian Operator: "Matrix-Free"\n'
            string += '                           Preconditioner: "None"\n'
            string += '            Line Search:\n'
            string += '                 Method: "Polynomial"\n'
            string += '            Switch to Verlet:\n'
            string += '                 Safety Factor: 0.95\n'
            string += '                 Numerical Damping: 0.000005\n'
            string += '                 Output Frequency: 7500\n'
        else:
            string += '        Verlet:\n'
            string += '            Safety Factor: 0.95\n'
            string += '            Numerical Damping: 0.000005\n'
        return string
    def boundaryCondition(self):
        string = '    Boundary Conditions:\n'
        for idx in range(0, self.bc['NNodesets']):
            string += '        Node Set ' + str(idx+1) +': "' + self.nsName + '_' + str(idx+1) + '.txt' + '"\n'
        bcDict = self.bc['BCDef']
        for idx in range(0, len(bcDict['NS'])):
            string += '        BC_' + str(idx+1) + ':\n'
            string += '            Type: "' + bcDict['Type'][idx] + '"\n'
            string += '            Node Set: "Node Set ' + str(bcDict['NS'][idx]) + '"\n'
            string += '            Coordinate: "' + bcDict['Direction'][idx] + '"\n'
            string += '            Value: "' + str(bcDict['Value'][idx]) + '*t"\n'
        return string
    def compute(self):
        string = '    Compute Class Parameters:\n'
        for out in self.computeDict['Compute Class Parameters']:
            string += '        ' + out['Name'] + ':\n'
            string += '            Compute Class: "Block_Data"\n'
            string += '            Calculation Type: "' + out['Calculation Type'] + '"\n'
            string += '            Block: "' + out['Block'] + '"\n'
            string += '            Variable: "' + out['Variable'] + '"\n'
            string += '            Output Label: "' + out['Name'] + '"\n'
        return string
    def output(self):
        idx = 0
        string=''
        for out in self.outputDict:
            string += '    ' + out['Name'] + ':\n'
            string += '        Output File Type: "ExodusII"\n'
            string += '        Output Format: "BINARY"\n'
            string += '        Output Filename: "' + self.filename +'_' + out['Name'] +'"\n'
            if out['InitStep'] !=0: 
                string += '        Initial Output Step: ' + str(out['InitStep']) + '\n'
            string += '        Output Frequency: ' + str(out['Frequency']) + '\n'
            string += '        Parallel Write: true\n'
            string += '        Output Variables:\n'
            if out['Displacement']: 
                string += '            Displacement: true\n'
            if out['Partial_Stress']: 
                string += '            Partial_Stress: true\n'
            if out['Damage']: 
                string += '            Damage: true\n'
            if out['Number_Of_Neighbors']: 
                string += '            Number_Of_Neighbors: true\n'
            if out['Force']: 
                string += '            Force: true\n'
            if out['External_Displacement']: 
                string += '            External_Displacement: true\n'
            if out['External_Force']: 
                string += '            External_Force: true\n'
            idx +=1
        return string
    def createYAML(self):
        string = 'Peridigm:\n'
        string += self.loadMesh()

        if len(self.bondfilters['Name'])>0:
            string += self.createBondFilter()
        string += self.material()
        if len(self.damageDict)>0:
            string += self.damage()
        string += self.blocks()
        string += self.boundaryCondition()
        string += self.solver()
        string += self.compute()
        string += self.output()

        return string