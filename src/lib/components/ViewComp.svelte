<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Tabs } from 'bits-ui';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';

  import ModelPreview from '$lib/components/views/ModelPreview.svelte';
  import ModelView from '$lib/components/views/ModelView.svelte';
  import ResultsView from '$lib/components/views/ResultsView.svelte';
  import CadView from '$lib/components/views/CadView.svelte';
  import JobsView from '$lib/components/views/JobsView.svelte';
  import ChartView from '$lib/components/views/ChartView.svelte';
  import RenewableView from '$lib/components/views/RenewableView.svelte';
  import AnalysisView from '$lib/components/views/AnalysisView.svelte';
  import { modelNeedsRefresh } from '$lib/utils/modelSync';

  const outputs = $derived(modelStore.modelData.outputs ?? []);
  const showResults = $derived(outputs.some((o) => o.selectedFileType === 'Exodus'));
  const showChart = $derived(outputs.some((o) => o.selectedFileType === 'CSV'));

  // CAD view hidden for now; flip to bring the tab back.
  const showCad = false;

  const tabClass =
    'px-3 py-2 pr-4 text-ml font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground';
</script>

<div class="flex h-full flex-col overflow-hidden">
  <Tabs.Root bind:value={viewStore.viewId} class="flex h-full flex-col">
    <Tabs.List class="border-border bg-muted/40 flex flex-wrap justify-center gap-x-6 border-b">
      <Tabs.Trigger value="image" class={tabClass}>Preview</Tabs.Trigger>
      <Tabs.Trigger value="model" class={tabClass}>Model</Tabs.Trigger>
      {#if showCad}
        <Tabs.Trigger value="cad" class={tabClass}>CAD</Tabs.Trigger>
      {/if}
      <Tabs.Trigger value="jobs" class={tabClass}>Jobs</Tabs.Trigger>
      {#if showResults}
        <Tabs.Trigger value="results" class={tabClass}>Results</Tabs.Trigger>
      {/if}
      {#if showChart}
        <Tabs.Trigger value="plotly" class={tabClass}>Plot</Tabs.Trigger>
      {/if}
      {#if viewStore.analysisImage}
        <Tabs.Trigger value="analysis" class={tabClass}>Analysis</Tabs.Trigger>
      {/if}
      {#if defaultStore.saveEnergy}
        <Tabs.Trigger value="renewable" class={tabClass}>Renewable</Tabs.Trigger>
      {/if}
    </Tabs.List>

    <div class="flex-1 overflow-auto">
      <Tabs.Content value="image" class="h-full">
        <!-- Mid-switch, config/valves may still belong to the previous model. -->
        <ModelPreview
          modelName={modelStore.selectedModel.file}
          data={modelStore.modelData}
          valves={modelStore.modelParams}
          paused={modelNeedsRefresh(modelStore.selectedModel.file)}
        />
      </Tabs.Content>
      <Tabs.Content value="model" class="h-full"><ModelView /></Tabs.Content>
      {#if showCad}
        <Tabs.Content value="cad" class="h-full"><CadView /></Tabs.Content>
      {/if}
      <Tabs.Content value="jobs" class="h-full"><JobsView /></Tabs.Content>
      <Tabs.Content value="results" class="h-full"><ResultsView /></Tabs.Content>
      <Tabs.Content value="plotly" class="h-full"><ChartView /></Tabs.Content>
      <Tabs.Content value="analysis" class="h-full"><AnalysisView /></Tabs.Content>
      <Tabs.Content value="renewable" class="h-full"><RenewableView /></Tabs.Content>
    </div>
  </Tabs.Root>
</div>
