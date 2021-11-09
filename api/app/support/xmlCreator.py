import numpy as np

class XMLcreator(object):
    def __init__(self, modelWriter, blockDef = {}):
        self.filename = modelWriter.filename
        self.materialDict = modelWriter.materialDict
        self.damageDict = modelWriter.damageDict
        self.computeDict = modelWriter.computeDict
        self.outputDict = modelWriter.outputDict
        self.solverDict = modelWriter.solverDict  
        self.blockDef = blockDef
        self.bondfilters = modelWriter.bondfilters
        self.bc = modelWriter.bcDict
        self.nsName = modelWriter.nsName
        self.nsList = modelWriter.nsList
        self.DiscType = modelWriter.DiscType
        self.TwoD = modelWriter.TwoD

    def checkIfDefined(self, name, obj):
        return name in obj and obj[name] != None and obj[name] != 0 and obj[name] != ''
        
    def loadMesh(self):
        string = '    <ParameterList name="Discretization">\n'
        if self.DiscType == 'txt':
            string += '        <Parameter name="Type" type="string" value="Text File" />\n'
            string += '        <Parameter name="Input Mesh File" type="string" value="' + self.filename +'.txt"/>\n'  
        elif self.DiscType == 'e':
            string += '        <Parameter name="Type" type="string" value="Exodus" />\n'
            string += '        <Parameter name="Input Mesh File" type="string" value="' + self.filename +'.g"/>\n'  
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
        for mat in self.materialDict:
            string += '        <ParameterList name="' + mat['Name'] +'">\n'
            string += '            <Parameter name="Material Model" type="string" value="' + mat['MatType'] + '"/>\n'
            string += '            <Parameter name="Plane Stress" type="bool" value="' + str(self.TwoD) + '"/>\n'
            string += '            <Parameter name="Density" type="double" value="' + str(np.format_float_scientific(float(mat['density']))) + '"/>\n'
            if mat['materialSymmetry'] == 'Anisotropic':
                string += '            <Parameter name="Material Symmetry" type="string" value = "' + mat['materialSymmetry'] + '"/>\n'
                for param in mat['Parameter']:
                    string += '            <Parameter name="'+ param +'" type="double" value="' +str(np.format_float_scientific(float(mat['Parameter'][param]['value']))) +'"/>\n'

                # needed for time step estimation
            if self.checkIfDefined('youngsModulus',mat):
                string += '            <Parameter name="Young' + "'" + 's Modulus" type="double" value="' + str(np.format_float_scientific(float(mat['youngsModulus']))) + '"/>\n'
            if self.checkIfDefined('shearModulus',mat):
                string += '            <Parameter name="Shear Modulus" type="double" value="' + str(np.format_float_scientific(float(mat['shearModulus']))) + '"/>\n'
            if self.checkIfDefined('bulkModulus',mat):
                string += '            <Parameter name="Bulk Modulus" type="double" value="' + str(np.format_float_scientific(float(mat['bulkModulus']))) + '"/>\n'
            if self.checkIfDefined('poissonsRatio',mat):
                string += '            <Parameter name="Poisson' + "'" + 's Ratio" type="double" value="' + str(np.format_float_scientific(float(mat['poissonsRatio']))) + '"/>\n'
            string += '            <Parameter name="Stabilizaton Type" type="string" value="' + mat['stabilizatonType'] + '"/>\n'
            string += '            <Parameter name="Thickness" type="double" value="' + str(float(mat['thickness'])) + '"/>\n'
            string += '            <Parameter name="Hourglass Coefficient" type="double" value="' + str(float(mat['hourglassCoefficient'])) + '"/>\n'
            if mat['tensionSeparation']:
                string += '            <Parameter name="Tension pressure separation for damage model" type="bool" value="' + str(mat['tensionSeparation']) + '"/>\n'
            if 'actualHorizon' in mat and mat['actualHorizon']!='':
                string += '            <Parameter name="Actual Horizon" type="double" value="' + str(float(mat['actualHorizon'])) + '"/>\n'
            if 'yieldStress' in mat and mat['yieldStress']!='':
                string += '            <Parameter name="Yield Stress" type="double" value="' + str(float(mat['yieldStress'])) + '"/>\n'
            if 'nonLinear' in mat and mat['nonLinear']!='':
                string += '            <Parameter name="Non linear" type="double" value="' + str(mat['nonLinear']) + '"/>\n'
            string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'  
        return string  
    def blocks(self):
        string = '    <ParameterList name="Blocks">\n'
        for block in self.blockDef:
            string += '        <ParameterList name="' + block['Name'] + '">\n'
            string += '            <Parameter name="Block Names" type="string" value="' + block['Name'] + '"/>\n'
            string += '            <Parameter name="Material" type="string" value="' + block['material'] + '"/>\n'
            if block['damageModel'] != '' and block['damageModel'] != None:
                string += '            <Parameter name="Damage Model" type="string" value="' + block['damageModel'] + '"/>\n'
            string += '            <Parameter name="Horizon" type="double" value="' + str(block['horizon']) + '"/>\n'
            if block['interface'] != '' and block['interface'] != None:
                string += '            <Parameter name="Interface" type="int" value="' + str(block['interface']) + '"/>\n'
            string += '        </ParameterList>\n'
        string += '     </ParameterList>\n'
        return string
    def damage(self):
        string = '    <ParameterList name="Damage Models">\n'
        for dam in self.damageDict:
            string += '        <ParameterList name="' + dam['Name'] + '">\n'
            string += '            <Parameter name="Damage Model" type="string" value="' + str(dam['damageModel']) + '"/>\n'
            if dam['damageModel'] =='Critical Energy Correspondence':
                string += '            <Parameter name="Critical Energy" type="double" value="' + str(float(dam['criticalEnergy'])) + '"/>\n'
                if "interblockdamageEnergy" in dam:
                    string += '            <Parameter name="Interblock damage energy" type="double" value="' + str(float(dam['interblockdamageEnergy'])) + '"/>\n'
            else:
                string += '            <Parameter name="Critical Stretch" type="double" value="'+ str(float(dam['criticalStretch'])) +'"/>\n'
            string += '            <Parameter name="Plane Stress" type="bool" value="'+ str(self.TwoD) +'"/>\n'
            string += '            <Parameter name="Only Tension" type="bool" value="'+ str(dam['onlyTension']) +'"/>\n'
            string += '            <Parameter name="Detached Nodes Check" type="bool" value="'+ str(dam['detachedNodesCheck']) +'"/>\n'
            string += '            <Parameter name="Thickness" type="double" value="'+ str(float(dam['thickness'])) +'"/>\n'
            string += '            <Parameter name="Hourglass Coefficient" type="double" value="'+ str(float(dam['hourglassCoefficient'])) +'"/>\n'
            string += '            <Parameter name="Stabilizaton Type" type="string" value="'+ str(dam['stabilizatonType']) +'"/>\n'
            string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        return string
    def solver(self):
        string = '    <ParameterList name="Solver">\n'
        string += '        <Parameter name="Verbose" type="bool" value="'+ str(self.solverDict['verbose']) +'"/>\n'
        string += '        <Parameter name="Initial Time" type="double" value="'+ str(float(self.solverDict['initialTime'])) +'"/>\n'
        string += '        <Parameter name="Final Time" type="double" value="'+ str(float(self.solverDict['finalTime'])) +'"/>\n'
        if(self.solverDict['solvertype']=='Verlet'):
            string += '        <ParameterList name="Verlet">\n'
            string += '            <Parameter name="Safety Factor" type="double" value="'+ str(float(self.solverDict['safetyFactor'])) +'"/>\n'
            string += '            <Parameter name="Numerical Damping" type="double" value="'+ str(float(self.solverDict['numericalDamping'])) +'"/>\n'
            if('adaptivetimeStepping' in self.solverDict and self.solverDict['adaptivetimeStepping']):
                string += '            <Parameter name="Adaptive Time Stepping" type="bool" value="true"/>\n'
                string += '            <Parameter name="Stable Step Difference" type="int" value="'+ str(self.solverDict['adapt']['stableStepDifference']) +'"/>\n'
                string += '            <Parameter name="Maximum Bond Difference" type="int" value="'+ str(self.solverDict['adapt']['maximumBondDifference']) +'"/>\n'
                string += '            <Parameter name="Stable Bond Difference" type="int" value="'+ str(self.solverDict['adapt']['stableBondDifference']) +'"/>\n'
        elif(self.solverDict['solvertype']=='NOXQuasiStatic'):
            string += '        <Parameter name="Peridigm Preconditioner" type="string" value="'+ str(self.solverDict['peridgimPreconditioner']) +'"/>\n'
            string += '        <ParameterList name="NOXQuasiStatic">\n'
            string += '            <Parameter name="Nonlinear Solver" type="string" value="'+ str(self.solverDict['nonlinearSolver']) +'"/>\n'
            string += '            <Parameter name="Number of Load Steps" type="int" value="'+ str(float(self.solverDict['NumberOfLoadSteps'])) +'"/>\n'
            string += '            <Parameter name="Max Solver Iterations" type="int" value="'+ str(self.solverDict['maxSolverIterations']) +'"/>\n'
            string += '            <Parameter name="Relative Tolerance" type="double" value="'+ str(float(self.solverDict['Tolerance'])) +'"/>\n'
            string += '            <Parameter name="Max Age Of Prec" type="int" value="'+ str(self.solverDict['maxAgeOfPrec']) +'"/>\n'
            string += '            <ParameterList name="Direction">\n'
            string += '                 <Parameter name="Method" type="string" value="'+ str(self.solverDict['directionMethod']) +'"/>\n'
            if(self.solverDict['directionMethod']=='Newton'):
                string += '                 <ParameterList name="Newton">\n'
                string += '                      <ParameterList name="Linear Solver">\n'
                string += '                           <Parameter name="Jacobian Operator" type="string" value="'+ str(self.solverDict['newton']['jacobianOperator']) +'"/>\n'
                string += '                           <Parameter name="Preconditioner" type="string" value="'+ str(self.solverDict['newton']['preconditioner']) +'"/>\n'
                string += '                      </ParameterList>\n'
                string += '                 </ParameterList>\n'
            string += '            </ParameterList>\n'
            string += '            <ParameterList name="Line Search">\n'
            string += '                 <Parameter name="Method" type="string" value="'+ str(self.solverDict['lineSearchMethod']) +'"/>\n'
            string += '            </ParameterList>\n'
            if(self.solverDict['verletSwitch']):
                string += '            <ParameterList name="Switch to Verlet">\n'
                string += '                 <Parameter name="Safety Factor" type="double" value="'+ str(float(self.solverDict['verlet']['safetyFactor'])) +'"/>\n'
                string += '                 <Parameter name="Numerical Damping" type="double" value="'+ str(float(self.solverDict['verlet']['numericalDamping'])) +'"/>\n'
                string += '                 <Parameter name="Output Frequency" type="int" value="'+ str(self.solverDict['verlet']['outputFrequency']) +'"/>\n'
                string += '            </ParameterList>\n'
        else:
            string += '        <ParameterList name="Verlet">\n'
            string += '            <Parameter name="Safety Factor" type="double" value="'+ str(float(self.solverDict['safetyFactor'])) +'"/>\n'
            string += '            <Parameter name="Numerical Damping" type="double" value="'+ str(float(self.solverDict['numericalDamping'])) +'"/>\n'
        string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        return string
    def boundaryCondition(self):
        string = '    <ParameterList name="Boundary Conditions">\n'
        if self.DiscType == 'txt':
            for idx in range(0, len(self.nsList)):
                string += '        <Parameter name="Node Set ' + str(idx+1) +'" type="string" value="' + self.nsName + '_' + str(idx+1) + '.txt' + '"/>\n'
        for bc in self.bc:
            nodeSetId = self.nsList.index(bc['blockId'])
            string += '        <ParameterList name="' + bc['Name'] + '">\n'
            string += '            <Parameter name="Type" type="string" value="' + bc['boundarytype'] + '"/>\n'
            if self.checkIfDefined('nodeSet', bc):
                string += '            <Parameter name="Node Set" type="string" value="' + bc['nodeSet'] + '"/>\n'
            else:
                string += '            <Parameter name="Node Set" type="string" value="Node Set ' + str(nodeSetId+1) + '"/>\n'
            string += '            <Parameter name="Coordinate" type="string" value="' + bc['coordinate'] + '"/>\n'
            string += '            <Parameter name="Value" type="string" value="' + str(bc['value']) + '"/>\n'
            string += '        </ParameterList>\n'
        string += '    </ParameterList>\n'
        return string
    def compute(self):
        string = '    <ParameterList name="Compute Class Parameters">\n'
        for out in self.computeDict:
            string += '        <ParameterList name="' + out['Name'] + '">\n'
            string += '            <Parameter name="Compute Class" type="string" value="Block_Data"/>\n'
            string += '            <Parameter name="Calculation Type" type="string" value="' + out['calculationType'] + '"/>\n'
            string += '            <Parameter name="Block" type="string" value="' + out['blockName'] + '"/>\n'
            string += '            <Parameter name="Variable" type="string" value="' + out['variable'] + '"/>\n'
            string += '            <Parameter name="Output Label" type="string" value="' + out['Name'] + '"/>\n'
            string += '        </ParameterList>\n'
            
        string += '    </ParameterList>\n'
        return string
    def output(self):
        idx = 0
        string=''
        for out in self.outputDict:
            string += '    <ParameterList name="' + out['Name'] + '">\n'
            string += '        <Parameter name="Output File Type" type="string" value="ExodusII"/>\n'
            string += '        <Parameter name="Output Format" type="string" value="BINARY"/>\n'
            string += '        <Parameter name="Output Filename" type="string" value="' + self.filename +'_' + out['Name'] +'"/>\n'
            if out['InitStep'] !=0:
                string += '        <Parameter name="Initial Output Step" type="int" value="' + str(out['InitStep']) + '"/>\n'
            string += '        <Parameter name="Output Frequency" type="int" value="' + str(out['Frequency']) + '"/>\n'
            string += '        <Parameter name="Parallel Write" type="bool" value="true"/>\n'
            string += '        <ParameterList name="Output Variables">\n'
            if out['Displacement']:
                string += '            <Parameter name="Displacement" type="bool" value="true"/>\n'
            if out['Partial_Stress']:
                string += '            <Parameter name="Partial_Stress" type="bool" value="true"/>\n'
            if out['Damage']:
                string += '            <Parameter name="Damage" type="bool" value="true"/>\n'
            if out['Number_Of_Neighbors']:
                string += '            <Parameter name="Number_Of_Neighbors" type="bool" value="true"/>\n'
            if out['Force']: 
                string += '            <Parameter name="Force" type="bool" value="true"/>\n'
            if out['External_Displacement']:
                string += '            <Parameter name="External_Displacement" type="bool" value="true"/>\n'
            if out['External_Force']:
                string += '            <Parameter name="External_Force" type="bool" value="true"/>\n'
            string += '        </ParameterList>\n'
            string += '    </ParameterList>\n'
            idx +=1
        return string
    def createXML(self):
        string = '<ParameterList>\n'
        string += self.loadMesh()

        if len(self.bondfilters)>0:
            string += self.createBondFilter()
        string += '    </ParameterList>\n'
        string += self.material()
        if len(self.damageDict)>0:
            string += self.damage()
        string += self.blocks()
        string += self.boundaryCondition()
        string += self.solver()
        string += self.compute()
        string += self.output()

        string += '</ParameterList>\n'
        
        return string