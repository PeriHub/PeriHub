import numpy as np

class YAMLcreator(object):
    def __init__(self, filename = 'mesh', nsName = '', solvertype = 'Verlet', bc = {}, damageDict = {}, materialDict = {},blockDef = {}, bondfilters = {}, TwoD = False):
        self.filename = filename
        self.materialDict = materialDict
        self.damageDict = damageDict
        self.blockDef = blockDef
        self.bondfilters = bondfilters
        self.bc = bc
        self.nsfilename = nsName
        self.TwoDstring = 'false'
        self.solvertype = solvertype
        if TwoD:
            self.TwoDstring = 'true'                   
    def loadMesh(self):
        string = '    Discretization:\n'
        string += '        Type: "Text File"\n'
        string += '        Input Mesh File: "' + self.filename +'.txt"\n'    
        return string
    def createBondFilter(self,bondfilters):
        string = '        Bond Filters:\n'

        for idx in range(0, len(bondfilters['Name'])):
            string += '            ' + bondfilters['Name'][idx] +':\n'
            string += '                Type: "Rectangular_Plane"\n'
            string += '                Normal_X: ' + str(bondfilters['Normal'][idx][0]) + '\n'
            string += '                Normal_Y: ' + str(bondfilters['Normal'][idx][1]) + '\n'
            string += '                Normal_Z: ' + str(bondfilters['Normal'][idx][2]) + '\n'
            string += '                Lower_Left_Corner_X: ' + str(bondfilters['Lower_Left_Corner'][idx][0]) + '\n'
            string += '                Lower_Left_Corner_Y: ' + str(bondfilters['Lower_Left_Corner'][idx][1]) + '\n'
            string += '                Lower_Left_Corner_Z: ' + str(bondfilters['Lower_Left_Corner'][idx][2]) + '\n'
            string += '                Bottom_Unit_Vector_X: ' + str(bondfilters['Bottom_Unit_Vector'][idx][0]) + '\n'
            string += '                Bottom_Unit_Vector_Y: ' + str(bondfilters['Bottom_Unit_Vector'][idx][1]) + '\n'
            string += '                Bottom_Unit_Vector_Z: ' + str(bondfilters['Bottom_Unit_Vector'][idx][2]) + '\n'
            string += '                Bottom_Length: ' + str(bondfilters['Bottom_Length'][idx]) + '\n'
            string += '                Side_Length: ' + str(bondfilters['Side_Length'][idx]) + '\n'
        return string
    def material(self, material):
        string = '    Materials:\n'
        aniso = False
        for mat in material:
            string += '        ' + mat +':\n'
            string += '            Material Model: "' + material[mat]['MatType'] + '"\n'
            string += '            Tension pressure separation for damage model: false\n'
            string += '            Plane Stress: ' + self.TwoDstring + '\n'
            for param in material[mat]['Parameter']:
                string += '            ' + param + ': ' + str(material[mat]['Parameter'][param]) + '\n'
                if param == 'C11':
                    aniso = True
            if aniso:
                # needed for time step estimation
                string += '            Young' + "'" + 's Modulus: 210000.0\n'
                string += '            Poisson' + "'" + 's Ratio:" 0.3\n'
                string += '            Material Symmetry: Anisotropic\n'   
            string += '            Stabilizaton Type: "Global Stiffness"\n'
            string += '            Thickness: 10.0\n'
            string += '            Hourglass Coefficient: 1.0\n'
        return string  
    def blocks(self,blockDef):
        string = '    Blocks:\n'
        for idx in range(0, len(blockDef['Material'])):
            string += '        block_' + str(idx+1) + ':\n'
            string += '            Block Names: "block_' + str(idx+1) + '"\n'
            string += '            Material: "' + blockDef['Material'][idx] + '"\n'
            if blockDef['Damage'][idx] != '':
                string += '            Damage Model: "' + blockDef['Damage'][idx] + '"\n'
            string += '            Horizon: ' + str(blockDef['Horizon'][idx]) + '\n'
        return string
    def damage(self,damageDict):
        string = '    Damage Models:\n'
        for dam in damageDict:
            string += '        ' + dam + ':\n'
            string += '            Damage Model: "Critical Energy Correspondence"\n'
            string += '            Critical Energy: ' + str(damageDict[dam]['Energy']) + '\n'
            string += '            Interblock damage energy: ' + str(damageDict[dam]['InferaceEnergy']) + '\n'
            string += '            Plane Stress: '+ self.TwoDstring +'\n'
            string += '            Only Tension: true\n'
            string += '            Detached Nodes Check: true\n'
            string += '            Thickness: 10.0\n'
            string += '            Hourglass Coefficient: 1.0\n'
            string += '            Stabilizaton Type: "Global Stiffness"\n'
        return string
    def solver(self, solvertype):
        string = '    Solver:\n'
        string += '        Verbose: false\n'
        string += '        Initial Time: 0.0\n'
        string += '        Final Time: 0.075\n'
        if(solvertype=='Verlet'):
            string += '        Verlet:\n'
            string += '            Safety Factor: 0.95\n'
            string += '            Numerical Damping: 0.000005\n'
        elif(solvertype=='NOXQuasiStatic'):
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
    def boundaryCondition(self,nsName, bc):
        string = '    Boundary Conditions:\n'
        for idx in range(0, bc['NNodesets']):
            string += '        Node Set ' + str(idx+1) +': "' + nsName + '_' + str(idx+1) + '.txt' + '"\n'
        bcDict = bc['BCDef']
        for idx in range(0, len(bcDict['NS'])):
            string += '        BC_' + str(idx+1) + ':\n'
            string += '            Type: "' + bcDict['Type'][idx] + '"\n'
            string += '            Node Set: "Node Set ' + str(bcDict['NS'][idx]) + '"\n'
            string += '            Coordinate: "' + bcDict['Direction'][idx] + '"\n'
            string += '            Value: "' + str(bcDict['Value'][idx]) + '*t"\n'
        return string
    def createYAML(self):
        string = 'Peridigm:\n'
        string += self.loadMesh()

        if len(self.bondfilters['Name'])>0:
            string += self.createBondFilter(self.bondfilters)
        string += self.material(self.materialDict)
        if len(self.damageDict)>0:
            string += self.damage(self.damageDict)
        string += self.blocks(self.blockDef)
        string += self.boundaryCondition(self.nsfilename,self.bc)
        string += self.solver(self.solvertype)
        '''
        string += '    Compute Class Parameters:\n'
        string += '        External Displacement:\n'
        string += '            Compute Class: "Block_Data"\n'
        string += '            Calculation Type: "Minimum"\n'
        string += '            Block: "block_4"\n'
        string += '            Variable: "Displacement"\n'
        string += '            Output Label: "External_Displacement"\n'
        '''
        string += '    Output:\n'
        string += '        Output File Type: "ExodusII"\n'
        string += '        Output Format: "BINARY"\n'
        string += '        Output Filename: "' + self.filename + '"\n'
        string += '        Output Frequency: 7500\n'
        string += '        Parallel Write: true\n'
        string += '        Output Variables:\n'
        string += '            Displacement: true\n'
        string += '            Partial_Stress: true\n'
        string += '            Damage: true\n'
        string += '            Number_Of_Neighbors: true\n'
        string += '            Force: true\n'
        return string