<template>
    <div>
            <h6 class="my-title">Compute Parameters</h6>
            <q-list
                v-for="compute, index in computes"
                :key="compute.computesId"
                style="padding: 0px"
            >
                <div class="row my-row">
                    <q-input 
                        class="my-input"
                        v-model="compute.name"
                        :rules="[rules.required, rules.name]"
                        :label="computeKeys.name"
                        outlined
                        dense
                    ></q-input>
                    <q-select 
                        class="my-input"
                        :options="computeClass"
                        v-model="compute.computeClass"
                        :label="computeKeys.computeClass"
                        outlined
                        dense
                    ></q-select>
                    <q-select 
                        class="my-input"
                        :options="variables"
                        v-model="compute.variable"
                        :label="computeKeys.variable"
                        outlined
                        dense
                    ></q-select>
                </div>
                <div class="row my-row" v-show="compute.computeClass=='Block_Data'"> 
                    <q-select 
                        class="my-input"
                        :options="calculationType"
                        v-model="compute.calculationType"
                        :label="computeKeys.calculationType"
                        outlined
                        dense
                    ></q-select>
                    <q-select 
                        class="my-input"
                        :options="blocks"
                        item-text="name"
                        v-model="compute.blockName"
                        :label="computeKeys.blockName"
                        outlined
                        dense
                    ></q-select>
                </div>
                <div class="row my-row" v-show="compute.computeClass=='Nearest_Point_Data'"> 
                    <q-input 
                        class="my-input"
                        v-model="compute.x"
                        :rules="[rules.required, rules.name]"
                        :label="computeKeys.x"
                        clearable
                        outlined
                        dense
                    ></q-input>
                    <q-input 
                        class="my-input"
                        v-model="compute.y"
                        :rules="[rules.required, rules.name]"
                        :label="computeKeys.y"
                        clearable
                        outlined
                        dense
                    ></q-input>
                    <q-input 
                        class="my-input"
                        v-model="compute.z"
                        :rules="[rules.required, rules.name]"
                        :label="computeKeys.z"
                        clearable
                        outlined
                        dense
                    ></q-input>
                </div>
                <q-btn flat icon="fas fa-trash-alt" @click="removeCompute(index)">
                    <q-tooltip>
                        Remove Compute
                    </q-tooltip>
                </q-btn>
                <q-separator></q-separator>
            </q-list>
            
            <q-btn flat icon="fas fa-plus" @click="addCompute">
                <q-tooltip>
                    Add Compute
                </q-tooltip>
            </q-btn>
            <q-separator></q-separator>
            <h6 class="my-title">Compute Parameters</h6>
            <q-list
                v-for="output, index in outputs"
                :key="output.outputsId"
                style="padding: 0px"
            >
                <div v-bind:style="(output.outputsId % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
                    <h4 class="my-title">Output {{output.outputsId}}</h4>
                    <div class="row my-row">
                        <q-input 
                            class="my-input"
                            v-model="output.name"
                            :rules="[rules.required, rules.name]"
                            :label="outputKeys.name"
                            outlined
                            dense
                        ></q-input>
                        <q-btn flat icon="fas fa-trash-alt" @click="removeOutput(index)">
                            <q-tooltip>
                                Remove Compute
                            </q-tooltip>
                        </q-btn>
                    </div>
                    <div class="row my-row">
                        <div v-for="(value, index) in Object.entries(outputKeys)" :key="index">
                            <q-toggle
                                v-if="value[0]!='name' & value[0]!='Frequency' & value[0]!='InitStep'"
                                class="my-toggle"
                                v-model="output[value[0]]"
                                :label="outputKeys[value[0]]"
                                outlined
                                dense
                            ></q-toggle>
                        </div>
                        <q-input 
                            class="my-input"
                            v-model="output.Frequency"
                            :rules="[rules.required, rules.name]"
                            :label="outputKeys.Frequency"
                            outlined
                            dense
                        ></q-input>
                        <q-input 
                            class="my-input"
                            v-model="output.InitStep"
                            :rules="[rules.required, rules.name]"
                            :label="outputKeys.InitStep"
                            outlined
                            dense
                        ></q-input>
                    </div>
                </div> 
                <q-separator></q-separator>
            </q-list>
            <q-btn flat icon="fas fa-plus" @click="addOutput">
                <q-tooltip>
                    Add Output
                </q-tooltip>
            </q-btn>
        </div>
</template>
  
