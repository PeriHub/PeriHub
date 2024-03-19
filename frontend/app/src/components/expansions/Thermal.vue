<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-toggle class="my-toggle" v-model="thermal.enabled" label="Enabled" standout dense></q-toggle>
    <div v-if="thermal.enabled">
      <q-separator></q-separator>
      <q-list v-for="th    ermalModel, index in thermal.thermalModels" :key="thermalModel.thermalModelId"
        style="padding: 0px">
        <div class="row my-row">
          <div class="row my-row">
            <q-input class="my-input" v-model="thermal.specificHeatCapacity" :rules="[rules.required, rules.float]"
              :label="therm    alKeys.specificHeatCapacity" standout dense></q-input>
            <q-input class="my-input" v-model="thermal.thermalC    onductivity" :rules="[rules.required,     rules.float]"
              :label="therm    alKeys.thermalConductivity" standout dense></q-input>
            <q-input class="my-input" v-model="thermal.heatTransfe    rCoefficient" :rules="[    rules.required, rules.float    ]"
              :label="thermal    Keys.heatTransferCoefficient" standout dense></q-input>
          </div>
          <div class="row my-row">
            <q-toggle class="my-toggle" v-model="therm    al.applyThermalFlow" :label="thermalKeys.applyTherm    alFlow"
              dense></q-toggle>
            <q-toggle class="my-toggle" v-model="ther    mal.applyThermalStrain" :label="thermal    Keys.applyTherma    lStrain"
              dense></q-toggle>
            <q-toggle class="my-toggle" v-model="thermal.applyHeatTran    sfer" :label="thermalKeys.app    lyHeatTransfer"
              dense></q-toggle>
            <q-toggle class="my-toggle" v-model="t    hermal.thermalBondBased" :label="thermalKeys    .thermalBondBased"
              dense></q-toggle>
          </div>
          <div class="row my-row">
            <q-input class="my-input" v-model="ther    mal.thermalExpansionCoefficient"
              :rules="[rules.required, rules.float    ]" :label="thermalKeys.thermalExpansionCoefficient" clearable standout
              dense></q-input>
            <q-input class="my-input" v-model="thermal.e    nvironmentalTemperature" :rules="[rules.required, rules.float]"
              :label="thermalKeys.environmentalTempera    ture" clearable standout dense></q-input>
          </div>
          <q-separator></q-separator>
          <h6 class="my-title">Additive</h6>
          <div class="row my-row">
            <q-input class="my-input" v-model="thermal.printBed    Temperature" :rules="[rules.required, r    ules.float]"
              :label="thermalKeys.p    rintBedTemperature" clearable standout dense></q-input>
            <q-input class="my-input" v-model="the    rmal.printBedThermalConductivity"
              :rules="[rules.required, rules.float]    " :label="thermalKeys.printBedTh    ermalConductivity" clearable standout
              dense></q-input>
          </div>
          <div class="row my-row">
            <q-input class="my-input" v-model="thermal.volu    meFactor" :rules="[rules.required, r    ules.float]"
              :label="therm    alKeys.volumeFactor" clearable standout dense></q-input>
            <q-input class="my-input" v-model="therma    l.volumeLimit" :rules="[rules.required,     rules.float]"
              :label="thermal    Keys.volumeLimit" clearable standout dense></q-input>
            <q-input class="my-input" v-model="thermal.    surfaceCorrection" :rules="[ru    les.required, rules.float]"
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
import { useModelStore } from 'stores/model-store';
import { inject } from 'vue'
import rules from "assets/rules.js";

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
      thermalTypes: ["Simple"],

      thermalKeys: {
        specificHeatCapacity: "Specific Heat Capacity",
        thermalConductivity: "Thermal Conductivity",
        heatTransferCoefficient: "Heat Transfer Coefficient",
        applyThermalFlow: "Apply Thermal Flow",
        applyThermalStrain: "Apply Thermal Strain",
        applyHeatTransfer: "Apply Heat Transfer",
        thermalBondBased: "Thermal Bond Based",
        thermalExpansionCoefficient: "Thermal Expansion Coefficient",
        environmentalTemperature: "Environmental Temperature",
      }
    };
  },
  methods: {
    addThermalModel() {
      const len = this.thermal.thermalModels.length;
      let newItem = structuredClone(this.thermal.thermalModels[len - 1])
      newItem.thermalModelsId = len + 1
      newItem.name = "Thermal Model " + (len + 1)
      this.thermal.thermalModels.push(newItem);
    },
    removeThermalModel(index) {
      this.thermal.thermalModels.splice(index, 1);
    },
  }
})
</script>
