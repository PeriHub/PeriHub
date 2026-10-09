<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { untrack } from 'svelte';
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
  const status = $derived(defaultStore.status);
  const modelReady = $derived(Boolean(status.created && status.meshfileExist));
  const resultsReady = $derived(
    Boolean(status.results) && outputs.some((o) => o.selectedFileType === 'Exodus')
  );
  // Generate / run switch to these tabs before their files exist - keep the
  // tab visible while it is selected so the loading state stays reachable.
  const showModel = $derived(modelReady || viewStore.viewId === 'model');
  const showResults = $derived(resultsReady || viewStore.viewId === 'results');
  const showChart = $derived(outputs.some((o) => o.selectedFileType === 'CSV'));

  // A status refresh says the open tab has no files (other folder, failed
  // run) - fall back to the preview unless they are still being produced.
  $effect(() => {
    const view = untrack(() => viewStore.viewId);
    if (view === 'model' && !modelReady && !untrack(() => viewStore.modelLoading)) {
      viewStore.viewId = 'image';
    } else if (view === 'results' && !resultsReady && !status.submitted) {
      viewStore.viewId = 'image';
    }
  });

  // CAD view hidden for now; flip to bring the tab back.
  const showCad = false;

  const tabClass =
    'px-3 py-2 pr-4 text-ml font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground';
</script>

<div class="flex h-full flex-col overflow-hidden">
  <Tabs.Root bind:value={viewStore.viewId} class="flex h-full flex-col">
    <Tabs.List class="border-border bg-muted/40 flex flex-wrap justify-center gap-x-6 border-b">
      <Tabs.Trigger value="image" class={tabClass}>Preview</Tabs.Trigger>
      {#if showModel}
        <Tabs.Trigger value="model" class={tabClass}>Model</Tabs.Trigger>
      {/if}
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
      <Tabs.Content value="results" class="h-full">
        <!-- bits-ui keeps inactive panels mounted; remount so each visit loads the current run and frames the camera. -->
        {#if viewStore.viewId === 'results'}<ResultsView />{/if}
      </Tabs.Content>
      <Tabs.Content value="plotly" class="h-full"><ChartView /></Tabs.Content>
      <Tabs.Content value="analysis" class="h-full"><AnalysisView /></Tabs.Content>
      <Tabs.Content value="renewable" class="h-full"><RenewableView /></Tabs.Content>
    </div>
  </Tabs.Root>
</div>
