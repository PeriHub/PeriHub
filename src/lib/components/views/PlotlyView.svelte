<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import PlotlyChart from '$lib/components/views/PlotlyChart.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
</script>

<PlotlyChart data={viewStore.plotData} layout={viewStore.plotLayout} class="h-full" />
