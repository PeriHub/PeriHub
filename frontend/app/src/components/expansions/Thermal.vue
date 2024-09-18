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
        <div class="row my-row">
          <div class="row my-row">
            <q-input class="my-input" v-model="thermal.specificHeatCapacity" :rules="[rules.required, rules.float]"
              :label="thermalKeys.specificHeatCapacity" standout dense></q-input>
            <q-input class="my-input" v-model="thermal.thermalConductivity" :rules="[rules.required, rules.float]"
              :label="thermalKeys.thermalConductivity" standout dense></q-input>
            <q-input class="my-input" v-model="thermal.heatTransferCoefficient" :rules="[rules.required, rules.float]"
              :label="thermalKeys.heatTransferCoefficient" standout dense></q-input>
          </div>
          <div class="row my-row">
            <q-toggle class="my-toggle" v-model="thermal.applyThermalFlow" :label="thermalKeys.applyThermalFlow"
              dense></q-toggle>
            <q-toggle class="my-toggle" v-model="thermal.applyThermalStrain" :label="thermalKeys.applyThermalStrain"
              dense></q-toggle>
            <q-toggle class="my-toggle" v-model="thermal.applyHeatTransfer" :label="thermalKeys.applyHeatTransfer"
              dense></q-toggle>
            <q-toggle class="my-toggle" v-model="thermal.thermalBondBased" :label="thermalKeys.thermalBondBased"
              dense></q-toggle>
          </div>
          <div class="row my-row">
            <q-input class="my-input" v-model="thermal.thermalExpansionCoefficient"
              :rules="[rules.required, rules.float]" :label="thermalKeys.thermalExpansionCoefficient" clearable standout
              dense></q-input>
            <q-input class="my-input" v-model="thermal.environmentalTemperature" :rules="[rules.required, rules.float]"
              :label="thermalKeys.environmentalTemperature" clearable standout dense></q-input>
          </div>
          <q-separator></q-separator>
          <h6 class="my-title">Additive</h6>
          <div class="row my-row">
            <q-input class="my-input" v-model="thermal.printBedTemperature" :rules="[rules.required, rules.float]"
              :label="thermalKeys.printBedTemperature" clearable standout dense></q-input>
            <q-input class="my-input" v-model="thermal.printBedThermalConductivity"
              :rules="[rules.required, rules.float]" :label="thermalKeys.printBedThermalConductivity" clearable standout
              dense></q-input>
          </div>
          <div class="row my-row">
            <q-input class="my-input" v-model="thermal.volumeFactor" :rules="[rules.required, rules.float]"
              :label="thermalKeys.volumeFactor" clearable standout dense></q-input>
            <q-input class="my-input" v-model="thermal.volumeLimit" :rules="[rules.required, rules.float]"
              :label="thermalKeys.volumeLimit" clearable standout dense></q-input>
            <q-input class="my-input" v-model="thermal.surfaceCorrection" :rules="[rules.required, rules.float]"
              :label="thermalKeys.surfaceCorrection" clearable standout dense></q-input>
          </div>
          <q-btn flat icon="fas fa-trash-alt" @click="removethermalModel(index)">
            <q-tooltip>
              Remove Thermal Model
            </q-tooltip>
          </q-btn>
        </div>
        <q-separator></q-separator>
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
  created() {
  },
  data() {
    return {
      thermalTypes: ['Simple'],

      thermalKeys: {
        specificHeatCapacity: 'Specific Heat Capacity',
        thermalConductivity: 'Thermal Conductivity',
        heatTransferCoefficient: 'Heat Transfer Coefficient',
        applyThermalFlow: 'Apply Thermal Flow',
        applyThermalStrain: 'Apply Thermal Strain',
        applyHeatTransfer: 'Apply Heat Transfer',
        thermalBondBased: 'Thermal Bond Based',
        thermalExpansionCoefficient: 'Thermal Expansion Coefficient',
        environmentalTemperature: 'Environmental Temperature',
      }
    };
  },
  methods: {
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
