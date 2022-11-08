"""
doc
"""
import numpy as np
from support.globals import log


class XMLcreator:
    def __init__(self, model_writer, block_def=None):
        self.filename = model_writer.filename
        self.material_dict = model_writer.material_dict
        self.damage_dict = model_writer.damage_dict
        self.compute_dict = model_writer.compute_dict
        self.output_dict = model_writer.output_dict
        self.solver_dict = model_writer.solver_dict
        self.block_def = block_def
        self.contact_dict = model_writer.contact_dict
        self.bondfilters = model_writer.bondfilters
        self.boundary_condition = model_writer.bc_dict
        self.ns_name = model_writer.ns_name
        self.ns_list = model_writer.ns_list
        self.disc_type = model_writer.disc_type
        self.two_d = model_writer.two_d

    @staticmethod
    def check_if_defined(obj):
        return obj is not None and obj != 0 and obj != ""

    def load_mesh(self):
        string = '    <ParameterList name="Discretization">\n'
        if self.disc_type == "txt":
            string += (
                '        <Parameter name="Type" type="string" value="Text File" />\n'
            )
            string += (
                '        <Parameter name="Input Mesh File" type="string" value="'
                + self.filename
                + '.txt"/>\n'
            )
        elif self.disc_type == "e":
            string += '        <Parameter name="Type" type="string" value="Exodus" />\n'
            string += (
                '        <Parameter name="Input Mesh File" type="string" value="'
                + self.filename
                + '.g"/>\n'
            )
        return string

    def create_bond_filter(self):
        string = '        <ParameterList name="Bond Filters">\n'
        for bond_filter in self.bondfilters:
            string += '            <ParameterList name="' + bond_filter.name + '">\n'
            string += (
                '                <Parameter name="Type" type="string" value = "'
                + bond_filter.type
                + '"/>\n'
            )
            string += (
                '                <Parameter name="Normal_X" type="double" value="'
                + str(bond_filter.normalX)
                + '"/>\n'
            )
            string += (
                '                <Parameter name="Normal_Y" type="double" value="'
                + str(bond_filter.normalY)
                + '"/>\n'
            )
            string += (
                '                <Parameter name="Normal_Z" type="double" value="'
                + str(bond_filter.normalZ)
                + '"/>\n'
            )
            if bond_filter.type == "Rectangular_Plane":
                string += (
                    '                <Parameter name="Lower_Left_Corner_X" type="double" value="'
                    + str(bond_filter.lowerLeftCornerX)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Lower_Left_Corner_Y" type="double" value="'
                    + str(bond_filter.lowerLeftCornerY)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Lower_Left_Corner_Z" type="double" value="'
                    + str(bond_filter.lowerLeftCornerZ)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Bottom_Unit_Vector_X" type="double" value="'
                    + str(bond_filter.bottomUnitVectorX)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Bottom_Unit_Vector_Y" type="double" value="'
                    + str(bond_filter.bottomUnitVectorY)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Bottom_Unit_Vector_Z" type="double" value="'
                    + str(bond_filter.bottomUnitVectorZ)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Bottom_Length" type="double" value="'
                    + str(bond_filter.bottomLength)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Side_Length" type="double" value="'
                    + str(bond_filter.sideLength)
                    + '"/>\n'
                )
            elif bond_filter.type == "Disk":
                string += (
                    '                <Parameter name="Center_X" type="double" value="'
                    + str(bond_filter.centerX)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Center_Y" type="double" value="'
                    + str(bond_filter.centerY)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Center_Z" type="double" value="'
                    + str(bond_filter.centerZ)
                    + '"/>\n'
                )
                string += (
                    '                <Parameter name="Radius" type="double" value="'
                    + str(bond_filter.radius)
                    + '"/>\n'
                )
            string += "            </ParameterList>\n"
        string += "        </ParameterList>\n"
        return string

    def material(self):
        string = '    <ParameterList name="Materials">\n'
        for mat in self.material_dict:
            string += '        <ParameterList name="' + mat.name + '">\n'
            string += (
                '            <Parameter name="Material Model" type="string" value="'
                + mat.matType
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Plane Stress" type="bool" value="'
                + str(self.two_d)
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Density" type="double" value="'
                + str(np.format_float_scientific(float(mat.density)))
                + '"/>\n'
            )
            if mat.materialSymmetry == "Anisotropic":
                string += (
                    '            <Parameter name="Material Symmetry" type="string" value = "'
                    + mat.materialSymmetry
                    + '"/>\n'
                )
                for param in mat.Parameter:
                    string += (
                        '            <Parameter name="'
                        + param.name
                        + '" type="double" value="'
                        + str(np.format_float_scientific(float(param.value)))
                        + '"/>\n'
                    )

                # needed for time step estimation
            if self.check_if_defined(mat.youngsModulus):
                string += (
                    '            <Parameter name="Young'
                    + "'"
                    + 's Modulus" type="double" value="'
                    + str(np.format_float_scientific(float(mat.youngsModulus)))
                    + '"/>\n'
                )
            if self.check_if_defined(mat.shearModulus):
                string += (
                    '            <Parameter name="Shear Modulus" type="double" value="'
                    + str(np.format_float_scientific(float(mat.shearModulus)))
                    + '"/>\n'
                )
            if self.check_if_defined(mat.bulkModulus):
                string += (
                    '            <Parameter name="Bulk Modulus" type="double" value="'
                    + str(np.format_float_scientific(float(mat.bulkModulus)))
                    + '"/>\n'
                )
            if self.check_if_defined(mat.poissonsRatio):
                string += (
                    '            <Parameter name="Poisson'
                    + "'"
                    + 's Ratio" type="double" value="'
                    + str(np.format_float_scientific(float(mat.poissonsRatio)))
                    + '"/>\n'
                )
            string += (
                '            <Parameter name="Stabilizaton Type" type="string" value="'
                + mat.stabilizatonType
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Thickness" type="double" value="'
                + str(float(mat.thickness))
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Hourglass Coefficient" type="double" value="'
                + str(float(mat.hourglassCoefficient))
                + '"/>\n'
            )
            if mat.tensionSeparation:
                string += (
                    '            <Parameter name="Tension pressure separation for damage model" type="bool" value="'
                    + str(mat.tensionSeparation)
                    + '"/>\n'
                )
            if self.check_if_defined(mat.actualHorizon):
                string += (
                    '            <Parameter name="Actual Horizon" type="double" value="'
                    + str(float(mat.actualHorizon))
                    + '"/>\n'
                )
            if self.check_if_defined(mat.yieldStress):
                string += (
                    '            <Parameter name="Yield Stress" type="double" value="'
                    + str(float(mat.yieldStress))
                    + '"/>\n'
                )
            if self.check_if_defined(mat.nonLinear):
                string += (
                    '            <Parameter name="Non linear" type="bool" value="'
                    + str(mat.nonLinear)
                    + '"/>\n'
                )
            if self.check_if_defined(mat.properties) and "User" in mat.matType:
                string += (
                    '            <Parameter name="Number of properties" type="int" value="'
                    + str(len(mat.properties))
                    + '"/>\n'
                )
                for prop in mat.properties:
                    string += (
                        '            <Parameter name="'
                        + prop.name
                        + '" type="double" value="'
                        + str(np.format_float_scientific(float(prop.value)))
                        + '"/>\n'
                    )
            if self.check_if_defined(mat.computePartialStress):
                string += (
                    '            <Parameter name="Compute Partial Stress" type="bool" value="'
                    + str(mat.computePartialStress)
                    + '"/>\n'
                )
            if self.check_if_defined(mat.useCollocationNodes):
                string += (
                    '            <Parameter name="Use Collocation Nodes" type="bool" value="'
                    + str(mat.useCollocationNodes)
                    + '"/>\n'
                )
            string += "        </ParameterList>\n"
        string += "    </ParameterList>\n"
        return string

    def blocks(self):
        string = '    <ParameterList name="Blocks">\n'
        for block in self.block_def:
            string += '        <ParameterList name="' + block.name + '">\n'
            string += (
                '            <Parameter name="Block Names" type="string" value="'
                + block.name
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Material" type="string" value="'
                + block.material
                + '"/>\n'
            )
            if block.damageModel != "" and block.damageModel is not None:
                string += (
                    '            <Parameter name="Damage Model" type="string" value="'
                    + block.damageModel
                    + '"/>\n'
                )
            string += (
                '            <Parameter name="Horizon" type="double" value="'
                + str(block.horizon)
                + '"/>\n'
            )
            string += "        </ParameterList>\n"
        string += "     </ParameterList>\n"
        return string

    def damage(self):
        string = '    <ParameterList name="Damage Models">\n'
        for dam in self.damage_dict:
            string += '        <ParameterList name="' + dam.name + '">\n'
            string += (
                '            <Parameter name="Damage Model" type="string" value="'
                + str(dam.damageModel)
                + '"/>\n'
            )
            if dam.damageModel == "Critical Energy Correspondence":
                string += (
                    '            <Parameter name="Critical Energy" type="double" value="'
                    + str(float(dam.criticalEnergy))
                    + '"/>\n'
                )

                if dam.interBlockDamage:
                    string += '            <Parameter name="Interblock Damage" type="bool" value="true"/>\n'
                    string += (
                        '            <Parameter name="Number of Blocks" type="int" value="'
                        + str(dam.numberOfBlocks)
                        + '"/>\n'
                    )
                    for interBlock in dam.interBlocks:
                        string += (
                            '            <Parameter name="Interblock Critical Energy '
                            + str(interBlock.firstBlockId)
                            + "_"
                            + str(interBlock.secondBlockId)
                            + '" type="double" value="'
                            + str(float(interBlock.value))
                            + '"/>\n'
                        )
            else:
                string += (
                    '            <Parameter name="Critical Stretch" type="double" value="'
                    + str(float(dam.criticalStretch))
                    + '"/>\n'
                )
            string += (
                '            <Parameter name="Plane Stress" type="bool" value="'
                + str(self.two_d)
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Only Tension" type="bool" value="'
                + str(dam.onlyTension)
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Detached Nodes Check" type="bool" value="'
                + str(dam.detachedNodesCheck)
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Thickness" type="double" value="'
                + str(float(dam.thickness))
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Hourglass Coefficient" type="double" value="'
                + str(float(dam.hourglassCoefficient))
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Stabilizaton Type" type="string" value="'
                + str(dam.stabilizatonType)
                + '"/>\n'
            )
            string += "        </ParameterList>\n"
        string += "    </ParameterList>\n"
        return string

    def solver(self):
        string = '    <ParameterList name="Solver">\n'
        string += (
            '        <Parameter name="Verbose" type="bool" value="'
            + str(self.solver_dict.verbose)
            + '"/>\n'
        )
        string += (
            '        <Parameter name="Initial Time" type="double" value="'
            + str(float(self.solver_dict.initialTime))
            + '"/>\n'
        )
        string += (
            '        <Parameter name="Final Time" type="double" value="'
            + str(float(self.solver_dict.finalTime))
            + '"/>\n'
        )
        if self.solver_dict.solvertype == "Verlet":
            string += '        <ParameterList name="Verlet">\n'
            if self.check_if_defined(self.solver_dict.fixedDt):
                string += (
                    '            <Parameter name="Fixed dt" type="double" value="'
                    + str(float(self.solver_dict.fixedDt))
                    + '"/>\n'
                )
            string += (
                '            <Parameter name="Safety Factor" type="double" value="'
                + str(float(self.solver_dict.safetyFactor))
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Numerical Damping" type="double" value="'
                + str(float(self.solver_dict.numericalDamping))
                + '"/>\n'
            )
            if self.solver_dict.stopAfterDamageInitation:
                string += '            <Parameter name="Stop after damage initiation" type="bool" value="true"/>\n'
            if self.solver_dict.stopBeforeDamageInitation:
                string += '            <Parameter name="Stop before damage initiation" type="bool" value="true"/>\n'
            if (self.check_if_defined(self.solver_dict.adaptivetimeStepping) and self.solver_dict.adaptivetimeStepping):
                string += '            <Parameter name="Adapt dt" type="bool" value="true"/>\n'
                string += (
                    '            <Parameter name="Stable Step Difference" type="int" value="'
                    + str(self.solver_dict.adapt.stableStepDifference)
                    + '"/>\n'
                )
                string += (
                    '            <Parameter name="Maximum Bond Difference" type="int" value="'
                    + str(self.solver_dict.adapt.maximumBondDifference)
                    + '"/>\n'
                )
                string += (
                    '            <Parameter name="Stable Bond Difference" type="int" value="'
                    + str(self.solver_dict.adapt.stableBondDifference)
                    + '"/>\n'
                )
        elif self.solver_dict.solvertype == "NOXQuasiStatic":
            string += (
                '        <Parameter name="Peridigm Preconditioner" type="string" value="'
                + str(self.solver_dict.peridgimPreconditioner)
                + '"/>\n'
            )
            string += '        <ParameterList name="NOXQuasiStatic">\n'
            string += (
                '            <Parameter name="Nonlinear Solver" type="string" value="'
                + str(self.solver_dict.nonlinearSolver)
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Number of Load Steps" type="int" value="'
                + str(self.solver_dict.numberOfLoadSteps)
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Max Solver Iterations" type="int" value="'
                + str(self.solver_dict.maxSolverIterations)
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Relative Tolerance" type="double" value="'
                + str(float(self.solver_dict.relativeTolerance))
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Max Age Of Prec" type="int" value="'
                + str(self.solver_dict.maxAgeOfPrec)
                + '"/>\n'
            )
            string += '            <ParameterList name="Direction">\n'
            string += (
                '                 <Parameter name="Method" type="string" value="'
                + str(self.solver_dict.directionMethod)
                + '"/>\n'
            )
            if self.solver_dict.directionMethod == "Newton":
                string += '                 <ParameterList name="Newton">\n'
                string += '                      <ParameterList name="Linear Solver">\n'
                string += (
                    '                           <Parameter name="Jacobian Operator" type="string" value="'
                    + str(self.solver_dict.newton.jacobianOperator)
                    + '"/>\n'
                )
                string += (
                    '                           <Parameter name="Preconditioner" type="string" value="'
                    + str(self.solver_dict.newton.preconditioner)
                    + '"/>\n'
                )
                string += "                      </ParameterList>\n"
                string += "                 </ParameterList>\n"
            string += "            </ParameterList>\n"
            string += '            <ParameterList name="Line Search">\n'
            string += (
                '                 <Parameter name="Method" type="string" value="'
                + str(self.solver_dict.lineSearchMethod)
                + '"/>\n'
            )
            string += "            </ParameterList>\n"
            if self.solver_dict.verletSwitch:
                string += '            <ParameterList name="Switch to Verlet">\n'
                string += (
                    '                 <Parameter name="Safety Factor" type="double" value="'
                    + str(float(self.solver_dict.verlet.safetyFactor))
                    + '"/>\n'
                )
                string += (
                    '                 <Parameter name="Numerical Damping" type="double" value="'
                    + str(float(self.solver_dict.verlet.numericalDamping))
                    + '"/>\n'
                )
                string += (
                    '                 <Parameter name="Output Frequency" type="int" value="'
                    + str(self.solver_dict.verlet.outputFrequency)
                    + '"/>\n'
                )
                string += "            </ParameterList>\n"
        else:
            string += '        <ParameterList name="Verlet">\n'
            string += (
                '            <Parameter name="Safety Factor" type="double" value="'
                + str(float(self.solver_dict.safetyFactor))
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Numerical Damping" type="double" value="'
                + str(float(self.solver_dict.numericalDamping))
                + '"/>\n'
            )
        string += "        </ParameterList>\n"
        string += "    </ParameterList>\n"
        return string

    def create_boundary_condition(self):
        string = '    <ParameterList name="Boundary Conditions">\n'
        if self.disc_type == "txt":
            for idx in range(0, len(self.ns_list)):
                string += (
                    '        <Parameter name="Node Set '
                    + str(idx + 1)
                    + '" type="string" value="'
                    + self.ns_name
                    + "_"
                    + str(idx + 1)
                    + ".txt"
                    + '"/>\n'
                )
        for boundary_condition in self.boundary_condition:
            node_set_id = self.ns_list.index(boundary_condition.blockId)
            string += '        <ParameterList name="' + boundary_condition.name + '">\n'
            string += (
                '            <Parameter name="Type" type="string" value="'
                + boundary_condition.boundarytype
                + '"/>\n'
            )
            if self.check_if_defined(boundary_condition.nodeSet):
                string += (
                    '            <Parameter name="Node Set" type="string" value="'
                    + boundary_condition.nodeSet
                    + '"/>\n'
                )
            else:
                string += (
                    '            <Parameter name="Node Set" type="string" value="Node Set '
                    + str(node_set_id + 1)
                    + '"/>\n'
                )
            string += (
                '            <Parameter name="Coordinate" type="string" value="'
                + boundary_condition.coordinate
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Value" type="string" value="'
                + str(boundary_condition.value)
                + '"/>\n'
            )
            string += "        </ParameterList>\n"
        string += "    </ParameterList>\n"
        return string

    def contact(self):
        string = '    <ParameterList name="Contact">\n'
        string += (
            '        <Parameter name="Search Radius" type="double" value="'
            + str(self.contact_dict.searchRadius)
            + '"/>\n'
        )
        string += (
            '        <Parameter name="Search Frequency" type="int" value="'
            + str(self.contact_dict.searchFrequency)
            + '"/>\n'
        )
        string += '        <ParameterList name="Models">\n'
        for models in self.contact_dict.contactModels:
            string += '            <ParameterList name="' + models.name + '">\n'
            string += (
                '               <Parameter name="Contact Model" type="string" value="'
                + models.contactType
                + '"/>\n'
            )
            string += (
                '               <Parameter name="Contact Radius" type="double" value="'
                + str(models.contactRadius)
                + '"/>\n'
            )
            string += (
                '               <Parameter name="Spring Constant" type="double" value="'
                + str(models.springConstant)
                + '"/>\n'
            )
            string += "                </ParameterList>\n"
        string += "            </ParameterList>\n"
        string += '        <ParameterList name="Interactions">\n'
        for interaction in self.contact_dict.interactions:
            string += (
                '            <ParameterList name="Interaction '
                + str(interaction.firstBlockId)
                + "_"
                + str(interaction.secondBlockId)
                + '">\n'
            )
            string += (
                '               <Parameter name="First Block" type="string" value="'
                + self.block_def[interaction.firstBlockId - 1].name
                + '"/>\n'
            )
            string += (
                '               <Parameter name="Second Block" type="string" value="'
                + self.block_def[interaction.secondBlockId - 1].name
                + '"/>\n'
            )
            string += (
                '               <Parameter name="Contact Model" type="string" value="'
                + self.contact_dict.contactModels[interaction.contactModelId - 1].name
                + '"/>\n'
            )
            string += "                </ParameterList>\n"
        string += "            </ParameterList>\n"
        string += "    </ParameterList>\n"
        return string

    def compute(self):
        string = '    <ParameterList name="Compute Class Parameters">\n'
        for out in self.compute_dict:
            string += '        <ParameterList name="' + out.name + '">\n'
            string += '            <Parameter name="Compute Class" type="string" value="Block_Data"/>\n'
            string += (
                '            <Parameter name="Calculation Type" type="string" value="'
                + out.calculationType
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Block" type="string" value="'
                + out.blockName
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Variable" type="string" value="'
                + out.variable
                + '"/>\n'
            )
            string += (
                '            <Parameter name="Output Label" type="string" value="'
                + out.name
                + '"/>\n'
            )
            string += "        </ParameterList>\n"

        string += "    </ParameterList>\n"
        return string

    def output(self):
        idx = 0
        string = ""
        for out in self.output_dict:
            string += '    <ParameterList name="Output' + str(idx + 1) + '">\n'
            string += '        <Parameter name="Output File Type" type="string" value="ExodusII"/>\n'
            string += '        <Parameter name="Output Format" type="string" value="BINARY"/>\n'
            string += (
                '        <Parameter name="Output Filename" type="string" value="'
                + self.filename
                + "_"
                + out.name
                + '"/>\n'
            )
            if out.InitStep != 0:
                string += (
                    '        <Parameter name="Initial Output Step" type="int" value="'
                    + str(out.InitStep)
                    + '"/>\n'
                )
            string += (
                '        <Parameter name="Output Frequency" type="int" value="'
                + str(out.Frequency)
                + '"/>\n'
            )
            string += (
                '        <Parameter name="Parallel Write" type="bool" value="true"/>\n'
            )
            if out.Write_After_Damage:
                string += '        <Parameter name="Write After Damage" type="bool" value="true"/>\n'
            string += '        <ParameterList name="Output Variables">\n'
            if out.Displacement:
                string += '            <Parameter name="Displacement" type="bool" value="true"/>\n'
            if out.Partial_Stress:
                string += '            <Parameter name="Partial_Stress" type="bool" value="true"/>\n'
            if out.Damage:
                string += (
                    '            <Parameter name="Damage" type="bool" value="true"/>\n'
                )
            if out.Number_Of_Neighbors:
                string += '            <Parameter name="Number_Of_Neighbors" type="bool" value="true"/>\n'
            if out.Contact_Force:
                string += '            <Parameter name="Contact_Force" type="bool" value="true"/>\n'
            if out.Force:
                string += (
                    '            <Parameter name="Force" type="bool" value="true"/>\n'
                )
            if out.Velocity:
                string += '            <Parameter name="Velocity" type="bool" value="true"/>\n'
            for compute in self.compute_dict:
                string += (
                    '            <Parameter name="'
                    + compute.name
                    + '" type="bool" value="true"/>\n'
                )
            if out.Horizon:
                string += (
                    '            <Parameter name="Horizon" type="bool" value="true"/>\n'
                )
            if out.Model_Coordinates:
                string += '            <Parameter name="Model_Coordinates" type="bool" value="true"/>\n'
            if out.Local_Angles:
                string += '            <Parameter name="Local_Angles" type="bool" value="true"/>\n'
            if out.Orientations:
                string += '            <Parameter name="Orientations" type="bool" value="true"/>\n'
            if out.Coordinates:
                string += '            <Parameter name="Coordinates" type="bool" value="true"/>\n'
            if out.Acceleration:
                string += '            <Parameter name="Acceleration" type="bool" value="true"/>\n'
            if out.Temperature:
                string += '            <Parameter name="Temperature" type="bool" value="true"/>\n'
            if out.Temperature_Change:
                string += '            <Parameter name="Temperature_Change" type="bool" value="true"/>\n'
            if out.Force_Density:
                string += '            <Parameter name="Force_Density" type="bool" value="true"/>\n'
            if out.External_Force_Density:
                string += '            <Parameter name="External_Force_Density" type="bool" value="true"/>\n'
            if out.Damage_Model_Data:
                string += '            <Parameter name="Damage_Model_Data" type="bool" value="true"/>\n'
            if out.Velocity_Gradient:
                string += '            <Parameter name="Velocity_Gradient_X" type="bool" value="true"/>\n'
                string += '            <Parameter name="Velocity_Gradient_Y" type="bool" value="true"/>\n'
                string += '            <Parameter name="Velocity_Gradient_Z" type="bool" value="true"/>\n'
            if out.PiolaStressTimesInvShapeTensor:
                string += '            <Parameter name="PiolaStressTimesInvShapeTensorX" type="bool" value="true"/>\n'
                string += '            <Parameter name="PiolaStressTimesInvShapeTensorY" type="bool" value="true"/>\n'
                string += '            <Parameter name="PiolaStressTimesInvShapeTensorZ" type="bool" value="true"/>\n'
            string += "        </ParameterList>\n"
            string += "    </ParameterList>\n"
            idx += 1
        return string

    def create_xml(self):
        string = "<ParameterList>\n"
        string += self.load_mesh()

        if len(self.bondfilters) > 0:
            string += self.create_bond_filter()
        string += "    </ParameterList>\n"
        string += self.material()
        if len(self.damage_dict) > 0:
            string += self.damage()
        string += self.blocks()
        if self.check_if_defined(self.contact_dict):
            if self.contact_dict.enabled and len(self.contact_dict.contactModels) > 0:
                try:
                    string += self.contact()
                except IndexError:
                    log.error("Error in contact definition")

        string += self.create_boundary_condition()
        string += self.solver()
        string += self.compute()
        string += self.output()

        string += "</ParameterList>\n"

        return string
