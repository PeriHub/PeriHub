<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-toggle class="my-toggle" v-model="thermal.enabled" label="Enabled" standout dense></q-toggle>
    <div v-if="thermal.enabled">
      <q-separator></q-separator>
      <q-list v-for="thermalModel, index in thermal.thermalModels" :key="thermalModel.thermalModelId"
        style="padding: 0px">
        <div
          v-bind:style="(thermalModel.thermalModelsId % 2 == 0) ? 'background-color: rgba(190, 190, 190, 0.1);' : 'background-color: rgba(255, 255, 255, 0.0);'">
          <h4 class="my-title">Thermal {{ thermalModel.thermalModelsId }}</h4>
          <div class="row my-row">
            <q-input class="my-input" v-model="thermalModel.name" :rules="[rules.required, rules.name]"
              :label="thermalKeys.name" standout dense></q-input>
            <q-btn flat icon="fas fa-trash-alt" @click="removethermalModel(index)">
              <q-tooltip>
                Remove Thermal Model
              </q-tooltip>
            </q-btn>
          </div>
          <div class="row my-row">
            <div class="row my-row">
              <q-select class="my-input" v-model="thermalModel.thermalModel" use-input use-chips multiple
                input-debounce="0" :options="thermalModelNames" @filter="filterFn"
                style="width: 250px; margin-bottom:20px;" :label="thermalKeys.thermalType" standout dense></q-select>
              <q-select class="my-input" :options="thermalTypes" v-model="thermalKeys.thermalType"
                :label="thermalKeys.thermalType" standout dense></q-select>
            </div>
            <div class="row my-row">
              <q-input class="my-input" v-model="thermalModel.thermalConductivity"
                :rules="[rules.required, rules.float]" :label="thermalKeys.thermalConductivity" standout
                dense></q-input>
              <q-input class="my-input" v-model="thermalModel.heatTransferCoefficient"
                :rules="[rules.required, rules.float]" :label="thermalKeys.heatTransferCoefficient" standout
                dense></q-input>
            </div>
            <div class="row my-row">
              <q-input class="my-input" v-model="thermalModel.thermalExpansionCoefficient"
                :rules="[rules.required, rules.float]" :label="thermalKeys.thermalExpansionCoefficient" clearable
                standout dense></q-input>
              <q-input class="my-input" v-model="thermalModel.environmentalTemperature"
                :rules="[rules.required, rules.float]" :label="thermalKeys.environmentalTemperature" clearable standout
                dense></q-input>
            </div>
            <q-separator></q-separator>
            <h6 class="my-title">Additive</h6>
            <div class="row my-row">
              <q-input class="my-input" v-model="thermalModel.printBedTemperature"
                :rules="[rules.required, rules.float]" :label="thermalKeys.printBedTemperature" clearable standout
                dense></q-input>
              <q-input class="my-input" v-model="thermalModel.thermalConductivityPrintBed"
                :rules="[rules.required, rules.float]" :label="thermalKeys.thermalConductivityPrintBed" clearable
                standout dense></q-input>
              <q-input class="my-input" v-model="thermalModel.requiredSpecificVolume"
                :rules="[rules.required, rules.float]" :label="thermalKeys.requiredSpecificVolume" clearable standout
                dense></q-input>
            </div>
            <q-separator></q-separator>
            <h6 class="my-title">HETVAL</h6>
            <div class="row my-row">
              <q-input class="my-input" v-model="thermalModel.file" :label="thermalKeys.file" clearable standout
                dense></q-input>
              <q-input class="my-input" v-model="thermalModel.numStateVars" :rules="[rules.required, rules.float]"
                :label="thermalKeys.numStateVars" clearable standout dense></q-input>
              <q-input class="my-input" v-model="thermalModel.predefinedFieldNames"
                :label="thermalKeys.predefinedFieldNames" clearable standout dense></q-input>
            </div>
          </div>
          <q-separator></q-separator>
        </div>
      </q-list>

      <q-btn flat icon="fas fa-plus" @click="addThermalModel">
        <q-tooltip>
          Add Thermal Model
        </q-tooltip>
      </q-btn>
    </div>
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import { inject } from 'vue'
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'ThermalSettings',
  setup() {
    const store = useModelStore();
    const thermal = computed(() => store.modelData.thermal)
    const bus = inject('bus')
    return {
      store,
      thermal,
      rules,
      bus
    }
  },
  data() {
    return {
      thermalModelNames: ['Thermal Flow', 'Heat Transfer', 'Thermal Expansion'],
      thermalTypes: ['Bond based'],
      thermalKeys: {
        name: 'Name',
        thermalType: 'Type',
        heatTransferCoefficient: 'Heat Transfer Coefficient',
        environmentalTemperature: 'Environmental Temperature',
        requiredSpecificVolume: 'Required Specific Volume',
        thermalConductivity: 'Thermal Conductivity',
        thermalExpansionCoefficient: 'Thermal Expansion Coefficient',
        thermalConductivityPrintBed: 'Thermal Conductivity Print Bed',
        printBedTemperature: 'Print Bed Temperature',
        file: 'File',
        numStateVars: 'Number of State Variables',
        predefinedFieldNames: 'Predefined Field Names',
      },
      filterOptions: this.thermalModelNames,
    };
  },
  methods: {
    filterFn(val, update) {
      update(() => {
        if (val === '') {
          this.filterOptions = this.thermalModelNames
        }
        else {
          const needle = val.toLowerCase()
          this.filterOptions = this.thermalModelNames.filter(
            v => v.toLowerCase().indexOf(needle) > -1
          )
        }
      })
    },
    addThermalModel() {
      const len = this.thermal.thermalModels.length;
      let newItem = structuredClone(this.thermal.thermalModels[len - 1])
      newItem.thermalModelsId = len + 1
      newItem.name = 'Thermal Model ' + (len + 1)
      this.thermal.thermalModels.push(newItem);
    },
    removeThermalModel(index) {
      this.thermal.thermalModels.splice(index, 1);
    },
  }
})
</script>
