<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-list v-for="boundaryCondition, index in boundaryConditions.conditions"
      :key="boundaryCondition.conditionsId as PropertyKey" style="padding: 0px">
      <div class="row my-row">
        <q-input class="my-input" v-model="boundaryCondition.name" :rules="[rules.required, rules.name]"
          :label="boundaryKeys.name" standout dense></q-input>
        <q-select class="my-select" :options="boundarytype" v-model="boundaryCondition.boundarytype"
          :label="boundaryKeys.boundarytype" standout dense></q-select>
        <q-select v-if="discretization.nodeSets && discretization.nodeSets.length > 0" class="my-select"
          :options="discretization.nodeSets" option-label="nodeSetId" option-value="nodeSetId" emit-value
          v-model="boundaryCondition.nodeSet" :label="boundaryKeys.nodeSet" standout dense
          style="width: 100px"></q-select>
        <q-select v-show="!model.ownModel" class="my-select" :options="blocks" option-label="blocksId"
          option-value="blocksId" emit-value v-model="boundaryCondition.blockId" :label="boundaryKeys.blockId" standout
          dense style="width: 100px"></q-select>
        <q-select v-if="solvers.length > 1" class="my-select" :options="solvers" use-chips multiple
          option-label="stepId" option-value="stepId" emit-value v-model="boundaryCondition.stepId"
          :label="boundaryKeys.stepId" standout dense style="width: 100px"></q-select>
      </div>
      <div class="row my-row">
        <q-select class="my-select" :options="boundaryVariables" v-model="boundaryCondition.variable"
          :label="boundaryKeys.variable" standout dense></q-select>
        <q-select class="my-select" :options="coordinate" v-model="boundaryCondition.coordinate"
          :label="boundaryKeys.coordinate" standout dense style="width: 120px"></q-select>
        <q-input class=" my-input" v-model="boundaryCondition.value" :rules="[rules.required]"
          :label="boundaryKeys.value" standout dense></q-input>
        <q-btn flat icon="fas fa-trash-alt" @click="removeCondition(index)">
          <q-tooltip>
            Remove Condition
          </q-tooltip>
        </q-btn>
      </div>
      <q-separator></q-separator>
    </q-list>

    <q-btn flat icon="fas fa-plus" @click="addCondition">
      <q-tooltip>
        Add Condition
      </q-tooltip>
    </q-btn>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, toRaw } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import type { BoundaryCondition, Discretization } from 'src/client';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'BoundaryConditionsSettings',
  setup() {
    const store = useModelStore();
    const model = computed(() => store.modelData.model)
    const blocks = computed(() => store.modelData.blocks)
    const solvers = computed(() => store.modelData.solvers)
    const boundaryConditions = computed(() => store.modelData.boundaryConditions)
    const discretization = computed(() => store.modelData.discretization) as unknown as Discretization
    return {
      store,
      model,
      blocks,
      solvers,
      boundaryConditions,
      discretization,
      rules
    }
  },
  created() {
    this.$bus.on('addCondition', () => {
      this.addCondition()
    })
  },
  data() {
    return {
      boundarytype: [
        'Dirichlet',
        'Initial',
      ],
      boundaryVariables: [
        'Displacements',
        'Force Densities',
        'Forces',
        'Temperature',
        'Damage',
        'Velocity'
      ],
      coordinate: ['x', 'y', 'z'],
      boundaryKeys: {
        name: 'name',
        nodeSet: 'Node Set',
        boundarytype: 'Type',
        variable: 'Variable',
        blockId: 'Block Id',
        stepId: 'Step Id',
        coordinate: 'Coordinate',
        value: 'Value',
      },
    };
  },
  methods: {
    addCondition() {
      if (!this.boundaryConditions.conditions) {
        this.boundaryConditions.conditions = []
      }
      const len = this.boundaryConditions.conditions.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.boundaryConditions.conditions[len - 1])) as BoundaryCondition : {} as BoundaryCondition;
      newItem.conditionsId = len + 1
      newItem.name = 'BC_' + (len + 1)
      newItem.blockId = len + 1
      this.boundaryConditions.conditions.push(newItem);
    },
    removeCondition(index: number) {
      this.boundaryConditions.conditions.splice(index, 1);
      // this.boundaryConditions.nodeSets.splice(index, 1);
      this.boundaryConditions.conditions.forEach((condition, i) => {
        condition.conditionsId = i + 1
      })
    },
  }
})
</script>
