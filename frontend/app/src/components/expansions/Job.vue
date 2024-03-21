<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <!-- <q-select class="my-select" :options="software" v-model="job.software" label="Software" standout dense></q-select> -->
    <q-select class="my-select" :options="cluster" v-model="job.cluster" label="Cluster"
      @change="changeNumberOfTasks();" standout dense></q-select>
    <!-- <q-input
          class="my-input"
          v-model="job.nodes"
          v-show="job.cluster=='Cara'"
          :rules="[rules.required, rules.name]"
          label="Nodes"
          standout
          dense
      ></q-input> -->
    <q-input class="my-input" v-model="job.tasks" v-show="job.cluster == 'Cara'" :rules="[rules.required, rules.name]"
      label="Tasks" standout dense></q-input>
    <!-- <q-input
          class="my-input"
          v-model="job.tasksPerNode"
          v-show="job.cluster=='Cara'"
          :rules="[rules.required, rules.name]"
          label="Tasks per Node"
          standout
          dense
      ></q-input> -->
    <q-input class="my-input" v-model="job.cpusPerTask" v-show="job.cluster == 'Cara'"
      :rules="[rules.required, rules.name]" label="CPUs per Task" standout dense></q-input>
    <q-toggle class="my-toggle" v-model="job.multithread" v-show="job.cluster == 'Cara'" label="Multithreading" standout
      dense></q-toggle>
    <q-input class="my-input" v-model="job.time" v-show="job.cluster == 'Cara'" :rules="[rules.required, rules.name]"
      label="Time" standout dense></q-input>
    <q-input class="my-input" v-model="job.account" v-show="job.cluster == 'Cara'" :rules="[rules.required, rules.name]"
      label="Account" standout dense></q-input>
  </div>
</template>

<script>
import { computed, defineComponent } from 'vue'
import { useModelStore } from 'stores/model-store';
import { inject } from 'vue'
import rules from "assets/rules.js";

export default defineComponent({
  name: 'JobSettings',
  setup() {
    const store = useModelStore();
    const solver = computed(() => store.modelData.solver)
    const job = computed(() => store.modelData.job)
    const bus = inject('bus')
    let cluster = ["None"];
    // if (process.env.DLR) {
    //   cluster.push("Cara")
    // }
    return {
      store,
      solver,
      job,
      rules,
      bus,
      cluster,
    }
  },
  created() {
  },
  methods: {
    changeNumberOfTasks() {
      if (this.job.cluster == "None") {
        this.job.tasks = 1;
      }
    },
  }
})
</script>
