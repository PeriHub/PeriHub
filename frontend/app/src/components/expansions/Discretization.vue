<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <div>
    <q-select class="my-select" :options="distributionTypes" v-model="discretization.distributionType"
      label="Distribution Type" standout dense></q-select>
  </div>
</template>

<script>
import { computed, defineComponent, inject } from 'vue'
import { useModelStore } from 'stores/model-store';
import rules from "assets/rules.js";

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
        "Neighbor based",
        "Node based"
      ]
    }
  }
})
</script>
