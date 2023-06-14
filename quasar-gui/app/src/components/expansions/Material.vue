<template>
    <div>
            <q-list
                v-for="material, index in materials"
                :key="material.materialsId"
                style="padding: 0px"
            >
                <div v-bind:style="(material.materialsId % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
                    <h4 class="my-title">Material {{material.materialsId}}</h4>
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="material.name"
                            :rules="[rules.required, rules.name]"
                            :label="materialKeys.name"
                            standout
                            dense
                        ></q-input>
                        <q-btn flat icon="fas fa-trash-alt" @click="removeMaterial(index)">
                            <q-tooltip>
                                Remove Material
                            </q-tooltip>
                        </q-btn>
                    </div>
                    <div class="row my-row">
                        <q-select 
                            class="my-input"
                            :options="materialModelName"
                            v-model="material.matType"
                            :label="materialKeys.matType"
                            standout
                            dense
                        ></q-select>
                    </div>
                    <div v-if="material.matType.includes('User')">
                      <q-list
                        v-for="prop, subindex in material.properties"
                        :key="prop.materialsPropId"
                        style="padding: 0px"
                      >
                        <div class="row my-row">
                            <q-input 
                                class="my-input"
                                v-model="prop.value"
                                :rules="[rules.required, rules.float]"
                                :label="prop.name"
                                standout
                                dense
                            ></q-input>
                            <q-btn flat icon="fas fa-trash-alt" @click="removeProp(index, subindex)">
                                <q-tooltip>
                                    Remove Property
                                </q-tooltip>
                            </q-btn>
                        </div>
                      </q-list>
                        <div class="row my-row">
                            <q-btn flat icon="fas fa-plus" @click="addProp(index)">
                                <q-tooltip>
                                    Add Property
                                </q-tooltip>
                            </q-btn>
                        </div>
                        <div class="row my-row">
                            <q-btn flat icon="fas fa-upload" @click="uploadProps(index)">
                                <q-tooltip>
                                    Upload Property
                                </q-tooltip>
                            </q-btn>
                          
                            <q-btn flat icon="fas fa-upload" @click="uploadSo">
                                <q-tooltip>
                                    Upload shared Librarie
                                </q-tooltip>
                            </q-btn>
                            <q-input 
                                class="my-input"
                                v-model="material.numStateVars"
                                :rules="[rules.required, rules.int]"
                                :label="materialKeys.numStateVars"
                                @update:model-value="bus.emit('addStateVarsToOutput', material.numStateVars)"
                                standout
                                dense
                            ></q-input>
                        </div>
                    </div>
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="material.density"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.density"
                            standout
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="material.poissonsRatio"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.poissonsRatio"
                            clearable
                            standout
                            dense
                        ></q-input>
                    </div>
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="material.bulkModulus"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.bulkModulus"
                            clearable
                            standout
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="material.shearModulus"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.shearModulus"
                            clearable
                            standout
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="material.youngsModulus"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.youngsModulus"
                            clearable
                            standout
                            dense
                        ></q-input>
                    </div>
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="material.tensionSeparation"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.tensionSeparation"
                            clearable
                            standout
                            dense
                        ></q-input>
                        <q-toggle
                            class="my-toggle"
                            v-model="material.nonLinear"
                            :label="materialKeys.nonLinear"
                            dense
                        ></q-toggle>
                        <q-toggle
                            class="my-toggle"
                            v-model="material.planeStress"
                            :label="materialKeys.planeStress"
                            dense
                        ></q-toggle>
                        <q-toggle
                            v-if="material.matType=='Elastic'"
                            class="my-toggle"
                            v-model="material.computePartialStress"
                            :label="materialKeys.computePartialStress"
                            dense
                        ></q-toggle>
                    </div>
                    <div class="row my-row">
                        <q-select 
                            class="my-input"
                            :options="materialSymmetry"
                            v-model="material.materialSymmetry"
                            v-show="['Linear Elastic Correspondence','Anisotropic Elastic Bond Associated Correspondence'].include(material.matType)"
                            :label="materialKeys.materialSymmetry"
                            standout
                            dense
                        ></q-select>
                    </div>
                    <div class="row my-row" v-if="material.materialSymmetry=='Anisotropic' & ['Linear Elastic Correspondence','Anisotropic Elastic Bond Associated Correspondence'].include(material.matType)">
                      <q-list
                        v-for="params in material.Parameter"
                        :key="params.index"
                        style="padding: 0px"
                      >
                        <q-input 
                            class="my-input"
                            v-model="params.value"
                            :rules="[rules.required, rules.float]"
                            :label="params.name"
                            standout
                            dense
                        ></q-input>
                      </q-list>
                    </div>
                    <div class="row my-row">
                        <q-select 
                            class="my-input"
                            :options="stabilizationType"
                            v-model="material.stabilizationType"
                            :label="materialKeys.stabilizationType"
                            standout
                            dense
                        ></q-select>
                    </div>  
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="material.thickness"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.thickness"
                            standout
                            dense
                        ></q-input>
                    </div> 
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="material.hourglassCoefficient"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.hourglassCoefficient"
                            standout
                            dense
                        ></q-input>
                    </div> 
                    <div class="row my-row" v-show="material.matType=='Elastic Plastic Hypoelastic Correspondence'">
                        <q-input 
                            class="my-input"
                            v-model="material.actualHorizon"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.actualHorizon"
                            standout
                            dense
                        ></q-input>
                    </div> 
                    <div class="row my-row"  v-show="material.matType.includes('Plastic')">
                        <q-input 
                            class="my-input"
                            v-model="material.yieldStress"
                            :rules="[rules.required, rules.float]"
                            :label="materialKeys.yieldStress"
                            standout
                            dense
                        ></q-input>
                    </div>
                    <q-separator></q-separator>
                    <h6 class="my-title">Thermal</h6>
                    <q-toggle
                        class="my-toggle"
                        v-model="material.enableThermal"
                        label="Enabled"
                        standout
                        dense
                    ></q-toggle>
                    <div v-if="material.enableThermal">
                        <div class="row my-row">
                            <q-input 
                                class="my-input"
                                v-model="material.specificHeatCapacity"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.specificHeatCapacity"
                                standout
                                dense
                            ></q-input>
                            <q-input 
                                class="my-input"
                                v-model="material.thermalConductivity"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.thermalConductivity"
                                standout
                                dense
                            ></q-input>
                            <q-input 
                                class="my-input"
                                v-model="material.heatTransferCoefficient"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.heatTransferCoefficient"
                                standout
                                dense
                            ></q-input>
                        </div> 
                        <div class="row my-row">
                            <q-toggle
                                class="my-toggle"
                                v-model="material.applyThermalFlow"
                                :label="materialKeys.applyThermalFlow"
                                dense
                            ></q-toggle>
                            <q-toggle
                                class="my-toggle"
                                v-model="material.applyThermalStrain"
                                :label="materialKeys.applyThermalStrain"
                                dense
                            ></q-toggle>
                            <q-toggle
                                class="my-toggle"
                                v-model="material.applyHeatTransfer"
                                :label="materialKeys.applyHeatTransfer"
                                dense
                            ></q-toggle>
                            <q-toggle
                                class="my-toggle"
                                v-model="material.thermalBondBased"
                                :label="materialKeys.thermalBondBased"
                                dense
                            ></q-toggle>
                        </div> 
                        <div class="row my-row">
                            <q-input 
                                class="my-input"
                                v-model="material.thermalExpansionCoefficient"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.thermalExpansionCoefficient"
                                clearable
                                standout
                                dense
                            ></q-input>
                            <q-input 
                                class="my-input"
                                v-model="material.environmentalTemperature"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.environmentalTemperature"
                                clearable
                                standout
                                dense
                            ></q-input>
                        </div> 
                        <q-separator></q-separator>
                        <h6 class="my-title">Additive</h6>
                        <div class="row my-row">
                            <q-input 
                                class="my-input"
                                v-model="material.printBedTemperature"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.printBedTemperature"
                                clearable
                                standout
                                dense
                            ></q-input>
                            <q-input 
                                class="my-input"
                                v-model="material.printBedThermalConductivity"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.printBedThermalConductivity"
                                clearable
                                standout
                                dense
                            ></q-input>
                        </div> 
                        <div class="row my-row">
                            <q-input 
                                class="my-input"
                                v-model="material.volumeFactor"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.volumeFactor"
                                clearable
                                standout
                                dense
                            ></q-input>
                            <q-input 
                                class="my-input"
                                v-model="material.volumeLimit"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.volumeLimit"
                                clearable
                                standout
                                dense
                            ></q-input>
                            <q-input 
                                class="my-input"
                                v-model="material.surfaceCorrection"
                                :rules="[rules.required, rules.float]"
                                :label="materialKeys.surfaceCorrection"
                                clearable
                                standout
                                dense
                            ></q-input>
                        </div> 
                    </div>
                </div>
            </q-list>
            <q-btn flat icon="fas fa-plus" @click="addMaterial">
                <q-tooltip>
                    Add Material
                </q-tooltip>
            </q-btn>
            <input
                type="file"
                style="display: none"
                ref="multiSoInput"
                multiple
                accept=".so"
                @change="onMultiFilePicked"
            />
            <input
                type="file"
                style="display: none"
                ref="propsInput"
                multiple
                accept=".inp"
                @change="onPropsFilePicked"
            />
        </div>
