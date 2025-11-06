<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <!-- <q-select class="my-select" :options="software" v-model="job.software" label="Software" standout dense></q-select> -->
    <q-toggle class="my-toggle" v-model="job.verbose" label="Verbose" standout dense></q-toggle>
    <q-toggle class="my-toggle" v-model="job.cluster" label="Cluster" standout dense @change="changeNumberOfTasks();"
      :disable="store.TRIAL"></q-toggle>
    <q-toggle class="my-toggle" v-model="job.sbatch" label="Sbatch" standout dense :disable="store.TRIAL"></q-toggle>
    <!-- <q-input
          class="my-input"
          v-model="job.nodes"
          v-show="job.cluster"
          :rules="[rules.required, rules.name]"
          label="Nodes"
          standout
          dense
      ></q-input> -->
    <q-input class="my-input" v-model="job.tasks" v-show="job.cluster" :rules="[rules.required, rules.int]"
      label="Tasks" standout dense></q-input>
    <!-- <q-input
          class="my-input"
          v-model="job.tasksPerNode"
          v-show="job.sbatch"
          :rules="[rules.required, rules.name]"
          label="Tasks per Node"
          standout
          dense
      ></q-input> -->
    <q-input class="my-input" v-model="job.cpusPerTask" v-show="job.sbatch" :rules="[rules.required, rules.int]"
      label="CPUs per Task" standout dense></q-input>
    <q-toggle class="my-toggle" v-model="job.multithread" v-show="job.sbatch" label="Multithreading" standout
      dense></q-toggle>
    <q-input class="my-input" v-model="job.time" v-show="job.sbatch" :rules="[rules.required, rules.name]" label="Time"
      standout dense></q-input>
    <q-input class="my-input" v-model="job.account" v-show="job.sbatch" :rules="[rules.required, rules.int]"
      label="Account" standout dense></q-input>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue'
import { useDefaultStore } from 'src/stores/default-store';
import { useModelStore } from 'src/stores/model-store';
import rules from 'assets/rules.js';

export default defineComponent({
  name: 'JobSettings',
  setup() {
    const store = useDefaultStore();
    const modelStore = useModelStore();
    const job = computed(() => modelStore.modelData.job)
    const cluster = false;
    // if (process.env.DLR) {
    //   cluster.push('Cara')
    // }
    return {
      store,
      job,
      rules,
      cluster,
    }
  },
  methods: {
    changeNumberOfTasks() {
      if (!this.job.cluster) {
        this.job.tasks = 1;
      }
    },
  }
})
</script>
