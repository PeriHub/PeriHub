import numpy as np

class XMLcreator(object):
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
        string = '    <ParameterList name="Discretization">\n'
        string += '        <Parameter name="Type" type="string" value="Text File" />\n'
        string += '        <Parameter name="Input Mesh File" type="string" value="' + self.filename +'.txt"/>\n'    
        return string
    def createBondFilter(self):
        string = '        <ParameterList name="Bond Filters">\n'
        
        
        for idx in range(0, len(self.bondfilters['Name'])):
            string += '            <ParameterList name="' + self.bondfilters['Name'][idx] +'">\n'
            string += '                <Parameter name="Type" type="string" value = "Rectangular_Plane"/>\n'
            string += '                <Parameter name="Normal_X" type="double" value="' + str(self.bondfilters['Normal'][idx][0]) + '"/>\n'
            string += '                <Parameter name="Normal_Y" type="double" value="' + str(self.bondfilters['Normal'][idx][1]) + '"/>\n'
            string += '                <Parameter name="Normal_Z" type="double" value="' + str(self.bondfilters['Normal'][idx][2]) + '"/>\n'
            string += '                <Parameter name="Lower_Left_Corner_X" type="double" value="' + str(self.bondfilters['Lower_Left_Corner'][idx][0]) + '"/>\n'
            string += '                <Parameter name="Lower_Left_Corner_Y" type="double" value="' + str(self.bondfilters['Lower_Left_Corner'][idx][1]) + '"/>\n'
            string += '                <Parameter name="Lower_Left_Corner_Z" type="double" value="' + str(self.bondfilters['Lower_Left_Corner'][idx][2]) + '"/>\n'
            string += '                <Parameter name="Bottom_Unit_Vector_X" type="double" value="' + str(self.bondfilters['Bottom_Unit_Vector'][idx][0]) + '"/>\n'
            string += '                <Parameter name="Bottom_Unit_Vector_Y" type="double" value="' + str(self.bondfilters['Bottom_Unit_Vector'][idx][1]) + '"/>\n'
            string += '                <Parameter name="Bottom_Unit_Vector_Z" type="double" value="' + str(self.bondfilters['Bottom_Unit_Vector'][idx][2]) + '"/>\n'
            string += '                <Parameter name="Bottom_Length" type="double" value="' + str(self.bondfilters['Bottom_Length'][idx]) + '"/>\n'
            string += '                <Parameter name="Side_Length" type="double" value="' + str(self.bondfilters['Side_Length'][idx]) + '"/>\n'
            string += '            </ParameterList>\n'
        string += '        </ParameterList>\n'
        return string
    def material(self):
        string = '    <ParameterList name="Materials">\n'
        aniso = False
        for mat in self.materialDict:
            string += '        <ParameterList name="' + mat +'">\n'
            string += '            <Parameter name="Material Model" type="string" value="' + self.materialDict[mat]['MatType'] + '"/>\n'
            string += '            <Parameter name="Tension pressure separation for damage model" type="bool" value="false"/>\n'
            string += '            <Parameter name="Plane Stress" type="bool" value="' + str(self.TwoD) + '"/>\n'
            #string += '            <Parameter name="Density" type="double" value="' + str(mat['dens'][idx]) + '"/>\n'
            for param in self.materialDict[mat]['Parameter']:
                string += '            <Parameter name="'+ param +'" type="double" value="' +str(np.format_float_scientific(self.materialDict[mat]['Parameter'][param])) +'"/>\n'
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
    def blocks(self):
        string = '    <ParameterList name="Blocks">\n'
        for idx in range(0, len(self.blockDef['Material'])):
            string += '        <ParameterList name="block_' + str(idx+1) + '">\n'
            string += '            <Parameter name="Block Names" type="string" value="block_' + str(idx+1) + '"/>\n'
            string += '            <Parameter name="Material" type="string" value="' + self.blockDef['Material'][idx] + '"/>\n'
            if self.blockDef['Damage'][idx] != '':
                string += '            <Parameter name="Damage Model" type="string" value="' + self.blockDef['Damage'][idx] + '"/>\n'
            string += '            <Parameter name="Horizon" type="double" value="' + str(self.blockDef['Horizon'][idx]) + '"/>\n'
            if self.blockDef['Interface'][idx] != -1:
                string += '            <Parameter name="Interface" type="int" value"' + str(self.blockDef['Interface'][idx]) + '"/>\n'
            string += '        </ParameterList>\n'
        string += '     </ParameterList>\n'
        return string
    def damage(self):
        string = '    <ParameterList name="Damage Models">\n'
        for dam in self.damageDict:
            string += '        <ParameterList name="' + dam + '">\n'
            string += '            <Parameter name="Damage Model" type="string" value="Critical Energy Correspondence"/>\n'
            string += '            <Parameter name="Critical Energy" type="double" value="' + str(self.damageDict[dam]['Energy']) + '"/>\n'
            if "InterfaceEnergy" in self.damageDict[dam]:
                string += '            <Parameter name="Interblock damage energy" type="double" value="' + str(self.damageDict[dam]['InterfaceEnergy']) + '"/>\n'
            string += '            <Parameter name="Plane Stress" type="bool" value="'+ str(self.TwoD) +'"/>\n'
            string += '            <Parameter name="Only Tension" type="bool" value="'+ str(self.onlyTension) +'"/>\n'
            string += '            <Parameter name="Detached Nodes Check" type="bool" value="true"/>\n'
            string += '            <Parameter name="Thickness" type="double" value="10.0"/>\n'
            string += '            <Parameter name="Hourglass Coefficient" type="double" value="1.0"/>\n'
            string += '            <Parameter name="Stabilizaton Type" type="string" value="Global Stiffness"/>\n'
            string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        return string
    def solver(self):
        string = '    <ParameterList name="Solver">\n'
        string += '        <Parameter name="Verbose" type="bool" value="false"/>\n'
        string += '        <Parameter name="Initial Time" type="double" value="0.0"/>\n'
        string += '        <Parameter name="Final Time" type="double" value="'+ str(self.finalTime) +'"/>\n'
        if(self.solvertype=='Verlet'):
            string += '        <ParameterList name="Verlet">\n'
            string += '            <Parameter name="Safety Factor" type="double" value="0.95"/>\n'
            string += '            <Parameter name="Numerical Damping" type="double" value="0.000005"/>\n'
        elif(self.solvertype=='NOXQuasiStatic'):
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
    def boundaryCondition(self):
        string = '    <ParameterList name="Boundary Conditions">\n'
        for idx in range(0, self.bc['NNodesets']):
            string += '        <Parameter name="Node Set ' + str(idx+1) +'" type="string" value="' + self.nsName + '_' + str(idx+1) + '.txt' + '"/>\n'
        bcDict = self.bc['BCDef']
        for idx in range(0, len(bcDict['NS'])):
            string += '        <ParameterList name="BC_' + str(idx+1) + '">\n'
            string += '            <Parameter name="Type" type="string" value="' + bcDict['Type'][idx] + '"/>\n'
            string += '            <Parameter name="Node Set" type="string" value="Node Set ' + str(bcDict['NS'][idx]) + '"/>\n'
            string += '            <Parameter name="Coordinate" type="string" value="' + bcDict['Direction'][idx] + '"/>\n'
            string += '            <Parameter name="Value" type="string" value="' + str(bcDict['Value'][idx]) + '*t"/>\n'
            string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        return string
    def output(self):
        idx = 0
        string=''
        for out in self.outputDict:
            string += '    <ParameterList name="' + out + '">\n'
            string += '        <Parameter name="Output File Type" type="string" value="ExodusII"/>\n'
            string += '        <Parameter name="Output Format" type="string" value="BINARY"/>\n'
            string += '        <Parameter name="Output Filename" type="string" value="' + self.filename +'_' + out +'"/>\n'
            if self.initStep[idx] !=0: 
                string += '        <Parameter name="Initial Output Step" type="int" value="' + str(self.initStep[idx]) + '"/>\n'
            string += '        <Parameter name="Output Frequency" type="int" value="' + str(self.frequency[idx]) + '"/>\n'
            string += '        <Parameter name="Parallel Write" type="bool" value="true"/>\n'
            string += '        <Parameter name="Output Variables">\n'
            if "Displacement" in self.outputDict[out]: 
                string += '            <Parameter name="Displacement" type="bool" value="true"/>\n'
            if "Partial_Stress" in self.outputDict[out]: 
                string += '            <Parameter name="Partial_Stress" type="bool" value="true"/>\n'
            if "Damage" in self.outputDict[out]: 
                string += '            <Parameter name="Damage" type="bool" value="true"/>\n'
            if "Number_Of_Neighbors" in self.outputDict[out]: 
                string += '            <Parameter name="Number_Of_Neighbors" type="bool" value="true"/>\n'
            if "Force" in self.outputDict[out]: 
                string += '            <Parameter name="Force" type="bool" value="true"/>\n'
            if "External_Displacement" in self.outputDict[out]: 
                string += '            <Parameter name="External_Displacement" type="bool" value="true"/>\n'
            if "External_Force" in self.outputDict[out]: 
                string += '            <Parameter name="External_Force" type="bool" value="true"/>\n'
            string += '        </ParameterList>\n'
            string += '    </ParameterList>\n'
            idx +=1
        return string
    def createXML(self):
        string = '<ParameterList>\n'
        string += self.loadMesh()

        if len(self.bondfilters['Name'])>0:
            string += self.createBondFilter()
        string += '    </ParameterList>\n'
        string += self.material()
        if len(self.damageDict)>0:
            string += self.damage()
        string += self.blocks()
        string += self.boundaryCondition()
        string += self.solver()
        
        string += '    <ParameterList name="Compute Class Parameters">\n'
        string += '        <ParameterList name="External Displacement">\n'
        string += '            <Parameter name="Compute Class" type="string" value="Block_Data"/>\n'
        string += '            <Parameter name="Calculation Type" type="string" value="Minimum"/>\n'
        string += '            <Parameter name="Block" type="string" value="block_7"/>\n'
        string += '            <Parameter name="Variable" type="string" value="Displacement"/>\n'
        string += '            <Parameter name="Output Label" type="string" value="External_Displacement"/>\n'
        string += '        </ParameterList>\n'
        string += '        <ParameterList name="External Loads">\n'
        string += '            <Parameter name="Compute Class" type="string" value="Block_Data"/>\n'
        string += '            <Parameter name="Calculation Type" type="string" value="Sum"/>\n'
        string += '            <Parameter name="Block" type="string" value="block_7"/>\n'
        string += '            <Parameter name="Variable" type="string" value="Force"/>\n'
        string += '            <Parameter name="Output Label" type="string" value="External_Force"/>\n'
        string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        
        string += self.output()

        string += '</ParameterList>\n'
        
        return string