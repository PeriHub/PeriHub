<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<template>
  <VuePlotly :data="viewStore.plotData" :layout="plotLayout" :options="plotOptions" :display-mode-bar="true">
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
      plotLayout: {
        // title: 'this.model.modelNameSelected',
        showlegend: true,
        // margin: { t: 50 },
        hovermode: "compare",
        bargap: 0,
        xaxis: {
          showgrid: true,
          zeroline: true,
          color: "white",
        },
        yaxis: {
          showgrid: true,
          zeroline: true,
          color: "white",
        },
        xaxis2: {
          showgrid: false,
          zeroline: false,
        },
        yaxis2: {
          showgrid: true,
          zeroline: false,
        },
        plot_bgcolor: "#2D2D2D",
        paper_bgcolor: "#2D2D2D",
        font: {
          color: "white",
        },
        modebar: {
          color: "white",
          // color: "#6E6E6E"
        },
      },
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
