<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Tabs } from 'bits-ui';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';

  import ImageView from '$lib/components/views/ImageView.svelte';
  import ModelView from '$lib/components/views/ModelView.svelte';
  import ResultsView from '$lib/components/views/ResultsView.svelte';
  import CadView from '$lib/components/views/CadView.svelte';
  import JobsView from '$lib/components/views/JobsView.svelte';
  import PlotlyView from '$lib/components/views/PlotlyView.svelte';
  import RenewableView from '$lib/components/views/RenewableView.svelte';

  const outputs = $derived(modelStore.modelData.outputs ?? []);
  const showResults = $derived(outputs.some((o) => o.selectedFileType === 'Exodus'));
  const showPlotly = $derived(outputs.some((o) => o.selectedFileType === 'CSV'));

  const tabClass =
    'px-3 py-2 text-sm font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground';
</script>

<div class="flex h-full flex-col overflow-hidden rounded-lg border border-border">
  <Tabs.Root bind:value={viewStore.viewId} class="flex h-full flex-col">
    <Tabs.List class="flex flex-wrap justify-between border-b border-border bg-muted/40">
      <Tabs.Trigger value="image" class={tabClass}>Image</Tabs.Trigger>
      <Tabs.Trigger value="model" class={tabClass}>Model</Tabs.Trigger>
      <Tabs.Trigger value="cad" class={tabClass}>CAD</Tabs.Trigger>
      <Tabs.Trigger value="jobs" class={tabClass}>Jobs</Tabs.Trigger>
      {#if showResults}
        <Tabs.Trigger value="results" class={tabClass}>Results</Tabs.Trigger>
      {/if}
      {#if showPlotly}
        <Tabs.Trigger value="plotly" class={tabClass}>Plotly</Tabs.Trigger>
      {/if}
      {#if defaultStore.saveEnergy}
        <Tabs.Trigger value="renewable" class={tabClass}>Renewable</Tabs.Trigger>
      {/if}
    </Tabs.List>

    <div class="flex-1 overflow-auto">
      <Tabs.Content value="image" class="h-full"><ImageView /></Tabs.Content>
      <Tabs.Content value="model" class="h-full"><ModelView /></Tabs.Content>
      <Tabs.Content value="cad" class="h-full"><CadView /></Tabs.Content>
      <Tabs.Content value="jobs" class="h-full"><JobsView /></Tabs.Content>
      <Tabs.Content value="results" class="h-full"><ResultsView /></Tabs.Content>
      <Tabs.Content value="plotly" class="h-full"><PlotlyView /></Tabs.Content>
      <Tabs.Content value="renewable" class="h-full"><RenewableView /></Tabs.Content>
    </div>
  </Tabs.Root>
</div>
