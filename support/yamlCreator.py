import numpy as np

class YAMLcreator(object):
    def __init__(self, modelWriter, blockDef = {}):
        self.filename = modelWriter.filename
        self.finalTime = modelWriter.finalTime
        self.materialDict = modelWriter.materialDict
        self.damageDict = modelWriter.damageDict
        self.outputDict = modelWriter.outputDict
        self.blockDef = blockDef
        self.bondfilters = modelWriter.bondfilters
        self.bc = modelWriter.bcDict
        self.nsName = modelWriter.nsName
        self.TwoD = modelWriter.TwoD
        self.onlyTension = modelWriter.onlyTension
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
            string += '        ' + mat +':\n'
            string += '            Material Model: "' + self.materialDict[mat]['MatType'] + '"\n'
            string += '            Tension pressure separation for damage model: false\n'
            string += '            Plane Stress: ' + str(self.TwoD) + '\n'
            for param in self.materialDict[mat]['Parameter']:
                string += '            ' + param + ': ' + str(np.format_float_scientific(self.materialDict[mat]['Parameter'][param])) + '\n'
                if param == 'C11':
                    aniso = True
            if aniso:
                # needed for time step estimation
                string += '            Young' + "'" + 's Modulus: 210000.0\n'
                string += '            Poisson' + "'" + 's Ratio: 0.3\n'
                string += '            Material Symmetry: Anisotropic\n'   
            string += '            Stabilizaton Type: "Global Stiffness"\n'
            string += '            Thickness: 10.0\n'
            string += '            Hourglass Coefficient: 1.0\n'
        return string  
    def blocks(self):
        string = '    Blocks:\n'
        for idx in range(0, len(self.blockDef['Material'])):
            string += '        block_' + str(idx+1) + ':\n'
            string += '            Block Names: "block_' + str(idx+1) + '"\n'
            string += '            Material: "' + self.blockDef['Material'][idx] + '"\n'
            if self.blockDef['Damage'][idx] != '':
                string += '            Damage Model: "' + self.blockDef['Damage'][idx] + '"\n'
            string += '            Horizon: ' + str(self.blockDef['Horizon'][idx]) + '\n'
            if self.blockDef['Interface'][idx] != -1:
                string += '            Interface: ' + str(self.blockDef['Interface'][idx]) + '\n'
        return string
    def damage(self):
        string = '    Damage Models:\n'
        for dam in self.damageDict:
            string += '        ' + dam + ':\n'
            string += '            Damage Model: "Critical Energy Correspondence"\n'
            string += '            Critical Energy: ' + str(self.damageDict[dam]['Energy']) + '\n'
            if "InterfaceEnergy" in self.damageDict[dam]:
                string += '            Interblock damage energy: ' + str(self.damageDict[dam]['InterfaceEnergy']) + '\n'
            string += '            Plane Stress: '+ str(self.TwoD) +'\n'
            string += '            Only Tension: '+ str(self.onlyTension) +'\n'
            string += '            Detached Nodes Check: true\n'
            string += '            Thickness: 10.0\n'
            string += '            Hourglass Coefficient: 1.0\n'
            string += '            Stabilizaton Type: "Global Stiffness"\n'
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
    def output(self):
        idx = 0
        string=''
        for out in self.outputDict:
            string += '    ' + out + ':\n'
            string += '        Output File Type: "ExodusII"\n'
            string += '        Output Format: "BINARY"\n'
            string += '        Output Filename: "' + self.filename +'_' + out +'"\n'
            if self.initStep[idx] !=0: 
                string += '        Initial Output Step: ' + str(self.initStep[idx]) + '\n'
            string += '        Output Frequency: ' + str(self.frequency[idx]) + '\n'
            string += '        Parallel Write: true\n'
            string += '        Output Variables:\n'
            if "Displacement" in self.outputDict[out]: 
                string += '            Displacement: true\n'
            if "Partial_Stress" in self.outputDict[out]: 
                string += '            Partial_Stress: true\n'
            if "Damage" in self.outputDict[out]: 
                string += '            Damage: true\n'
            if "Number_Of_Neighbors" in self.outputDict[out]: 
                string += '            Number_Of_Neighbors: true\n'
            if "Force" in self.outputDict[out]: 
                string += '            Force: true\n'
            if "External_Displacement" in self.outputDict[out]: 
                string += '            External_Displacement: true\n'
            if "External_Force" in self.outputDict[out]: 
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

        string += '    Compute Class Parameters:\n'
        string += '        External Displacement:\n'
        string += '            Compute Class: "Block_Data"\n'
        string += '            Calculation Type: "Minimum"\n'
        string += '            Block: "block_7"\n'
        string += '            Variable: "Displacement"\n'
        string += '            Output Label: "External_Displacement"\n'
        string += '        External Loads:\n'
        string += '            Compute Class: "Block_Data"\n'
        string += '            Calculation Type: "Sum"\n'
        string += '            Block: "block_7"\n'
        string += '            Variable: "Force"\n'
        string += '            Output Label: "External_Force"\n'

        string += self.output()

        return string