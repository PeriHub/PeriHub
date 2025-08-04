# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0


import numpy as np
import yaml


class YAMLcreatorPeriLab:
    def __init__(self, model_writer, block_def=None):
        self.filename = model_writer.filename
        self.ns_name = model_writer.ns_name
        self.node_set_ids = model_writer.node_set_ids
        self.block_def = block_def

        self.mesh_file = model_writer.model_data.model.meshFile
        self.boundary_condition = model_writer.model_data.boundaryConditions
        self.solver_dict = model_writer.model_data.solvers
        self.damage_dict = model_writer.model_data.damages
        self.material_dict = model_writer.model_data.materials
        self.thermal_dict = model_writer.model_data.thermal
        self.additive_dict = model_writer.model_data.additive
        self.compute_dict = model_writer.model_data.computes
        self.output_dict = model_writer.model_data.outputs
        self.contact_dict = model_writer.model_data.contact
        self.bondfilters = model_writer.model_data.bondFilters
        self.preCalculations = model_writer.model_data.preCalculations
        self.disc_dict = model_writer.model_data.discretization
        self.disc_type = model_writer.model_data.discretization.discType
        # self.two_d = model_writer.model_data.model.twoDimensional

    @staticmethod
    def check_if_defined(obj):
        return obj is not None and obj != 0 and obj != ""

    def load_mesh(self):
        data = {}

        if self.disc_type == "txt":
            data["Type"] = "Text File"

            # if self.check_if_defined(self.boundary_condition.nodeSets):
            #     for nodeSet in self.boundary_condition.nodeSets:
            #         data["Node Sets"]["Node Set " + str(nodeSet.nodeSetId)] = nodeSet.file
            # else:
            if self.check_if_defined(self.disc_dict.nodeSets) and len(self.disc_dict.nodeSets) > 0:
                data["Node Sets"] = {}
                for nodeSet in self.disc_dict.nodeSets:
                    data["Node Sets"]["Node Set " + str(nodeSet.nodeSetId)] = nodeSet.file
            else:
                if len(self.node_set_ids) > 0:
                    data["Node Sets"] = {}
                for idx in range(0, len(self.node_set_ids)):
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

        elif self.disc_type == "gcode":
            data["Type"] = "Gcode"

            if self.check_if_defined(self.disc_dict.nodeSets) and len(self.disc_dict.nodeSets) > 0:
                data["Node Sets"] = {}
                for nodeSet in self.disc_dict.nodeSets:
                    data["Node Sets"]["Node Set " + str(nodeSet.nodeSetId)] = nodeSet.file

            if self.check_if_defined(self.mesh_file):
                data["Input Mesh File"] = self.mesh_file
            else:
                data["Input Mesh File"] = self.filename + ".gcode"
            data["Gcode"] = {}

            data["Gcode"]["Overwrite Mesh"] = self.disc_dict.gcode.overwriteMesh
            data["Gcode"]["Sampling"] = self.disc_dict.gcode.sampling
            data["Gcode"]["Width"] = self.disc_dict.gcode.width
            data["Gcode"]["Scale"] = self.disc_dict.gcode.scale

            if (
                self.check_if_defined(self.disc_dict.gcode.blockFunctions)
                and len(self.disc_dict.gcode.blockFunctions) > 0
            ):
                data["Gcode"]["Blocks"] = {}

                for block in self.disc_dict.gcode.blockFunctions:
                    data["Gcode"]["Blocks"][block.id] = block.function

        return data

    def create_bond_filter(self):
        data = {}

        for bond_filter in self.bondfilters:
            filter = {}
            filter["Type"] = bond_filter.type
            filter["Normal X"] = bond_filter.normalX
            filter["Normal Y"] = bond_filter.normalY
            filter["Normal Z"] = bond_filter.normalZ

            if self.check_if_defined(bond_filter.allow_contact):
                filter["Allow Contact"] = bond_filter.allow_contact

            if bond_filter.type == "Rectangular_Plane":
                filter["Lower Left Corner X"] = bond_filter.lowerLeftCornerX
                filter["Lower Left Corner Y"] = bond_filter.lowerLeftCornerY
                filter["Lower Left Corner Z"] = bond_filter.lowerLeftCornerZ
                filter["Bottom Unit Vector X"] = bond_filter.bottomUnitVectorX
                filter["Bottom Unit Vector Y"] = bond_filter.bottomUnitVectorY
                filter["Bottom Unit Vector Z"] = bond_filter.bottomUnitVectorZ
                filter["Bottom Length"] = bond_filter.bottomLength
                filter["Side Length"] = bond_filter.sideLength
            elif bond_filter.type == "Disk":
                filter["Center X"] = bond_filter.centerX
                filter["Center Y"] = bond_filter.centerY
                filter["Center Z"] = bond_filter.centerZ
                filter["Radius"] = bond_filter.radius
            data[bond_filter.name] = filter

        return data

    def preCalculation(self):
        data = {}

        data["Deformed Bond Geometry"] = True
        data["Deformation Gradient"] = True
        data["Shape Tensor"] = True
        data["Bond Associated Shape Tensorr"] = False
        data["Bond Associated Deformation Gradient"] = False

        return data

    def materials(self):
        data = {}

        for mat in self.material_dict:
            material = {}
            material["Material Model"] = " + ".join([str(x) for x in mat.matType])
            if mat.materialSymmetry == "Anisotropic" and mat.planeStress:
                material["Symmetry"] = "anisotropic plane stress"
            elif mat.materialSymmetry == "Isotropic" and mat.planeStress:
                material["Symmetry"] = "isotropic plane stress"
            elif mat.materialSymmetry == "Isotropic" and mat.planeStrain:
                material["Symmetry"] = "isotropic plane strain"
            elif mat.materialSymmetry == "Anisotropic" and mat.planeStrain:
                material["Symmetry"] = "anisotropic plane strain"
            if mat.materialSymmetry == "Anisotropic":
                # material["Material Symmetry"] = mat.materialSymmetry
                if mat.stiffnessMatrix is not None:
                    for key, value in mat.stiffnessMatrix.matrix:
                        material[key] = float(np.format_float_scientific(float(value)))

            if self.check_if_defined(mat.youngsModulus):
                material["Young's Modulus"] = float(np.format_float_scientific(float(mat.youngsModulus)))

            if self.check_if_defined(mat.shearModulus):
                material["Shear Modulus"] = float(np.format_float_scientific(float(mat.shearModulus)))

            if self.check_if_defined(mat.bulkModulus):
                material["Bulk Modulus"] = float(np.format_float_scientific(float(mat.bulkModulus)))

            if self.check_if_defined(mat.poissonsRatio):
                material["Poisson's Ratio"] = float(np.format_float_scientific(float(mat.poissonsRatio)))

            material["Zero Energy Control"] = "Global"
            # material["Thickness"] = float(mat.thickness)
            # material["Hourglass Coefficient"] = float(mat.hourglassCoefficient)

            # if mat.tensionSeparation:
            #     material["Tension Separation"] = mat.tensionSeparation
            # if self.check_if_defined(mat.actualHorizon):
            #     material["Actual Horizon"] = float(mat.actualHorizon)
            if self.check_if_defined(mat.yieldStress):
                material["Yield Stress"] = float(mat.yieldStress)
            # if self.check_if_defined(mat.nonLinear):
            #     material["Non linear"] = mat.nonLinear
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
            # if self.check_if_defined(mat.specificHeatCapacity):
            #     material["Specific Heat Capacity"] = float(mat.specificHeatCapacity)
            # if self.check_if_defined(mat.thermalConductivity):
            #     material["Thermal Conductivity"] = float(mat.thermalConductivity)
            # if self.check_if_defined(mat.heatTransferCoefficient):
            #     material["Heat Transfer Coefficient"] = float(mat.heatTransferCoefficient)
            # if self.check_if_defined(mat.applyThermalFlow):
            #     material["Apply Thermal Flow"] = mat.applyThermalFlow
            # if self.check_if_defined(mat.applyThermalStrain):
            #     material["Apply Thermal Strain"] = mat.applyThermalStrain
            # if self.check_if_defined(mat.applyHeatTransfer):
            #     material["Apply Heat Transfer"] = mat.applyHeatTransfer
            # if self.check_if_defined(mat.thermalBondBased):
            #     material["Thermal Bond Based"] = mat.thermalBondBased
            # if self.check_if_defined(mat.thermalExpansionCoefficient):
            #     material["Thermal Expansion Coefficient"] = float(mat.thermalExpansionCoefficient)
            # if self.check_if_defined(mat.environmentalTemperature):
            #     material["Environmental Temperature"] = float(mat.environmentalTemperature)
            # if self.check_if_defined(mat.printBedTemperature):
            #     material["Print Bed Temperature"] = float(mat.printBedTemperature)
            # if self.check_if_defined(mat.printBedThermalConductivity):
            #     material["Print Bed Thermal Conductivity"] = float(mat.printBedThermalConductivity)
            # if self.check_if_defined(mat.volumeFactor):
            #     material["Volume Factor"] = float(mat.volumeFactor)
            # if self.check_if_defined(mat.volumeLimit):
            #     material["Volume Limit"] = float(mat.volumeLimit)
            # if self.check_if_defined(mat.surfaceCorrection):
            #     material["Surface Correction"] = float(mat.surfaceCorrection)

            data[mat.name] = material

        return data

    def thermal(self):
        data = {}

        for therm in self.thermal_dict.thermalModels:
            thermal = {}
            thermal["Thermal Model"] = " + ".join([str(x) for x in therm.thermalModel])
            # if self.check_if_defined(therm.thermalBondBased):
            thermal["Type"] = therm.thermalType
            if self.check_if_defined(therm.thermalConductivity):
                thermal["Thermal Conductivity"] = float(therm.thermalConductivity)
            if self.check_if_defined(therm.thermalConductivityPrintBed):
                thermal["Thermal Conductivity Print Bed"] = float(therm.thermalConductivityPrintBed)
            if self.check_if_defined(therm.printBedTemperature):
                thermal["Print Bed Temperature"] = float(therm.printBedTemperature)
            if self.check_if_defined(therm.environmentalTemperature):
                thermal["Environmental Temperature"] = float(therm.environmentalTemperature)
            if self.check_if_defined(therm.heatTransferCoefficient):
                thermal["Heat Transfer Coefficient"] = float(therm.heatTransferCoefficient)

            data[therm.name] = thermal
        return data

    def additive(self):
        data = {}

        for add in self.additive_dict.additiveModels:
            additive = {}
            additive["Additive Model"] = add.additiveType
            additive["Print Temperature"] = float(add.printTemp)

            # if self.check_if_defined(add.timeFactor):
            #     additive["Time Factor"] = float(add.timeFactor)

            data[add.name] = additive
        return data

    def blocks(self, max_block_id):
        data = {}

        for block in self.block_def:
            if block.blocksId > max_block_id:
                continue
            blocks = {}

            # blocks["Block Names"] = block.name
            blocks["Block ID"] = block.blocksId
            if block.material != "" and block.material is not None:
                blocks["Material Model"] = block.material
            if block.damageModel != "" and block.damageModel is not None:
                blocks["Damage Model"] = block.damageModel
            if block.thermalModel != "" and block.thermalModel is not None:
                blocks["Thermal Model"] = block.thermalModel
            if block.additiveModel != "" and block.additiveModel is not None:
                blocks["Additive Model"] = block.additiveModel
            blocks["Horizon"] = block.horizon
            blocks["Density"] = block.density
            if self.check_if_defined(block.specificHeatCapacity):
                blocks["Specific Heat Capacity"] = block.specificHeatCapacity

            data[block.name] = blocks

        return data

    def damage(self, max_block_id):
        data = {}

        for dam in self.damage_dict:
            damage = {}

            damage["Damage Model"] = str(dam.damageModel)

            if dam.damageModel == "Critical Energy":
                damage["Critical Value"] = float(dam.criticalEnergy)

            elif dam.damageModel == "Von Mises Stress":
                damage["Critical Von Mises Stress"] = float(dam.criticalVonMisesStress)

                if self.check_if_defined(dam.criticalDamage):
                    damage["Critical Damage"] = float(dam.criticalDamage)
                if self.check_if_defined(dam.thresholdDamage):
                    damage["Threshold Damage"] = float(dam.thresholdDamage)
                if self.check_if_defined(dam.criticalDamageToNeglect):
                    damage["Critical Damage To Neglect"] = float(dam.criticalDamageToNeglect)

            elif dam.damageModel == "Critical Stretch":
                damage["Critical Value"] = float(dam.criticalStretch)
            else:
                damage["Critical Value"] = 0.0

            if dam.interBlockDamage:
                allowed = False
                for interBlock in dam.interBlocks:
                    if interBlock.firstBlockId <= max_block_id and interBlock.secondBlockId <= max_block_id:
                        allowed = True
                        break
                if allowed:
                    damage["Interblock Damage"] = {}
                    for interBlock in dam.interBlocks:
                        damage["Interblock Damage"][
                            "Interblock Critical Value "
                            + str(interBlock.firstBlockId)
                            + "_"
                            + str(interBlock.secondBlockId)
                        ] = float(interBlock.value)
            if dam.anistropicDamage:
                damage["Anisotropic Damage"] = {}
                damage["Anisotropic Damage"]["Critical Value X"] = float(dam.anistropicDamageX)
                damage["Anisotropic Damage"]["Critical Value Y"] = float(dam.anistropicDamageY)
                # if not self.two_d:
                damage["Anisotropic Damage"]["Critical Value Z"] = float(dam.anistropicDamageZ)
            # damage["Plane Stress"] = self.two_d
            if self.check_if_defined(dam.onlyTension):
                damage["Only Tension"] = dam.onlyTension
            # damage["Detached Nodes Check"] = dam.detachedNodesCheck
            if self.check_if_defined(dam.thickness):
                damage["Thickness"] = float(dam.thickness)
            # damage["Hourglass Coefficient"] = float(dam.hourglassCoefficient)
            # damage["Stabilization Type"] = dam.stabilizationType

            data[dam.name] = damage

        return data

    def solver(self, id=0, multistep=False):
        data = {}
        print(self.solver_dict[id])
        if multistep:
            data["Step ID"] = self.solver_dict[id].stepId

        data["Material Models"] = self.solver_dict[id].matEnabled
        if self.check_if_defined(self.solver_dict[id].damEnabled):
            data["Damage Models"] = self.solver_dict[id].damEnabled
        if self.check_if_defined(self.solver_dict[id].tempEnabled):
            data["Thermal Models"] = self.solver_dict[id].tempEnabled
        if self.check_if_defined(self.solver_dict[id].addEnabled):
            data["Additive Models"] = self.solver_dict[id].addEnabled

        # data["Verbose"] = self.solver_dict[id].verbose

        if self.check_if_defined(self.solver_dict[id].additionalTime):
            data["Additional Time"] = float(self.solver_dict[id].additionalTime)
        else:
            data["Initial Time"] = float(self.solver_dict[id].initialTime)
            data["Final Time"] = float(self.solver_dict[id].finalTime)

        if self.solver_dict[id].stopAfterDamageInitation:
            data["Stop after damage initiation"] = True

        # if self.solver_dict[id].stopAfterCertainDamage and self.solver_dict[id].endStepAfterDamage:
        #     data["End step after damage"] = self.solver_dict[id].endStepAfterDamage

        # if self.solver_dict[id].stopAfterCertainDamage:
        #     data["Stop after certain damage value"] = True

        # if self.solver_dict[id].stopAfterCertainDamage and self.solver_dict[id].maxDamageValue:
        #     data["Max. damage value"] = self.solver_dict[id].maxDamageValue

        if self.solver_dict[id].stopBeforeDamageInitation:
            data["Stop before damage initiation"] = True

        if self.solver_dict[id].solvertype == "Verlet":
            data["Verlet"] = {}
            if self.check_if_defined(self.solver_dict[id].fixedDt):
                data["Verlet"]["Fixed dt"] = float(self.solver_dict[id].fixedDt)

            data["Verlet"]["Safety Factor"] = float(self.solver_dict[id].safetyFactor)

            if (
                self.check_if_defined(self.solver_dict[id].adaptivetimeStepping)
                and self.solver_dict[id].adaptivetimeStepping
            ):
                data["Verlet"]["Adapt dt"] = True
                data["Verlet"]["Stable Step Difference"] = self.solver_dict[id].adapt.stableStepDifference
                data["Verlet"]["Maximum Bond Difference"] = self.solver_dict[id].adapt.maximumBondDifference
                data["Verlet"]["Stable Bond Difference"] = self.solver_dict[id].adapt.stableBondDifference
        elif self.solver_dict[id].solvertype == "Static":
            data["Number of Steps"] = self.solver_dict[id].static.numberOfSteps
            data["Static"] = {}
            if self.check_if_defined(self.solver_dict[id].static.maximumNumberOfIterations):
                data["Static"]["Maximum number of iterations"] = int(
                    self.solver_dict[id].static.maximumNumberOfIterations
                )
            if self.check_if_defined(self.solver_dict[id].static.showSolverIteration):
                data["Static"]["Show solver iteration"] = self.solver_dict[id].static.showSolverIteration
            if self.check_if_defined(self.solver_dict[id].static.residualTolerance):
                data["Static"]["Residual tolerance"] = float(self.solver_dict[id].static.residualTolerance)
            if self.check_if_defined(self.solver_dict[id].static.solutionTolerance):
                data["Static"]["Solution tolerance"] = float(self.solver_dict[id].static.solutionTolerance)
            if self.check_if_defined(self.solver_dict[id].static.linearStartValue):
                data["Static"]["Linear Start Value"] = self.solver_dict[id].static.linearStartValue
            if self.check_if_defined(self.solver_dict[id].static.residualScaling):
                data["Static"]["Residual scaling"] = float(self.solver_dict[id].static.residualScaling)
            if self.check_if_defined(self.solver_dict[id].static.m):
                data["Static"]["m"] = int(self.solver_dict[id].static.m)
        else:
            data["Verlet"] = {}

            data["Verlet"]["Safety Factor"] = float(self.solver_dict[id].safetyFactor)

            data["Verlet"]["Numerical Damping"] = float(self.solver_dict[id].numericalDamping)

        if self.check_if_defined(self.solver_dict[id].calculateCauchy):
            data["Calculate Cauchy"] = self.solver_dict[id].calculateCauchy

        if self.check_if_defined(self.solver_dict[id].calculateVonMises):
            data["Calculate von Mises stress"] = self.solver_dict[id].calculateVonMises

        if self.check_if_defined(self.solver_dict[id].calculateStrain):
            data["Calculate Strain"] = self.solver_dict[id].calculateStrain

        return data

    def multistepSolver(self):
        data = {}

        for i, _ in enumerate(self.solver_dict):
            data[self.solver_dict[i].name] = self.solver(i, True)
        return data

    def create_boundary_conditions(self, multistep):
        data = {}

        for condition in self.boundary_condition.conditions:
            cond = {}
            node_set_id = self.node_set_ids.index(condition.blockId)
            cond["Type"] = condition.boundarytype
            cond["Variable"] = condition.variable

            if self.check_if_defined(condition.nodeSet):
                cond["Node Set"] = "Node Set " + str(condition.nodeSet)
            else:
                cond["Node Set"] = "Node Set " + str(node_set_id + 1)

            if self.check_if_defined(condition.stepId) and multistep:
                steps = ""
                for step in condition.stepId:
                    steps += str(step) + ", "
                cond["Step ID"] = steps[:-2]

            if "Temperature" not in condition.variable:
                cond["Coordinate"] = condition.coordinate
            cond["Value"] = condition.value

            data[condition.name] = cond

        return data

    def contact(self):
        data = {}
        data["Globals"] = {}
        data["Globals"]["Only Surface Contact Nodes"] = self.contact_dict.onlySurfaceContactNodes
        data["Globals"]["Global Search Frequency"] = self.contact_dict.searchFrequency
        for con in self.contact_dict.contactModels:
            contact = {}
            contact["Type"] = con.contactType
            contact["Contact Radius"] = con.contactRadius
            contact["Contact Stiffness"] = con.contactStiffness
            groups = {}
            for group in con.contactGroups:
                group_dict = {}
                group_dict["Master Block ID"] = group.masterBlockId
                group_dict["Slave Block ID"] = group.slaveBlockId
                group_dict["Search Radius"] = group.searchRadius
                groups[group.name] = group_dict

            contact["Contact Groups"] = groups
            data[con.name] = contact
        return data

    def compute(self):
        data = {}
        for out in self.compute_dict:
            compute = {}
            if out.computeClass == "Node_Set_Data":
                compute["Compute Class"] = "Node_Set_Data"
                compute["Calculation Type"] = out.calculationType
                compute["Node Set"] = "Node Set " + str(out.nodeSetId)
            elif out.computeClass == "Block_Data":
                compute["Compute Class"] = "Block_Data"
                compute["Calculation Type"] = out.calculationType
                compute["Block"] = out.blockName
            elif out.computeClass == "Nearest_Point_Data":
                compute["Compute Class"] = "Nearest_Point_Data"
                compute["X"] = out.x_value
                compute["Y"] = out.y_value
                compute["Z"] = out.z_value
            compute["Variable"] = out.variable
            # compute["Output Label"] = out.name

            data[out.name] = compute

        return data

    def output(self):
        data = {}
        idx = 0
        for out in self.output_dict:
            output = {}
            output["Output File Type"] = out.selectedFileType
            output["Output Filename"] = self.filename + "_" + out.name

            if out.InitStep != 0:
                output["Initial Output Step"] = out.InitStep
            if out.useOutputFrequency:
                output["Output Frequency"] = out.Frequency
            else:
                output["Number of Output Steps"] = out.numberOfOutputSteps
            # output["Parallel Write"] = True
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

    def create_yaml(self, max_block_id):

        multistep = len(self.solver_dict) > 1

        data = {"PeriLab": {}}
        data["PeriLab"]["Models"] = {}

        data["PeriLab"]["Discretization"] = self.load_mesh()
        if self.check_if_defined(self.bondfilters) and len(self.bondfilters) > 0:
            data["PeriLab"]["Discretization"]["Bond Filters"] = self.create_bond_filter()
        if self.check_if_defined(self.preCalculations):
            data["PeriLab"]["Models"]["Pre Calculation"] = self.preCalculation()
        if self.check_if_defined(self.material_dict) and len(self.material_dict) > 0:
            data["PeriLab"]["Models"]["Material Models"] = self.materials()
        if self.check_if_defined(self.thermal_dict):
            if self.thermal_dict.enabled and len(self.thermal_dict.thermalModels) > 0:
                data["PeriLab"]["Models"]["Thermal Models"] = self.thermal()
        if self.check_if_defined(self.additive_dict):
            if self.additive_dict.enabled and len(self.additive_dict.additiveModels) > 0:
                data["PeriLab"]["Models"]["Additive Models"] = self.additive()
        data["PeriLab"]["Blocks"] = self.blocks(max_block_id)
        if self.check_if_defined(self.damage_dict) and len(self.damage_dict) > 0:
            data["PeriLab"]["Models"]["Damage Models"] = self.damage(max_block_id)
        if multistep:
            data["PeriLab"]["Multistep Solver"] = self.multistepSolver()
        else:
            data["PeriLab"]["Solver"] = self.solver()
        if self.check_if_defined(self.boundary_condition.conditions) and len(self.boundary_condition.conditions) > 0:
            data["PeriLab"]["Boundary Conditions"] = self.create_boundary_conditions(multistep)
        if self.check_if_defined(self.contact_dict):
            if self.contact_dict.enabled and len(self.contact_dict.contactModels) > 0:
                data["PeriLab"]["Contact"] = self.contact()
        if self.check_if_defined(self.compute_dict):
            if len(self.compute_dict) > 0:
                data["PeriLab"]["Compute Class Parameters"] = self.compute()
        data["PeriLab"]["Outputs"] = self.output()

        yaml_string = yaml.dump(data, default_flow_style=False)
        return yaml_string
