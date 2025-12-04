<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-list v-for="block in blocks" :key="block.blocksId as PropertyKey" style="padding: 0px">
      <div class="row my-row">
        <q-input class="small-input" v-model="block.name" :rules="[rules.required, rules.name]" :label="blockKeys.name"
          standout dense></q-input>
        <q-select class="my-select" :options="materials" option-label="name" option-value="name" emit-value
          v-model="block.material" :label="blockKeys.material" clearable standout dense></q-select>
        <q-select class="my-select" :options="damages" option-label="name" option-value="name" emit-value
          v-model="block.damageModel" :label="blockKeys.damageModel" clearable standout dense></q-select>
        <q-select v-if="thermal.enabled" class="my-select" :options="thermalModels" option-label="name"
          option-value="name" emit-value v-model="block.thermalModel" :label="blockKeys.thermalModel" clearable standout
          dense></q-select>
        <q-select v-if="additive.enabled" class="my-select" :options="additiveModels" option-label="name"
          option-value="name" emit-value v-model="block.additiveModel" :label="blockKeys.additiveModel" clearable
          standout dense></q-select>
        <q-input class="small-input" v-model="block.density" :rules="[rules.required, rules.posFloat]"
          :label="blockKeys.density" standout dense></q-input>
        <q-input class="small-input" v-model="block.specificHeatCapacity" :rules="[rules.posFloat]"
          :label="blockKeys.specificHeatCapacity" standout dense></q-input>
        <q-input class="small-input" v-if="model.ownModel" v-model="block.horizon"
          :rules="[rules.required, rules.posFloat]" :label="blockKeys.horizon" standout dense></q-input>
        <q-toggle class="my-toggle" v-model="block.show" @update:model-value="showBlock()"
          :label="blockKeys.show" standout dense></q-toggle>
        <q-btn v-if="model.ownModel" flat icon="fas fa-trash-alt" @click="removeBlock(block.blocksId - 1)">
          <q-tooltip>
            Remove Block
          </q-tooltip>
        </q-btn>
      </div>
      <q-separator></q-separator>
    </q-list>

    <q-btn v-if="model.ownModel" flat icon="fas fa-plus" @click="addBlock">
      <q-tooltip>
        Add Block
      </q-tooltip>
    </q-btn>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, toRaw } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import type { Block, Thermal,ThermalModel, Additive, Damage, AdditiveModel } from 'src/client';
import rules from 'assets/rules';

export default defineComponent({
  name: 'BlocksSettings',
  setup() {
    const store = useModelStore();
    const model = computed(() => store.modelData.model)
    const materials = computed(() => store.modelData.materials)
    const damages = computed(() => store.modelData.damages) as unknown as Damage[]
    const thermal = computed(() => store.modelData.thermal) as unknown as Thermal
    const thermalModels = computed(() => thermal.thermalModels) as unknown as ThermalModel[]
    const additive = computed(() => store.modelData.additive) as unknown as Additive
    const additiveModels = computed(() => additive.additiveModels) as unknown as AdditiveModel[]
    const blocks = computed(() => store.modelData.blocks)
    const job = computed(() => store.modelData.job)
    return {
      store,
      model,
      materials,
      damages,
      thermal,
      thermalModels,
      additive,
      additiveModels,
      blocks,
      job,
      rules
    }
  },
  data() {
    return {
      blockKeys: {
        name: 'Block Names',
        material: 'Material',
        damageModel: 'Damage Model',
        thermalModel: 'Thermal Model',
        additiveModel: 'Additive Model',
        horizon: 'Horizon',
        density: 'Density',
        specificHeatCapacity: 'Specific Heat Capacity',
        show: 'Show',
      },
    };
  },
  methods: {
    showBlock() {
      this.$bus.emit('filterPointData')
    },
    addBlock() {
      const len = this.blocks.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.blocks[len - 1])) as Block : {} as Block;
      newItem.blocksId = len + 1
      newItem.name = 'block_' + (len + 1)
      this.blocks.push(newItem);
    },
    removeBlock(index: number) {
      console.log(index)
      this.blocks.splice(index, 1);
      this.blocks.forEach((block, i) => {
        block.blocksId = i + 1
      })
    },
  }
})
</script>
<style>
.small-input {
  width: 100px;
  margin-left: 10px;
}
</style>
