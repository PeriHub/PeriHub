<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Tabs } from 'bits-ui';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
  import TextView from '$lib/components/views/TextView.svelte';
  import LogView from '$lib/components/views/LogView.svelte';

  function updateTextView() {
    if (viewStore.textId === 'input') {
      bus.emit('viewInputFile' as never);
    } else if (viewStore.textId === 'log') {
      bus.emit('enableWebsocket' as never);
    }
  }
  onMount(() => {
    bus.on('updateTextView' as never, updateTextView);
    return () => bus.off('updateTextView' as never, updateTextView);
  });

  const tabClass =
    'flex-1 px-3 py-2 text-center text-sm font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground';
</script>

<div class="border-border flex h-full flex-col overflow-hidden rounded-lg border">
  <Tabs.Root bind:value={viewStore.textId} class="flex h-full flex-col">
    <Tabs.List class="border-border bg-muted/40 flex border-b">
      <Tabs.Trigger value="input" class={tabClass}>Input</Tabs.Trigger>
      <Tabs.Trigger value="log" class={tabClass}>Log</Tabs.Trigger>
    </Tabs.List>

    {#if viewStore.logProgress}
      <div class="border-border border-b px-3 py-1.5">
        <ProgressBar
          value={viewStore.logProgress.percent}
          label="Simulation step {viewStore.logProgress.currentStep} / {viewStore.logProgress
            .totalSteps}"
        />
      </div>
    {/if}

    <div class="flex-1 overflow-auto">
      <Tabs.Content value="input" class="h-full"><TextView /></Tabs.Content>
      <Tabs.Content value="log" class="h-full"><LogView /></Tabs.Content>
    </div>
  </Tabs.Root>
</div>