<script>
    import { computed, defineComponent } from 'vue'
    import { useModelStore } from 'stores/model-store';
    import { inject } from 'vue'
    import rules from "assets/rules.js";
    import { deepCopy } from '../../utils/functions.js'
  
    export default defineComponent({
        name: 'OutputSettings',
        setup() {
            const store = useModelStore();
            const blocks = computed(() => store.modelData.blocks)
            const computes = computed(() => store.modelData.computes)
            const outputs = computed(() => store.modelData.outputs)
            const bus = inject('bus')
            return {
                store,
                blocks,
                computes,
                outputs,
                rules,
                bus
            }
        },
        created() {
        },
        data() {
            return {
                computeClass: ["Block_Data", "Nearest_Point_Data"],
                calculationType: ["Sum", "Maximum", "Minimum"],
                variables: ["Force", "Displacement", "Damage", "Temperature"],
                computeKeys: {
                    computeClass: "Compute Class",
                    name: "Output Label",
                    variable: "Variable",
                    calculationType: "Calculation Type",
                    blockName: "Block",
                    xValue: "X",
                    yValue: "Y",
                    zValue: "Z",
                },
                outputKeys: {
                    name: "Output Filename",
                    Element_Id: "Element_Id",
                    Block_Id: "Block_Id",
                    Horizon: "Horizon",
                    Volume: "Volume",
                    Point_Time: "Point_Time",
                    Node_Type: "Node_Type",
                    Model_Coordinates: "Model_Coordinates",
                    Local_Angles: "Local_Angles",
                    Orientations: "Orientations",
                    Coordinates: "Coordinates",
                    Displacement: "Displacement",
                    Velocity: "Velocity",
                    Acceleration: "Acceleration",
                    Temperature: "Temperature",
                    Concentration: "Concentration",
                    Temperature_Change: "Temperature_Change",
                    Flux_Divergence: "Flux_Divergence",
                    Concentration_Flux_Divergence: "Concentration_Flux_Divergence",
                    Force_Density: "Force_Density",
                    Contact_Force_Density: "Contact_Force_Density",
                    External_Force_Density: "External_Force_Density",
                    Damage_Model_Data: "Damage_Model_Data",
                    Damage: "Damage",
                    Detached_Nodes: "Detached_Nodes",
                    Bond_Damage_Diff: "Bond_Damage_Diff",
                    Specific_Volume: "Specific_Volume",
                    Proc_Num: "Proc_Num",
                    Hourglass_Force_Density: "Hourglass_Force_Density",
                    Deformation_Gradient: "Deformation_Gradient",
                    Left_Stretch_Tensor: "Left_Stretch_Tensor",
                    Rotation_Tensor: "Rotation_Tensor",
                    Shape_Tensor_Inverse: "Shape_Tensor_Inverse",
                    Unrotated_Cauchy_Stress: "Unrotated_Cauchy_Stress",
                    Unrotated_Rate_Of_Deformation: "Unrotated_Rate_Of_Deformation",
                    Unrotated_Plastic_Cauchy_Stress: "Unrotated_Plastic_Cauchy_Stress",
                    Cauchy_Stress: "Cauchy_Stress",
                    Partial_Stress: "Partial_Stress",
                    Hourglass_Stiffness: "Hourglass_Stiffness",
                    Von_Mises_Stress: "Von_Mises_Stress",
                    Equivalent_Plastic_Strain: "Equivalent_Plastic_Strain",
                    Unrotated_Strain: "Unrotated_Strain",
                    Weighted_Volume: "Weighted_Volume",
                    Dilatation: "Dilatation",
                    Number_Of_Neighbors: "Number_Of_Neighbors",
                    Force: "Force",
                    Velocity_Gradient: "Velocity_Gradient",
                    PiolaStressTimesInvShapeTensor: "PiolaStressTimesInvShapeTensor",
                    Frequency: "Output Frequency",
                    InitStep: "Initial Output Step",
                },
            };
        },
        methods: {
            addCompute() {
                const len = this.computes.length;
                let newItem = deepCopy(this.computes[len - 1])
                newItem.computesId = len + 1
                newItem.name = "Compute" + (len + 1)
                this.computes.push(newItem);
            },
            removeCompute(index) {
                this.computes.splice(index, 1);
            },
            addOutput() {
                const len = this.outputs.length;
                this.outputs.push({
                    outputsId: len + 1,
                    name: "Output" + (len + 1),

                    Element_Id: false,
                    Block_Id: false,
                    Horizon: false,
                    Volume: false,
                    Point_Time: false,
                    Node_Type: false,
                    Model_Coordinates: false,
                    Local_Angles: false,
                    Orientations: false,
                    Coordinates: false,
                    Displacement: false,
                    Velocity: false,
                    Acceleration: false,
                    Temperature: false,
                    Concentration: false,
                    Temperature_Change: false,
                    Flux_Divergence: false,
                    Concentration_Flux_Divergence: false,
                    Force_Density: false,
                    Contact_Force_Density: false,
                    External_Force_Density: false,
                    Damage_Model_Data: false,
                    Damage: false,
                    Detached_Nodes: false,
                    Bond_Damage_Diff: false,
                    Specific_Volume: false,
                    Proc_Num: false,
                    Hourglass_Force_Density: false,
                    Deformation_Gradient: false,
                    Left_Stretch_Tensor: false,
                    Rotation_Tensor: false,
                    Shape_Tensor_Inverse: false,
                    Unrotated_Cauchy_Stress: false,
                    Unrotated_Rate_Of_Deformation: false,
                    Unrotated_Plastic_Cauchy_Stress: false,
                    Cauchy_Stress: false,
                    Partial_Stress: false,
                    Hourglass_Stiffness: false,
                    Von_Mises_Stress: false,
                    Equivalent_Plastic_Strain: false,
                    Unrotated_Strain: false,
                    Weighted_Volume: false,
                    Dilatation: false,
                    Number_Of_Neighbors: false,
                    Force: false,

                    Velocity_Gradient: false,
                    PiolaStressTimesInvShapeTensor: false,

                    Write_After_Damage: false,
                    InitStep: 0,
                });
            },
            removeOutput(index) {
            this.outputs.splice(index, 1);
            },
        }
    })
</script>
<style>
.my-title {
    margin-top: 10px;
    margin-bottom: 0px;
    margin-left: 10px;
}
.my-row {
    min-height: 50px;
}
.my-input {
    margin-left: 10px;
}
.my-toggle {
    height: 40px;
    margin: 10px;
}
</style>