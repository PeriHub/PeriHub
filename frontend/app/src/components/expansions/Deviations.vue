<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-toggle class="my-toggle" v-model="deviations.enabled" label="Enabled" standout dense :disable="store.TRIAL">
      <q-tooltip v-if="store.TRIAL">
        <div>Disabled in trial version</div>
      </q-tooltip>
    </q-toggle>
    <div v-if="deviations.enabled">
      <q-input class="my-input" v-model="deviations.sampleSize" :rules="[rules.required, rules.int]" label="sampleSize"
        standout dense></q-input>
      <q-separator></q-separator>
      <q-list v-for="parameter, index in deviations.parameters" :key="parameter.parameterId as PropertyKey"
        style="padding: 0px">
        <div class="row my-row">
          <q-select class="my-input" :options="filterOptions" v-model="parameter.id" label="Id" use-input use-chips
            multiple input-debounce="0" @filter="filterFn" standout dense></q-select>
          <q-input class="my-input" v-model="parameter.std" :rules="[rules.required, rules.float]" label="Std" standout
            dense></q-input>
          <q-btn flat icon="fas fa-trash-alt" @click="removeParameter(index)">
            <q-tooltip>
              Remove parameter
            </q-tooltip>
          </q-btn>
        </div>
        <q-separator></q-separator>
      </q-list>

      <q-btn flat icon="fas fa-plus" @click="addParameter">
        <q-tooltip>
          Add parameter
        </q-tooltip>
      </q-btn>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, toRaw } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import type { Parameter, Deviations } from 'src/client';
// @vue-expect-error Bla
import objleaves from 'objleaves';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'DeviationsSettings',
  setup() {
    const store = useDefaultStore();
    const modelStore = useModelStore();
    const modelData = computed(() => modelStore.modelData)
    const deviations = computed(() => modelStore.modelData.deviations) as unknown as Deviations
    return {
      store,
      modelData,
      deviations,
      rules,
    }
  },
  data() {
    return {
      parameters: [
        'materials[0].youngsModulus'
      ],
      distrKeys: {
        gcode: {
          overwriteMesh: 'overwriteMesh',
          sampling: 'Sampling',
          width: 'Width',
          height: 'Height',
          scale: 'Scale'
        }
      },
      filterOptions: [] as string[],
    }
  },
  mounted() {
    this.getAllParameters()
  },
  methods: {
    filterFn(val: string, update: (callbackFn: () => void) => void) {
      update(() => {
        if (val === '') {
          this.filterOptions = this.parameters
        }
        else {
          const needle = val.toLowerCase()
          this.filterOptions = this.parameters.filter(
            v => v.toLowerCase().indexOf(needle) > -1
          )
        }
      })
    },
    getAllParameters() {
      this.parameters = objleaves(this.modelData)
    },
    addParameter() {
      if (!this.deviations.parameters) {
        this.deviations.parameters = []
      }
      const len = this.deviations.parameters.length;
      const newItem = len > 0 ? structuredClone(toRaw(this.deviations.parameters[len - 1])) as Parameter : {} as Parameter;
      newItem.parameterId = len + 1
      this.deviations.parameters.push(newItem);
    },
    removeParameter(index: number) {
      this.deviations.parameters.splice(index, 1);
      this.deviations.parameters.forEach((model, i) => {
        model.parameterId = i + 1
      })
    },
  },
})
</script>
