<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-list v-for="block in blocks" :key="block.blocksId" style="padding: 0px">
      <div class="row my-row">
        <q-input class="my-input" v-model="block.name" :rules="[rules.required, rules.name]" :label="blockKeys.name"
          standout dense></q-input>
        <q-select class="my-select" :options="materials" option-label="name" option-value="name" emit-value
          v-model="block.material" :label="blockKeys.material" standout dense></q-select>
        <q-select class="my-select" :options="damages" option-label="name" option-value="name" emit-value
          v-model="block.damageModel" :label="blockKeys.damageModel" clearable standout dense></q-select>
        <q-select v-if="additive.enabled" class="my-select" :options="additive.additiveModels" option-label="name"
          option-value="name" emit-value v-model="block.additiveModel" :label="blockKeys.additiveModel" clearable
          standout dense></q-select>
        <q-input class="my-input" v-model="block.density" :rules="[rules.required, rules.posFloat]"
          :label="blockKeys.density" standout dense></q-input>
        <q-toggle class="my-toggle" v-model="block.show" @update:model-value="bus.emit('filterPointData')" label="Show"
          standout dense></q-toggle>
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

<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'stores/model-store';
import { inject } from 'vue'
import rules from "assets/rules.js";

export default defineComponent({
  name: 'BlocksSettings',
  setup() {
    const store = useModelStore();
    const model = computed(() => store.modelData.model)
    const materials = computed(() => store.modelData.materials)
    const damages = computed(() => store.modelData.damages)
    const additive = computed(() => store.modelData.additive)
    const blocks = computed(() => store.modelData.blocks)
    const job = computed(() => store.modelData.job)
    const bus = inject('bus')
    return {
      store,
      model,
      materials,
      damages,
      additive,
      blocks,
      job,
      rules,
      bus
    }
  },
  created() {
  },
  data() {
    return {
      blockKeys: {
        name: "Block Names",
        material: "Material",
        damageModel: "Damage Model",
        additiveModel: "Additive Model",
        horizon: "Horizon",
        density: "Density",
      },
    };
  },
  methods: {
    addBlock() {
      const len = this.blocks.length;
      let newItem = structuredClone(this.blocks[len - 1])
      newItem.blocksId = len + 1
      newItem.name = "block_" + (len + 1)
      this.blocks.push(newItem);
    },
    removeBlock(index) {
      console.log(index)
      this.blocks.splice(index, 1);
    },
  }
})
</script>
