<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <h6 class="my-title">Compute Parameters (Global Variables)</h6>
    <q-list v-for="compute, index in computes" :key="compute.computesId" style="padding: 0px">
      <div class="row my-row">
        <q-input class="my-input" v-model="compute.name" :rules="[rules.required, rules.name]" :label="computeKeys.name"
          standout dense></q-input>
        <q-select class="my-select" :options="computeClass" v-model="compute.computeClass"
          :label="computeKeys.computeClass" standout dense></q-select>
        <q-select class="my-select" :options="variables" v-model="compute.variable" :label="computeKeys.variable"
          standout dense></q-select>
      </div>
      <div class="row my-row" v-show="compute.computeClass == 'Block_Data'">
        <q-select class="my-select" :options="calculationType" v-model="compute.calculationType"
          :label="computeKeys.calculationType" standout dense></q-select>
        <q-select class="my-select" :options="blocks" option-label="name" option-value="name" emit-value
          v-model="compute.blockName" :label="computeKeys.blockName" standout dense></q-select>
      </div>
      <div class="row my-row" v-show="compute.computeClass == 'Node_Set_Data'">
        <q-select class="my-select" :options="calculationType" v-model="compute.calculationType"
          :label="computeKeys.calculationType" standout dense></q-select>
        <q-select class="my-select" :options="nodeSets" option-label="nodeSetId" option-value="nodeSetId" emit-value
          v-model="compute.nodeSetId" :label="computeKeys.nodeSetId" standout dense></q-select>
      </div>
      <div class="row my-row" v-show="compute.computeClass == 'Nearest_Point_Data'">
        <q-input class="my-input" v-model="compute.xValue" :rules="[rules.required, rules.name]"
          :label="computeKeys.xValue" clearable standout dense></q-input>
        <q-input class="my-input" v-model="compute.yValue" :rules="[rules.required, rules.name]"
          :label="computeKeys.yValue" clearable standout dense></q-input>
        <q-input class="my-input" v-model="compute.zValue" :rules="[rules.required, rules.name]"
          :label="computeKeys.zValue" clearable standout dense></q-input>
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
    <q-list v-for="output, index in outputs" :key="output.outputsId" style="padding: 0px">
      <div
        v-bind:style="(output.outputsId % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
        <h4 class="my-title">Output {{ output.outputsId }}</h4>
        <div class="row my-row">
          <q-input class="my-input" v-model="output.name" :rules="[rules.required, rules.name]" :label="outputKeys.name"
            standout dense></q-input>
          <q-btn flat icon="fas fa-trash-alt" @click="removeOutput(index)">
            <q-tooltip>
              Remove Compute
            </q-tooltip>
          </q-btn>
        </div>
        <div class="row my-row">
          <q-select v-if="output.selectedFileType == 'Exodus'" class="my-input" v-model="output.selectedOutputs"
            use-input use-chips multiple input-debounce="0" :options="filterOptions" @filter="filterFn"
            style="width: 250px; margin-bottom:20px;" standout dense></q-select>
          <q-select v-if="output.selectedFileType == 'CSV'" class="my-input" v-model="output.selectedOutputs" use-input
            use-chips multiple input-debounce="0" :options="filterOptionsCsv" @filter="filterFnCsv"
            style="width: 250px; margin-bottom:20px;" standout dense></q-select>
          <q-select class="my-input" v-model="output.selectedFileType" :options="fileTypes" input-debounce="0"
            @update:model-value="output.selectedOutputs = []" style="width: 250px; margin-bottom:20px;" standout
            dense></q-select>
          <q-toggle class="my-toggle" v-model="output.useOutputFrequency" label="Use Output Frequency" standout
            dense></q-toggle>
          <q-input v-if="output.useOutputFrequency" class="my-input" v-model="output.Frequency" :rules="[rules.int]"
            label="Output Frequency" standout dense></q-input>
          <q-input v-if="!output.useOutputFrequency" class="my-input" v-model="output.numberOfOutputSteps"
            :rules="[rules.int]" label="Number of Outputs" standout dense></q-input>
          <q-input class="my-input" v-model="output.InitStep" :rules="[rules.required, rules.name]"
            label="Initial Output Step" standout dense></q-input>
          <q-toggle class="my-toggle" v-model="output.Write_After_Damage" label="Write After Damage" standout
            dense></q-toggle>
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
import { useModelStore } from 'src/stores/model-store';
import { inject } from 'vue'
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'OutputSettings',
  setup() {
    const store = useModelStore();
    const blocks = computed(() => store.modelData.blocks)
    const nodeSets = computed(() => store.modelData.discretization.nodeSets)
    const computes = computed(() => store.modelData.computes)
    const outputs = computed(() => store.modelData.outputs)
    const job = computed(() => store.modelData.job)
    const bus = inject('bus')
    return {
      store,
      blocks,
      nodeSets,
      computes,
      outputs,
      job,
      rules,
      bus
    }
  },
  created() {
    this.bus.on('addStateVarsToOutput', (numStateVars) => {
      this.addStateVarsToOutput(numStateVars)
    })
  },
  data() {
    return {
      fileTypes: ['Exodus', 'CSV'],
      computeClass: ['Block_Data', 'Node_Set_Data', 'Nearest_Point_Data'],
      calculationType: ['Sum', 'Maximum', 'Minimum'],
      variables: ['Forces', 'Displacements', 'Damage', 'Temperature'],
      // variables: ['Force', 'Displacement', 'Damage', 'Temperature'],
      computeKeys: {
        computeClass: 'Compute Class',
        name: 'Output Label',
        variable: 'Variable',
        calculationType: 'Calculation Type',
        blockName: 'Block',
        xValue: 'X',
        yValue: 'Y',
        zValue: 'Z',
      },

      outputKeys: [
        'Displacements',
        'Damage',
        'Forces',
        'Number of Neighbors',
        'Number of Filtered Neighbors',
        'Activation_Time',
        'Temperature',
        'Heat Flow',
        'Active',
        'Specific Volume',
        'Strain',
        'Cauchy Stress',
        'von Mises Stress',
        'Angles',
        'Orientations',
        'Contact Nodes'
      ],
      // outputKeys: [
      //   'Element_Id',
      //   'Block_Id',
      //   'Horizon',
      //   'Volume',
      //   'Point_Time',
      //   'Node_Type',
      //   'Model_Coordinates',
      //   'Local_Angles',
      //   'Orientations',
      //   'Coordinates',
      //   'Displacement',
      //   'Velocity',
      //   'Acceleration',
      //   'Temperature',
      //   'Concentration',
      //   'Temperature_Change',
      //   'Flux_Divergence',
      //   'Concentration_Flux_Divergence',
      //   'Force_Density',
      //   'Contact_Force_Density',
      //   'External_Force_Density',
      //   'Damage_Model_Data',
      //   'Damage',
      //   'Detached_Nodes',
      //   'Bond_Damage_Diff',
      //   'Specific_Volume',
      //   'Proc_Num',
      //   'Hourglass_Force_Density',
      //   'Deformation_Gradient',
      //   'Left_Stretch_Tensor',
      //   'Rotation_Tensor',
      //   'Shape_Tensor_Inverse',
      //   'Unrotated_Cauchy_Stress',
      //   'Unrotated_Rate_Of_Deformation',
      //   'Unrotated_Plastic_Cauchy_Stress',
      //   'Cauchy_Stress',
      //   'Partial_Stress',
      //   'Hourglass_Stiffness',
      //   'Von_Mises_Stress',
      //   'Equivalent_Plastic_Strain',
      //   'Unrotated_Strain',
      //   'Weighted_Volume',
      //   'Dilatation',
      //   'Number_Of_Neighbors',
      //   'Force',
      //   'Velocity_Gradient',
      //   'PiolaStressTimesInvShapeTensor',
      // ],
      filterOptions: this.outputKeys,
      filterOptionsCsv: this.outputKeys,
    };
  },
  methods: {
    filterFn(val, update) {
      update(() => {
        if (val === '') {
          this.filterOptions = this.outputKeys
        }
        else {
          const needle = val.toLowerCase()
          this.filterOptions = this.outputKeys.filter(
            v => v.toLowerCase().indexOf(needle) > -1
          )
        }
      })
    },
    filterFnCsv(val, update) {
      update(() => {
        let outputKeys = []
        for (var i = 0; i < this.computes.length; i++) {
          outputKeys.push(this.computes[i].name)
        }
        if (val === '') {
          this.filterOptionsCsv = outputKeys
        }
        else {
          const needle = val.toLowerCase()
          this.filterOptionsCsv = outputKeys.filter(
            v => v.toLowerCase().indexOf(needle) > -1
          )
        }
      })
    },
    addStateVarsToOutput(numStateVars) {
      for (var i = 1; i <= numStateVars; i++) {
        var name = 'State_Parameter_Field_' + i.toString()
        if (!this.outputKeys.includes(name)) {
          this.outputKeys.push('State_Parameter_Field_' + i.toString())
        }
      }
    },
    addCompute() {
      if (!this.computes) {
        this.computes = []
      }
      const len = this.computes.length;
      let newItem = {}
      if (len != 0) {
        newItem = structuredClone(this.computes[len - 1])
      } else {
        newItem = {
          'id': 1,
          'computeClass': 'Block_Data',
          'name': 'External_Force',
          'variable': 'Forces',
          'calculationType': 'Sum',
          'blockName': this.blocks[0].name,
          'nodeSetId': 1
        }
      }
      newItem.computesId = len + 1
      newItem.name = 'Compute' + (len + 1)
      this.computes.push(newItem);
    },
    removeCompute(index) {
      this.computes.splice(index, 1);
    },
    addOutput() {
      const len = this.outputs.length;
      this.outputs.push({
        outputsId: len + 1,
        name: 'Output' + (len + 1),
        selectedOutputs: [],

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