</template>
  
<script>
    import { computed, defineComponent } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { useViewStore } from 'stores/view-store';
    import { inject } from 'vue'
    import rules from "assets/rules.js";
    import { deepCopy } from '../../utils/functions.js'
  
    export default defineComponent({
        name: 'MaterialSettings',
        setup() {
            const store = useModelStore();
            const viewStore = useViewStore();
            const materials = computed(() => store.modelData.materials)
            const modelData = computed(() => store.modelData)
            const bus = inject('bus')
            return {
                viewStore,
                materials,
                modelData,
                rules,
                bus
            }
        },
        created() {
        },
        data() {
            return {
                selectedMaterial: 0,
                materialModelName: [
                    "Diffusion",
                    "Elastic",
                    "Elastic Bond Based",
                    "Elastic Bond Associated Correspondence",
                    "Anisotropic Elastic Bond Associated Correspondence",
                    "Elastic Correspondence",
                    "Elastic Correspondence Partial Stress",
                    "Elastic Hypoelastic Correspondence",
                    "Elastic Partial Volume",
                    "Elastic Plastic",
                    "Elastic Plastic Correspondence",
                    "Elastic Plastic Hardening",
                    "Elastic Plastic Hypoelastic Correspondence",
                    "Isotropic Hardening Correspondence",
                    "Isotropic Hardening Hypoelastic Correspondence",
                    "LCM",
                    "Linear Elastic Correspondence",
                    "Linear LPS Partial Volume",
                    "Multiphysics Elastic",
                    "Pals",
                    "Pressure Dependent Elastic Plastic",
                    "User Correspondence",
                    "Viscoelastic",
                    "Viscoplastic Needleman Correspondence",
                    "Vector Poisson",
                ],
                materialSymmetry: ["Isotropic", "Anisotropic"],
                stabilizationType: [
                    "Bond Based",
                    "State Based",
                    "Sub Horizon",
                    "Global Stiffness",
                ],
                micofam: {
                    RVE: {
                    rve_fvc: 30,
                    rve_radius: 6.6,
                    rve_lgth: 50,
                    rve_dpth: 1,
                    },
                    Mesh: {
                    mesh_fib: 35,
                    mesh_lgth: 35,
                    mesh_dpth: 1,
                    mesh_aa: "on",
                    },
                },
                materialKeys: {
                    name: "name",
                    matType: "Material Model",
                    density: "Density",
                    bulkModulus: "Bulk Modulus",
                    shearModulus: "Shear Modulus",
                    youngsModulus: "Young's Modulus",
                    poissonsRatio: "Poisson's Ratio",
                    tensionSeparation: "Tension Separation",
                    nonLinear: "Non linear",
                    planeStress: "Plane Stress",
                    materialSymmetry: "Material Symmetry",
                    stabilizationType: "Stabilization Type",
                    thickness: "Thickness",
                    hourglassCoefficient: "Hourglass Coefficient",
                    actualHorizon: "Actual Horizon",
                    yieldStress: "Yield Stress",
                    Parameter_0: "C11",
                    Parameter_1: "C12",
                    Parameter_2: "C13",
                    Parameter_3: "C14",
                    Parameter_4: "C15",
                    Parameter_5: "C16",
                    Parameter_6: "C22",
                    Parameter_7: "C23",
                    Parameter_8: "C24",
                    Parameter_9: "C25",
                    Parameter_10: "C26",
                    Parameter_11: "C33",
                    Parameter_12: "C34",
                    Parameter_13: "C35",
                    Parameter_14: "C36",
                    Parameter_15: "C44",
                    Parameter_16: "C45",
                    Parameter_17: "C46",
                    Parameter_18: "C55",
                    Parameter_19: "C56",
                    Parameter_20: "C66",
                    computePartialStress: "Compute Partial Stress",
                    useCollocationNodes: "Use Collocation Nodes",
                    numStateVars: "Number of State Vars",
                    // Thermal
                    specificHeatCapacity: "Specific Heat Capacity",
                    thermalConductivity: "Thermal Conductivity",
                    heatTransferCoefficient: "Heat Transfer Coefficient",
                    applyThermalFlow: "Apply Thermal Flow",
                    applyThermalStrain: "Apply Thermal Strain",
                    applyHeatTransfer: "Apply Heat Transfer",
                    thermalBondBased: "Thermal Bond Based",
                    thermalExpansionCoefficient: "Thermal Expansion Coefficient",
                    environmentalTemperature: "Environmental Temperature",
                    // 3dPrint
                    printBedTemperature: "Print Bed Temperature",
                    printBedThermalConductivity: "Thermal Conductivity Print Bed",
                    volumeFactor: "Volume Factor",
                    volumeLimit: "Volume Limit",
                    surfaceCorrection: "Surface Correction",
                },
            };
        },
        methods: {
            onMultiFilePicked(event) {
                const files = event.target.files;
                const filetype = files[0].type;
                if (files.length <= 0) {
                    return false;
                }

                this.viewStore.modelLoading = true;
                this.uploadfiles(files);

                this.viewStore.modelLoading = false;
            },
            async uploadfiles(files) {
                const formData = new FormData();
                for (var i = 0; i < files.length; i++) {
                    formData.append("files", files[i]);
                }
                let params={model_name: this.modelData.model.modelNameSelected,
                model_folder_name: this.modelData.model.modelFolderName}

                this.$api.post('/uploadfiles', formData, {params})
                .then((response) => {
                    this.$q.notify({
                        message: response.data.message
                    })
                })
                .catch((error) => {
                    this.$q.notify({
                        type: 'negative',
                        message: error.response.data.detail
                    })
                })
            },
            uploadSo() {
                this.$refs.multiSoInput.click();
            },
            uploadProps(id) {
                this.$refs.propsInput.click();
                this.selectedMaterial = id;
            },
            onPropsFilePicked(event) {
                const files = event.target.files;

                const fr = new FileReader();
                fr.onload = (e) => {
                    const input_string = e.target.result;

                    let filtered_string = input_string.match(/\*User([\D\S]*?)\*/gi);
                    let propsArray = filtered_string[0].split(/[\n,]/gi);
                    propsArray = propsArray.slice(0, propsArray.length - 1);

                    if (propsArray[1].match(/\d+/) == propsArray.length - 2) {
                    this.materials[0].properties = [];
                    for (var i = 2; i < propsArray.length; i++) {
                        this.addProp(0);
                        this.materials[0].properties[i - 2].value = propsArray[i].trim();
                    }
                    } else {
                    console.log("Length of Propsarray unexpected");
                    }
                };
                fr.readAsText(files.item(0));

                // console.log(input_string)
                // let filtered_string = input_string.search(/\*User([\D\S]*?)\*/i);
            },
            addMaterial() {
                const len = this.materials.length;
                let newItem = deepCopy(this.materials[len - 1])
                newItem.materialsId = len + 1
                newItem.name = "Material" + (len + 1)
                this.materials.push(newItem);
            },
            removeMaterial(index) {
                this.materials.splice(index, 1);
            },
            addProp(index) {
                const len = this.materials[index].properties.length;
                let newItem = {}
                if (len !=0){
                    newItem = deepCopy(this.materials[index].properties[len - 1])
                }
                newItem.materialsPropId = len + 1
                newItem.name = "Prop_" + (len + 1)

                this.materials[index].properties.push(newItem)
            },
            removeProp(index, subindex) {
                this.materials[index].properties.splice(subindex, 1);
            },
        }
    })
</script>