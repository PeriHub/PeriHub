<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <VuePlotly :data="viewStore.plotData" :layout="viewStore.plotLayout" :options="plotOptions" :display-mode-bar="true">
  </VuePlotly>
</template>

<script>
import { defineComponent } from 'vue'
import { useViewStore } from 'stores/view-store';
import { VuePlotly } from 'vue3-plotly'
export default defineComponent({
  name: 'PlotlyView',
  components: {
    VuePlotly
  },
  setup() {
    const viewStore = useViewStore();

    return {
      viewStore,
    }
  },
  data() {
    return {
      plotOptions: {
        scrollZoom: true,
        setBackground: "black",
      },
    };
  },
  methods: {},
})
</script>

<style></style>
