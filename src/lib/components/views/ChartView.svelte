<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import SeriesLineChart from '$lib/components/views/SeriesLineChart.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';

  // viewStore.plotData/plotLayout still use their old Plotly-shaped fields
  // (ViewActions.svelte populates them) - adapted to SeriesLineChart's props
  // here rather than reworking that population logic too.
  const series = $derived(viewStore.plotData.map((s) => ({ name: s.name, x: s.x, y: s.y })));
  const xLabel = $derived(viewStore.plotLayout.xaxis?.title ?? '');
  const yLabel = $derived(viewStore.plotLayout.yaxis?.title ?? '');
</script>

<SeriesLineChart {series} {xLabel} {yLabel} class="h-full" />
