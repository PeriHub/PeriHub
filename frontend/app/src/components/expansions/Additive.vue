<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-toggle class="my-toggle" v-model="additive.enabled" label="Enabled" standout dense></q-toggle>
    <div v-if="additive.enabled">
      <q-separator></q-separator>
      <q-list v-for="additiveModel, index in additive.additiveModels" :key="additiveModel.additiveModelId as PropertyKey"
        style="padding: 0px">
        <div class="row my-row">
          <q-input class="my-input" v-model="additiveModel.name" :rules="[rules.required, rules.name]" label="Name"
            standout dense></q-input>
          <q-select class="my-input" :options="additiveTypes" v-model="additiveModel.additiveType" label="Type" standout
            dense></q-select>
          <q-input class="my-input" v-model="additiveModel.printTemp" :rules="[rules.required, rules.float]"
            label="Print Temperature" standout dense></q-input>
          <!-- <q-input class="my-input" v-model="additiveModel.timeFactor" :rules="[rules.required, rules.float]"
            label="Time Factor" standout dense></q-input> -->
          <q-btn flat icon="fas fa-trash-alt" @click="removeAdditiveModel(index)">
            <q-tooltip>
              Remove Additive Model
            </q-tooltip>
          </q-btn>
        </div>
        <q-separator></q-separator>
      </q-list>

      <q-btn flat icon="fas fa-plus" @click="addAdditiveModel">
        <q-tooltip>
          Add additive Model
        </q-tooltip>
      </q-btn>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, toRaw } from 'vue'
import { useModelStore } from 'src/stores/model-store';
import type { Additive, AdditiveModel } from 'src/client';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'AdditiveSettings',
  setup() {
    const store = useModelStore();
    const additive = computed(() => store.modelData.additive) as unknown as Additive
    const additiveModels = computed(() => additive.additiveModels) as unknown as AdditiveModel[]
    return {
      store,
      additive,
      additiveModels,
      rules
    }
  },
  created() {
  },
  data() {
    return {
      additiveTypes: ['Simple'],
    };
  },
  methods: {
    addAdditiveModel() {
      if (!this.additiveModels) {
        this.additiveModels = []
      }
      const len = this.additiveModels.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.additiveModels[len - 1])) as AdditiveModel : {} as AdditiveModel;
      newItem.additiveModelId = len + 1
      newItem.name = 'Additive Model ' + (len + 1)
      this.additiveModels.push(newItem);
    },
    removeAdditiveModel(index: number) {
      this.additiveModels.splice(index, 1);
      this.additiveModels.forEach((model, i) => {
        model.additiveModelId = i + 1
      })
    },
  }
})
</script>
