import numpy as np

class XMLcreator(object):
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
        string = '    <ParameterList name="Discretization">\n'
        string += '        <Parameter name="Type" type="string" value="Text File" />\n'
        string += '        <Parameter name="Input Mesh File" type="string" value="' + self.filename +'.txt"/>\n'    
        return string
    def createBondFilter(self,bondfilters):
        string = '        <ParameterList name="Bond Filters">\n'
        
        
        for idx in range(0, len(bondfilters['Name'])):
            string += '            <ParameterList name="' + bondfilters['Name'][idx] +'">\n'
            string += '                <Parameter name="Type" type="string" value = "Rectangular_Plane"/>\n'
            string += '                <Parameter name="Normal_X" type="double" value="' + str(bondfilters['Normal'][idx][0]) + '"/>\n'
            string += '                <Parameter name="Normal_Y" type="double" value="' + str(bondfilters['Normal'][idx][1]) + '"/>\n'
            string += '                <Parameter name="Normal_Z" type="double" value="' + str(bondfilters['Normal'][idx][2]) + '"/>\n'
            string += '                <Parameter name="Lower_Left_Corner_X" type="double" value="' + str(bondfilters['Lower_Left_Corner'][idx][0]) + '"/>\n'
            string += '                <Parameter name="Lower_Left_Corner_Y" type="double" value="' + str(bondfilters['Lower_Left_Corner'][idx][1]) + '"/>\n'
            string += '                <Parameter name="Lower_Left_Corner_Z" type="double" value="' + str(bondfilters['Lower_Left_Corner'][idx][2]) + '"/>\n'
            string += '                <Parameter name="Bottom_Unit_Vector_X" type="double" value="' + str(bondfilters['Bottom_Unit_Vector'][idx][0]) + '"/>\n'
            string += '                <Parameter name="Bottom_Unit_Vector_Y" type="double" value="' + str(bondfilters['Bottom_Unit_Vector'][idx][1]) + '"/>\n'
            string += '                <Parameter name="Bottom_Unit_Vector_Z" type="double" value="' + str(bondfilters['Bottom_Unit_Vector'][idx][2]) + '"/>\n'
            string += '                <Parameter name="Bottom_Length" type="double" value="' + str(bondfilters['Bottom_Length'][idx]) + '"/>\n'
            string += '                <Parameter name="Side_Length" type="double" value="' + str(bondfilters['Side_Length'][idx]) + '"/>\n'
            string += '            </ParameterList>\n'
        string += '        </ParameterList>\n'
        return string
    def material(self, material):
        string = '    <ParameterList name="Materials">\n'
        aniso = False
        for mat in material:
            string += '        <ParameterList name="' + mat +'">\n'
            string += '            <Parameter name="Material Model" type="string" value="' + material[mat]['MatType'] + '"/>\n'
            string += '            <Parameter name="Tension pressure separation for damage model" type="bool" value="false"/>\n'
            string += '            <Parameter name="Plane Stress" type="bool" value="' + self.TwoDstring + '"/>\n'
            #string += '            <Parameter name="Density" type="double" value="' + str(mat['dens'][idx]) + '"/>\n'
            for param in material[mat]['Parameter']:
                string += '            <Parameter name="'+ param +'" type="double" value="' +str(material[mat]['Parameter'][param]) +'"/>\n'
                if param == 'C11':
                    aniso = True
            if aniso:
                # needed for time step estimation
                string += '            <Parameter name="Young' + "'" + 's Modulus" type="double" value="210000.0"/>\n'
                string += '            <Parameter name="Poisson' + "'" + 's Ratio" type="double" value="0.3"/>\n'
                string += '            <Parameter name="Material Symmetry" type="string" value = "Anisotropic"/>\n'   
            string += '            <Parameter name="Stabilizaton Type" type="string" value="Global Stiffness"/>\n'
            string += '            <Parameter name="Thickness" type="double" value="10.0"/>\n'
            string += '            <Parameter name="Hourglass Coefficient" type="double" value="1.0"/>\n'
            string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'  
        return string  
    def blocks(self,blockDef):
        string = '    <ParameterList name="Blocks">\n'
        for idx in range(0, len(blockDef['Material'])):
            string += '        <ParameterList name="block_' + str(idx+1) + '">\n'
            string += '            <Parameter name="Block Names" type="string" value="block_' + str(idx+1) + '"/>\n'
            string += '            <Parameter name="Material" type="string" value="' + blockDef['Material'][idx] + '"/>\n'
            if blockDef['Damage'][idx] != '':
                string += '            <Parameter name="Damage Model" type="string" value="' + blockDef['Damage'][idx] + '"/>\n'
            string += '            <Parameter name="Horizon" type="double" value="' + str(blockDef['Horizon'][idx]) + '"/>\n'
            string += '        </ParameterList>\n'
        string += '     </ParameterList>\n'
        return string
    def damage(self,damageDict):
        string = '    <ParameterList name="Damage Models">\n'
        for dam in damageDict:
            string += '        <ParameterList name="' + dam + '">\n'
            string += '            <Parameter name="Damage Model" type="string" value="Critical Energy Correspondence"/>\n'
            string += '            <Parameter name="Critical Energy" type="double" value="' + str(damageDict[dam]['Energy']) + '"/>\n'
            string += '            <Parameter name="Plane Stress" type="bool" value="'+ self.TwoDstring +'"/>\n'
            string += '            <Parameter name="Only Tension" type="bool" value="true"/>\n'
            string += '            <Parameter name="Detached Nodes Check" type="bool" value="true"/>\n'
            string += '            <Parameter name="Thickness" type="double" value="10.0"/>\n'
            string += '            <Parameter name="Hourglass Coefficient" type="double" value="1.0"/>\n'
            string += '            <Parameter name="Stabilizaton Type" type="string" value="Global Stiffness"/>\n'
            string += '            <Parameter name="Interblock damage energy" type="double" value="' + str(damageDict[dam]['InferaceEnergy']) + '"/>\n'
            string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        return string
    def solver(self, solvertype):
        string = '    <ParameterList name="Solver">\n'
        string += '        <Parameter name="Verbose" type="bool" value="false"/>\n'
        string += '        <Parameter name="Initial Time" type="double" value="0.0"/>\n'
        string += '        <Parameter name="Final Time" type="double" value="0.075"/>\n'
        if(solvertype=='Verlet'):
            string += '        <ParameterList name="Verlet">\n'
            string += '            <Parameter name="Safety Factor" type="double" value="0.95"/>\n'
            string += '            <Parameter name="Numerical Damping" type="double" value="0.000005"/>\n'
        elif(solvertype=='NOXQuasiStatic'):
            string += '        <Parameter name="Peridigm Preconditioner" type="string" value="None"/>\n'
            string += '        <ParameterList name="NOXQuasiStatic">\n'
            string += '            <Parameter name="Nonlinear Solver" type="string" value="Line Search Based"/>\n'
            string += '            <Parameter name="Number of Load Steps" type="int" value="100"/>\n'
            string += '            <Parameter name="Max Solver Iterations" type="int" value="50"/>\n'
            string += '            <Parameter name="Relative Tolerance" type="double" value="1.0e-8"/>\n'
            string += '            <Parameter name="Max Age Of Prec" type="int" value="100"/>\n'
            string += '            <ParameterList name="Direction">\n'
            string += '                 <Parameter name="Method" type="string" value="Newton"/>\n'
            string += '                 <ParameterList name="Newton">\n'
            string += '                      <ParameterList name="Linear Solver">\n'
            string += '                           <Parameter name="Jacobian Operator" type="string" value="Matrix-Free"/>\n'
            string += '                           <Parameter name="Preconditioner" type="string" value="None"/>\n'
            string += '                      </ParameterList>\n'
            string += '                 </ParameterList>\n'
            string += '            </ParameterList>\n'
            string += '            <ParameterList name="Line Search">\n'
            string += '                 <Parameter name="Method" type="string" value="Polynomial"/>\n'
            string += '            </ParameterList>\n'
            string += '            <ParameterList name="Switch to Verlet">\n'
            string += '                 <Parameter name="Safety Factor" type="double" value="0.95"/>\n'
            string += '                 <Parameter name="Numerical Damping" type="double" value="0.000005"/>\n'
            string += '                 <Parameter name="Output Frequency" type="int" value="7500"/>\n'
            string += '            </ParameterList>\n'
        else:
            string += '        <ParameterList name="Verlet">\n'
            string += '            <Parameter name="Safety Factor" type="double" value="0.95"/>\n'
            string += '            <Parameter name="Numerical Damping" type="double" value="0.000005"/>\n'
        string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        return string
    def boundaryCondition(self,nsName, bc):
        string = '    <ParameterList name="Boundary Conditions">\n'
        for idx in range(0, bc['NNodesets']):
            string += '        <Parameter name="Node Set ' + str(idx+1) +'" type="string" value="' + nsName + '_' + str(idx+1) + '.txt' + '"/>\n'
        bcDict = bc['BCDef']
        for idx in range(0, len(bcDict['NS'])):
            string += '        <ParameterList name="BC_' + str(idx+1) + '">\n'
            string += '            <Parameter name="Type" type="string" value="' + bcDict['Type'][idx] + '"/>\n'
            string += '            <Parameter name="Node Set" type="string" value="Node Set ' + str(bcDict['NS'][idx]) + '"/>\n'
            string += '            <Parameter name="Coordinate" type="string" value="' + bcDict['Direction'][idx] + '"/>\n'
            string += '            <Parameter name="Value" type="string" value="' + str(bcDict['Value'][idx]) + '*t"/>\n'
            string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        return string
    def createXML(self):
        string = '<ParameterList>\n'
        string += self.loadMesh()

        if len(self.bondfilters['Name'])>0:
            string += self.createBondFilter(self.bondfilters)
        string += '    </ParameterList>\n'
        string += self.material(self.materialDict)
        if len(self.damageDict)>0:
            string += self.damage(self.damageDict)
        string += self.blocks(self.blockDef)
        string += self.boundaryCondition(self.nsfilename,self.bc)
        string += self.solver(self.solvertype)
        '''
        string += '    <ParameterList name="Compute Class Parameters">\n'
        string += '        <ParameterList name="External Displacement">\n'
        string += '            <Parameter name="Compute Class" type="string" value="Block_Data"/>\n'
        string += '            <Parameter name="Calculation Type" type="string" value="Minimum"/>\n'
        string += '            <Parameter name="Block" type="string" value="block_4"/>\n'
        string += '            <Parameter name="Variable" type="string" value="Displacement"/>\n'
        string += '            <Parameter name="Output Label" type="string" value="External_Displacement"/>\n'
        string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        '''
        string += '    <ParameterList name="Output">\n'
        string += '        <Parameter name="Output File Type" type="string" value="ExodusII"/>\n'
        string += '        <Parameter name="Output Format" type="string" value="BINARY"/>\n'
        string += '        <Parameter name="Output Filename" type="string" value="' + self.filename + '"/>\n'
        string += '        <Parameter name="Output Frequency" type="int" value="7500"/>\n'
        string += '        <Parameter name="Parallel Write" type="bool" value="true"/>\n'
        string += '        <ParameterList name="Output Variables">\n'
        string += '            <Parameter name="Displacement" type="bool" value="true"/>\n'
        string += '            <Parameter name="Partial_Stress" type="bool" value="true"/>\n'
        string += '            <Parameter name="Damage" type="bool" value="true"/>\n'
        string += '            <Parameter name="Number_Of_Neighbors" type="bool" value="true"/>\n'
        string += '            <Parameter name="Force" type="bool" value="true"/>\n'
        string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        string += '</ParameterList>\n'
        return string