<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-select class="my-select" :options="distributionTypes" v-model="discretization.distributionType"
      label="Distribution Type" standout dense></q-select>
    <div v-if="store.modelData.model.gcode && discretization.gcode != null">
      <q-toggle class="my-toggle" v-model="discretization.gcode.overwriteMesh" :label=discKeys.gcode.overwriteMesh
        standout dense></q-toggle>
      <q-input class="my-input" v-model="discretization.gcode.dx" :rules="[rules.required, rules.float]"
        :label="discKeys.gcode.dx" standout dense></q-input>
      <q-input class="my-input" v-model="discretization.gcode.dy" :rules="[rules.required, rules.float]"
        :label="discKeys.gcode.dy" standout dense></q-input>
      <q-input class="my-input" v-model="discretization.gcode.width" :rules="[rules.required, rules.float]"
        :label="discKeys.gcode.width" standout dense></q-input>
      <q-input class="my-input" v-model="discretization.gcode.scale" :rules="[rules.required, rules.float]"
        :label="discKeys.gcode.scale" standout dense></q-input>
    </div>
  </div>
</template>

<script>
import { computed, defineComponent, inject } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'DiscretizazionSettings',
  setup() {
    const store = useModelStore();
    const discretization = computed(() => store.modelData.discretization)
    return {
      store,
      discretization,
      rules,
    }
  },
  data() {
    return {
      distributionTypes: [
        'Neighbor based',
        'Node based'
      ],
      discKeys: {
        gcode: {
          overwriteMesh: 'overwriteMesh',
          dx: 'dx',
          dy: 'dy',
          width: 'Width',
          scale: 'Scale'
        }
      }
    }
  }
})
</script>
