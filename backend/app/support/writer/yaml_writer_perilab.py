# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0


import numpy as np
import yaml


class YAMLcreatorPeriLab:
    def __init__(self, model_writer, block_def=None):
        self.filename = model_writer.filename
        self.ns_name = model_writer.ns_name
        self.ns_list = model_writer.ns_list
        self.block_def = block_def

        self.mesh_file = model_writer.model_data.model.mesh_file
        self.boundary_condition = model_writer.model_data.boundaryConditions
        self.solver_dict = model_writer.model_data.solver
        self.damage_dict = model_writer.model_data.damages
        self.material_dict = model_writer.model_data.materials
        self.additive_dict = model_writer.model_data.additive
        self.compute_dict = model_writer.model_data.computes
        self.output_dict = model_writer.model_data.outputs
        self.contact_dict = model_writer.model_data.contact
        self.bondfilters = model_writer.model_data.bondFilters
        self.disc_type = model_writer.disc_type
        self.two_d = model_writer.model_data.model.twoDimensional

    @staticmethod
    def check_if_defined(obj):
        return obj is not None and obj != 0 and obj != ""

    @staticmethod
    def temp_enabled(material_dict):
        for mat in material_dict:
            if mat.thermalConductivity is not None:
                return True
        return False

    def load_mesh(self):
        data = {}
        data["Node Sets"] = {}

        if self.disc_type == "txt":
            data["Type"] = "Text File"

            if self.check_if_defined(self.boundary_condition.nodeSets):
                for nodeSet in self.boundary_condition.nodeSets:
                    data["Node Sets"]["Node Set " + str(nodeSet.nodeSetId)] = nodeSet.file
            else:
                for idx in range(0, len(self.ns_list)):
                    data["Node Sets"]["Node Set " + str(idx + 1)] = self.ns_name + "_" + str(idx + 1) + ".txt"

            if self.check_if_defined(self.mesh_file):
                data["Input Mesh File"] = self.mesh_file
            else:
                data["Input Mesh File"] = self.filename + ".txt"

        elif self.disc_type == "e":
            data["Type"] = "Exodus"

            if self.check_if_defined(self.mesh_file):
                data["Input Mesh File"] = self.mesh_file
            else:
                data["Input Mesh File"] = self.filename + ".g"

        return data

    def create_bond_filter(self):
        data = {}

        for bond_filter in self.bondfilters:
            filter = {}
            filter["Type"] = bond_filter.type
            filter["Normal_X"] = bond_filter.normalX
            filter["Normal_Y"] = bond_filter.normalY
            filter["Normal_Z"] = bond_filter.normalZ

            if bond_filter.type == "Rectangular_Plane":
                filter["Lower_Left_Corner_X"] = bond_filter.lowerLeftCornerX
                filter["Lower_Left_Corner_Y"] = bond_filter.lowerLeftCornerY
                filter["Lower_Left_Corner_Z"] = bond_filter.lowerLeftCornerZ
                filter["Bottom_Unit_Vector_X"] = bond_filter.bottomUnitVectorX
                filter["Bottom_Unit_Vector_Y"] = bond_filter.bottomUnitVectorY
                filter["Bottom_Unit_Vector_Z"] = bond_filter.bottomUnitVectorZ
                filter["Bottom_Length"] = bond_filter.bottomLength
                filter["Side_Length"] = bond_filter.sideLength
            elif bond_filter.type == "Disk":
                filter["Center_X"] = bond_filter.centerX
                filter["Center_Y"] = bond_filter.centerY
                filter["Center_Z"] = bond_filter.centerZ
                filter["Radius"] = bond_filter.radius
            data[bond_filter.name] = filter

        return data

    def materials(self):
        data = {}

        for mat in self.material_dict:
            material = {}
            material["Material Model"] = mat.matType
            material["Plane Stress"] = mat.planeStress
            material["Density"] = float(np.format_float_scientific(float(mat.density)))
            print(material["Density"])
            if mat.materialSymmetry == "Anisotropic":
                material["Material Symmetry"] = mat.materialSymmetry
                if mat.stiffnessMatrix is not None:
                    for key, value in mat.stiffnessMatrix.matrix:
                        material[key] = float(np.format_float_scientific(float(value)))

            if self.check_if_defined(mat.youngsModulus):
                material["Young's Modulus"] = float(np.format_float_scientific(float(mat.youngsModulus)))

            if self.check_if_defined(mat.shearModulus):
                material["Shear Modulus"] = float(np.format_float_scientific(float(mat.shearModulus)))

            if self.check_if_defined(mat.bulkModulus):
                material["Bulk Modulus"] = float(np.format_float_scientific(float(mat.bu)))

            if self.check_if_defined(mat.poissonsRatio):
                material["Poisson's Ratio"] = float(np.format_float_scientific(float(mat.poissonsRatio)))

            material["Stabilization Type"] = mat.stabilizationType
            material["Thickness"] = float(mat.thickness)
            material["Hourglass Coefficient"] = float(mat.hourglassCoefficient)

            if mat.tensionSeparation:
                material["Tension Separation"] = mat.tensionSeparation
            if self.check_if_defined(mat.actualHorizon):
                material["Actual Horizon"] = float(mat.actualHorizon)
            if self.check_if_defined(mat.yieldStress):
                material["Yield Stress"] = float(mat.yieldStress)
            if self.check_if_defined(mat.nonLinear):
                material["Non linear"] = mat.nonLinear
            if self.check_if_defined(mat.numStateVars):
                material["Number of State Vars"] = mat.numStateVars
            if self.check_if_defined(mat.properties) and "User" in mat.matType:
                material["Number of Properties"] = len(mat.properties)
                for prop in mat.properties:
                    material[prop.name] = float(np.format_float_scientific(float(prop.value)))
            if self.check_if_defined(mat.computePartialStress):
                material["Compute Partial Stress"] = mat.computePartialStress
            if self.check_if_defined(mat.useCollocationNodes):
                material["Use Collocation Nodes"] = mat.useCollocationNodes
            if self.check_if_defined(mat.specificHeatCapacity):
                material["Specific Heat Capacity"] = float(mat.specificHeatCapacity)
            if self.check_if_defined(mat.thermalConductivity):
                material["Thermal Conductivity"] = float(mat.thermalConductivity)
            if self.check_if_defined(mat.heatTransferCoefficient):
                material["Heat Transfer Coefficient"] = float(mat.heatTransferCoefficient)
            if self.check_if_defined(mat.applyThermalFlow):
                material["Apply Thermal Flow"] = mat.applyThermalFlow
            if self.check_if_defined(mat.applyThermalStrain):
                material["Apply Thermal Strain"] = mat.applyThermalStrain
            if self.check_if_defined(mat.applyHeatTransfer):
                material["Apply Heat Transfer"] = mat.applyHeatTransfer
            if self.check_if_defined(mat.thermalBondBased):
                material["Thermal Bond Based"] = mat.thermalBondBased
            if self.check_if_defined(mat.thermalExpansionCoefficient):
                material["Thermal Expansion Coefficient"] = float(mat.thermalExpansionCoefficient)
            if self.check_if_defined(mat.environmentalTemperature):
                material["Environmental Temperature"] = float(mat.environmentalTemperature)
            if self.check_if_defined(mat.printBedTemperature):
                material["Print Bed Temperature"] = float(mat.printBedTemperature)
            if self.check_if_defined(mat.printBedThermalConductivity):
                material["Print Bed Thermal Conductivity"] = float(mat.printBedThermalConductivity)
            if self.check_if_defined(mat.volumeFactor):
                material["Volume Factor"] = float(mat.volumeFactor)
            if self.check_if_defined(mat.volumeLimit):
                material["Volume Limit"] = float(mat.volumeLimit)
            if self.check_if_defined(mat.surfaceCorrection):
                material["Surface Correction"] = float(mat.surfaceCorrection)

            data[mat.name] = material

        return data

    def additive(self):
        data = {}

        for add in self.additive_dict.additiveModels:
            additive = {}
            additive["Additive Model"] = add.additiveType
            additive["Print Temperature"] = float(add.printTemp)

            if self.check_if_defined(add.timeFactor):
                additive["Time Factor"] = float(add.timeFactor)

            data[add.name] = additive
        return data

    def blocks(self):
        data = {}

        for block in self.block_def:
            blocks = {}

            blocks["Block Names"] = block.name
            blocks["Material Model"] = block.material
            if block.damageModel != "" and block.damageModel is not None:
                blocks["Damage Model"] = block.damageModel
            if block.additiveModel != "" and block.additiveModel is not None:
                blocks["Additive Model"] = block.additiveModel
            blocks["Horizon"] = block.horizon
            blocks["Density"] = block.density

            data[block.name] = blocks

        return data

    def damage(self):
        data = {}

        for dam in self.damage_dict:
            damage = {}

            damage["Damage Model"] = str(dam.damageModel)

            if dam.damageModel == "Critical Energy Correspondence":
                damage["Critical Energy"] = float(dam.criticalEnergy)

                if dam.interBlockDamage:
                    damage["Interblock Damage"] = True
                    damage["Number of Blocks"] = dam.numberOfBlocks
                    for interBlock in dam.interBlocks:
                        damage[
                            "Interblock Critical Energy "
                            + str(interBlock.firstBlockId)
                            + "_"
                            + str(interBlock.secondBlockId)
                        ] = str(float(interBlock.value))

            elif dam.damageModel == "Von Mises Stress":
                damage["Critical Von Mises Stress"] = str(float(dam.criticalVonMisesStress))

                if self.check_if_defined(dam.criticalDamage):
                    damage["Critical Damage"] = float(dam.criticalDamage)
                if self.check_if_defined(dam.thresholdDamage):
                    damage["Threshold Damage"] = float(dam.thresholdDamage)
                if self.check_if_defined(dam.criticalDamageToNeglect):
                    damage["Critical Damage To Neglect"] = float(dam.criticalDamageToNeglect)

            else:
                damage["Critical Stretch"] = float(dam.criticalStretch)

            damage["Plane Stress"] = self.two_d
            damage["Only Tension"] = dam.onlyTension
            damage["Detached Nodes Check"] = dam.detachedNodesCheck
            damage["Thickness"] = float(dam.thickness)
            damage["Hourglass Coefficient"] = float(dam.hourglassCoefficient)
            damage["Stabilization Type"] = dam.stabilizationType

            data[dam.name] = damage

        return data

    def solver(self, temp_enabled):
        data = {}

        data["Solver For Displacement"] = self.solver_dict.dispEnabled

        if temp_enabled:
            data["Solver For Temperature"] = True

        data["Verbose"] = self.solver_dict.verbose
        data["Initial Time"] = float(self.solver_dict.initialTime)
        data["Final Time"] = float(self.solver_dict.finalTime)

        if self.solver_dict.stopAfterDamageInitation:
            data["Stop after damage initiation"] = True

        if self.solver_dict.endStepAfterDamage:
            data["End step after damage"] = self.solver_dict.endStepAfterDamage

        if self.solver_dict.stopAfterCertainDamage:
            data["Stop after certain damage value"] = True

        if self.solver_dict.maxDamageValue:
            data["Max. damage value"] = self.solver_dict.maxDamageValue

        if self.solver_dict.stopBeforeDamageInitation:
            data["Stop before damage initiation"] = True

        if self.solver_dict.solvertype == "Verlet":
            data["Verlet"] = {}
            if self.check_if_defined(self.solver_dict.fixedDt):
                data["Verlet"]["Fixed dt"] = float(self.solver_dict.fixedDt)

            data["Verlet"]["Safety Factor"] = float(self.solver_dict.safetyFactor)

            data["Verlet"]["Numerical Damping"] = float(self.solver_dict.numericalDamping)

            if self.check_if_defined(self.solver_dict.adaptivetimeStepping) and self.solver_dict.adaptivetimeStepping:
                data["Verlet"]["Adapt dt"] = True
                data["Verlet"]["Stable Step Difference"] = self.solver_dict.adapt.stableStepDifference
                data["Verlet"]["Maximum Bond Difference"] = self.solver_dict.adapt.maximumBondDifference
                data["Verlet"]["Stable Bond Difference"] = self.solver_dict.adapt.stableBondDifference

        elif self.solver_dict.solvertype == "NOXQuasiStatic":
            data["Peridigm Preconditioner"] = self.solver_dict.peridgimPreconditioner

            data["NOXQuasiStatic"] = {}
            data["NOXQuasiStatic"]["Nonlinear Solver"] = self.solver_dict.nonlinearSolver
            data["NOXQuasiStatic"]["Number of Load Steps"] = self.solver_dict.numberOfLoadSteps
            data["NOXQuasiStatic"]["Max Solver Iterations"] = self.solver_dict.maxSolverIterations
            data["NOXQuasiStatic"]["Relative Tolerance"] = float(self.solver_dict.relativeTolerance)
            data["NOXQuasiStatic"]["Max Age Of Prec"] = self.solver_dict.maxAgeOfPrec
            data["NOXQuasiStatic"]["Direction"] = {}
            data["NOXQuasiStatic"]["Direction"]["Method"] = self.solver_dict.directionMethod
            if self.solver_dict.directionMethod == "Newton":
                data["NOXQuasiStatic"]["Direction"]["Newton"] = {}
                data["NOXQuasiStatic"]["Direction"]["Newton"]["Linear Solver"] = {}
                data["NOXQuasiStatic"]["Direction"]["Newton"]["Linear Solver"][
                    "Jacobian Operator"
                ] = self.solver_dict.newton.jacobianOperator
                data["NOXQuasiStatic"]["Direction"]["Newton"]["Linear Solver"][
                    "Preconditioner"
                ] = self.solver_dict.newton.preconditioner
            data["NOXQuasiStatic"]["Line Search"] = {}
            data["NOXQuasiStatic"]["Line Search"]["Method"] = self.solver_dict.lineSearchMethod

            if self.solver_dict.verletSwitch:
                data["NOXQuasiStatic"]["Switch to Verlet"] = {}
                data["NOXQuasiStatic"]["Switch to Verlet"]["Safety Factor"] = float(
                    self.solver_dict.verlet.safetyFactor
                )
                data["NOXQuasiStatic"]["Switch to Verlet"]["Numerical Damping"] = float(
                    self.solver_dict.verlet.numericalDamping
                )
                data["NOXQuasiStatic"]["Switch to Verlet"]["Output Frequency"] = self.solver_dict.verlet.outputFrequency

        else:
            data["Verlet"] = {}

            data["Verlet"]["Safety Factor"] = float(self.solver_dict.safetyFactor)

            data["Verlet"]["Numerical Damping"] = float(self.solver_dict.numericalDamping)

        return data

    def create_boundary_conditions(self):
        data = {}

        for condition in self.boundary_condition.conditions:
            cond = {}
            node_set_id = self.ns_list.index(condition.blockId)
            cond["Type"] = condition.boundarytype

            if self.check_if_defined(condition.nodeSet):
                cond["Node Set"] = "Node Set " + str(condition.nodeSet)
            else:
                cond["Node Set"] = "Node Set " + str(node_set_id + 1)

            if "Temperature" not in condition.boundarytype:
                cond["Coordinate"] = condition.coordinate
            cond["Value"] = condition.value

            data[condition.name] = cond

        return data

    def contact(self):
        data = {}
        data["Search Radius"] = self.contact_dict.searchRadius
        data["Search Frequency"] = self.contact_dict.searchFrequency

        for models in self.contact_dict.contactModels:
            model = {}
            model["Contact Model"] = models.contactType
            model["Contact Radius"] = models.contactRadius
            model["Spring Constant"] = models.springConstant

            data[models.name] = model
        interactions = {}
        for interaction in self.contact_dict.interactions:
            inter = {}
            inter["First Block"] = self.block_def[interaction.firstBlockId - 1].name
            inter["Second Block"] = self.block_def[interaction.secondBlockId - 1].name
            inter["Contact Model"] = self.contact_dict.contactModels[interaction.contactModelId - 1].name

            interactions["Interaction " + str(interaction.firstBlockId) + "_" + str(interaction.secondBlockId)] = inter
        data["Interactions"] = interactions

        return data

    def compute(self):
        data = {}
        for out in self.compute_dict:
            compute = {}
            if out.computeClass == "Nearest_Point_Data":
                compute["Compute Class"] = "Nearest_Point_Data"
                compute["X"] = out.x_value
                compute["Y"] = out.y_value
                compute["Z"] = out.z_value
            else:
                compute["Compute Class"] = "Block_Data"
                compute["Calculation Type"] = out.calculationType
                compute["Block"] = out.blockName
            compute["Variable"] = out.variable
            compute["Output Label"] = out.name

            data[out.name] = compute

        return data

    def output(self):
        data = {}
        idx = 0
        for out in self.output_dict:
            output = {}
            output["Output File Type"] = "ExodusII"
            output["Output Format"] = "BINARY"
            output["Output Filename"] = self.filename + "_" + out.name

            if out.InitStep != 0:
                output["Initial Output Step"] = out.InitStep
            if out.useOutputFrequency:
                output["Output Frequency"] = out.Frequency
            else:
                output["Number of Output Steps"] = out.numberOfOutputSteps
            output["Parallel Write"] = True
            if out.Write_After_Damage:
                output["Write After Damage"] = True

            variable = {}
            for outputs in out.selectedOutputs:
                if outputs == "Velocity_Gradient":
                    variable["Velocity_Gradient_X"] = True
                    variable["Velocity_Gradient_Y"] = True
                    variable["Velocity_Gradient_Z"] = True
                elif outputs == "PiolaStressTimesInvShapeTensor":
                    variable["PiolaStressTimesInvShapeTensorX"] = True
                    variable["PiolaStressTimesInvShapeTensorY"] = True
                    variable["PiolaStressTimesInvShapeTensorZ"] = True
                else:
                    variable[outputs] = True

                output["Output Variables"] = variable
            if self.check_if_defined(self.compute_dict):
                for compute in self.compute_dict:
                    variable[compute.name] = True

            output["Output Variables"] = variable

            data["Output" + str(idx + 1)] = output
            idx += 1
        return data

    def create_yaml(self):
        data = {"PeriLab": {}}
        data["PeriLab"]["Physics"] = {}

        data["PeriLab"]["Discretization"] = self.load_mesh()
        if self.check_if_defined(self.bondfilters):
            data["PeriLab"]["Bond Filters"] = self.create_bond_filter()
        data["PeriLab"]["Physics"]["Material Models"] = self.materials()
        if self.check_if_defined(self.additive_dict):
            if self.additive_dict.enabled and len(self.additive_dict.additiveModels) > 0:
                data["PeriLab"]["Additive Models"] = self.additive()
        data["PeriLab"]["Blocks"] = self.blocks()
        if self.check_if_defined(self.damage_dict):
            data["PeriLab"]["Physics"]["Damage Models"] = self.damage()
        data["PeriLab"]["Solver"] = self.solver(self.temp_enabled(self.material_dict))
        if self.check_if_defined(self.boundary_condition.conditions):
            data["PeriLab"]["Boundary Conditions"] = self.create_boundary_conditions()
        if self.check_if_defined(self.contact_dict):
            if self.contact_dict.enabled and len(self.contact_dict.contactModels) > 0:
                data["PeriLab"]["Contact"] = self.contact()
        if self.check_if_defined(self.compute_dict):
            data["PeriLab"]["Compute Class Parameters"] = self.compute()
        data["PeriLab"]["Outputs"] = self.output()

        yaml_string = yaml.dump(data, default_flow_style=False)
        return yaml_string
