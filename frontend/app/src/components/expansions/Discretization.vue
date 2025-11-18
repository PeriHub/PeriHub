<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-select class="my-select" :options="distributionTypes" v-model="discretization.distributionType"
      label="Distribution Type" standout dense></q-select>
    <q-list v-for="nodeSet, index in discretization.nodeSets" :key="nodeSet.nodeSetId as PropertyKey"
      style="padding: 0px">
      <div class="row my-row">
        <q-input class="my-input" v-model="nodeSet.file" :rules="[rules.required, rules.name]" label="Nodeset" standout
          dense></q-input>
        <q-btn flat icon="fas fa-trash-alt" @click="removeNodeSet(index)">
          <q-tooltip>
            Remove Nodeset
          </q-tooltip>
        </q-btn>
      </div>
      <q-separator></q-separator>
    </q-list>
    <q-btn flat icon="fas fa-plus" @click="addNodeSet">
      <q-tooltip>
        Add Nodeset
      </q-tooltip>
    </q-btn>
    <div v-if="discretization.discType == 'gcode' && discretization.gcode != null">
      <q-toggle class="my-toggle" v-model="discretization.gcode.overwriteMesh" :label=discKeys.gcode.overwriteMesh
        standout dense></q-toggle>
      <q-input class="my-input" v-model="discretization.gcode.sampling" :rules="[rules.required, rules.float]"
        :label="discKeys.gcode.sampling" standout dense></q-input>
      <q-input class="my-input" v-model="discretization.gcode.width" :rules="[rules.required, rules.float]"
        :label="discKeys.gcode.width" standout dense></q-input>
      <q-input class="my-input" v-model="discretization.gcode.height" :rules="[rules.required, rules.float]"
        :label="discKeys.gcode.height" standout dense></q-input>
      <q-input class="my-input" v-model="discretization.gcode.scale" :rules="[rules.required, rules.float]"
        :label="discKeys.gcode.scale" standout dense></q-input>
      <q-list v-for="block, index in discretization.gcode.blockFunctions" :key="block.id" style="padding: 0px">
        <div class="row my-row">
          <q-input class="my-input" v-model="block.id" :rules="[rules.required, rules.float]" label="id" standout
            dense></q-input>
          <q-input class="my-input" v-model="block.function" :rules="[rules.required, rules.equation]" label="Function"
            standout dense></q-input>
          <q-btn flat icon="fas fa-trash-alt" @click="removeBlockFunction(index)">
            <q-tooltip>
              Remove Block Function
            </q-tooltip>
          </q-btn>
        </div>
        <q-separator></q-separator>
      </q-list>
      <q-btn flat icon="fas fa-plus" @click="addBlockFunction">
        <q-tooltip>
          Add Block Function
        </q-tooltip>
      </q-btn>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, toRaw } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import type { Discretization, BlockFunction, Gcode, NodeSet } from 'src/client';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'DiscretizazionSettings',
  setup() {
    const store = useModelStore();
    const discretization = computed(() => store.modelData.discretization) as unknown as Discretization
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
          sampling: 'Sampling',
          width: 'Width',
          height: 'Height',
          scale: 'Scale'
        }
      }
    }
  },
  methods: {
    addNodeSet() {
      if (!this.discretization.nodeSets) {
        this.discretization.nodeSets = []
      }
      const len = this.discretization.nodeSets.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.discretization.nodeSets[len - 1])) as NodeSet : {} as NodeSet;
      newItem.nodeSetId = len + 1
      this.discretization.nodeSets.push(newItem);
    },
    removeNodeSet(index: number) {
      if (!this.discretization.nodeSets) {
        return
      }
      this.discretization.nodeSets.splice(index, 1);
      this.discretization.nodeSets.forEach((model, i) => {
        model.nodeSetId = i + 1
      })
    },

    addBlockFunction() {
      if (!this.discretization.gcode) {
        this.discretization.gcode = {} as Gcode;
      }
      if (!this.discretization.gcode.blockFunctions) {
        this.discretization.gcode.blockFunctions = []
      }
      const len = this.discretization.gcode.blockFunctions.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.discretization.gcode.blockFunctions[len - 1])) as BlockFunction : {} as BlockFunction;
      newItem.id = len + 1
      this.discretization.gcode.blockFunctions.push(newItem);
    },
    removeBlockFunction(index: number) {
      if (!this.discretization.gcode || !this.discretization.gcode.blockFunctions) {
        return
      }
      this.discretization.gcode.blockFunctions.splice(index, 1);
      this.discretization.gcode.blockFunctions.forEach((model, i) => {
        model.id = i + 1
      })
    },
  }
})
</script>
