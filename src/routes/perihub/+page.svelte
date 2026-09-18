<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Tabs } from 'bits-ui';
  import { Sliders, LineChart, FileText } from 'lucide-svelte';
  import ExpansionComp from '$lib/components/ExpansionComp.svelte';
  import ViewComp from '$lib/components/ViewComp.svelte';
  import TextComp from '$lib/components/TextComp.svelte';
  import ModelActions from '$lib/components/actions/ModelActions.svelte';
  import ViewActions from '$lib/components/actions/ViewActions.svelte';
  import TextActions from '$lib/components/actions/TextActions.svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { bus } from '$lib/utils/bus';

  let mobileTab = $state('setup');

  // Only one of the desktop/mobile layouts must ever be mounted at a time -
  // rendering both simultaneously (previously toggled with `hidden lg:grid` /
  // `flex lg:hidden`) duplicated every stateful component (ModelActions,
  // ViewActions, TextActions, TextComp, ...) and their bus listeners, causing
  // every bus.emit(...) to fire its handlers multiple times.
  // Default to desktop for SSR; corrected on the client before paint.
  let isDesktop = $state(true);

  onMount(() => {
    const mql = window.matchMedia('(min-width: 1024px)');
    isDesktop = mql.matches;
    const onChange = (e: MediaQueryListEvent) => (isDesktop = e.matches);
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  });

  async function showTutorial() {
    // @ts-expect-error driver.js v0.9 ships no type declarations
    const { default: Driver } = await import('driver.js');
    // @ts-expect-error nor for its CSS
    await import('driver.js/dist/driver.min.css');

    const driver = new Driver({
      animate: true,
      opacity: 0.5,
      stageBackground: defaultStore.darkMode ? 'gray' : 'white'
    });

    driver.defineSteps([
      {
        element: '#ModelActions',
        popover: {
          title: 'ModelActions',
          description: 'Here you are able to upload, save, switch and generate models',
          position: 'right'
        }
      },
      {
        element: '#ExpansionComp',
        popover: {
          title: 'ExpansionComp',
          description: 'Here you can find the configuration for your simulation',
          position: 'right'
        }
      },
      {
        element: '#ViewActions',
        popover: {
          title: 'ViewActions',
          description: 'Here you are able to submit your simulation, view your results and download them',
          position: 'left'
        }
      },
      {
        element: '#ViewComp',
        popover: {
          title: 'ViewComp',
          description: 'This is where your simulation results are displayed',
          position: 'left'
        }
      },
      {
        element: '#TextActions',
        popover: {
          title: 'TextActions',
          description: 'If you want to edit your input-deck you can save it here',
          position: 'left'
        }
      },
      {
        element: '#TextComp',
        popover: {
          title: 'TextComp',
          description: 'This is where your input-deck or log-file is displayed',
          position: 'left'
        }
      }
    ]);

    driver.start();
  }

  onMount(() => {
    bus.on('showTutorial' as never, showTutorial);

    // Auto-launch the tour once for first-time visitors instead of relying
    // solely on them discovering the help icon in the header.
    if (!localStorage.getItem('periHubTourSeen')) {
      localStorage.setItem('periHubTourSeen', 'true');
      setTimeout(showTutorial, 600);
    }

    return () => bus.off('showTutorial' as never, showTutorial);
  });
</script>

<svelte:head>
  <title>PeriHub — Model Builder</title>
</svelte:head>

{#if isDesktop}
<!-- Desktop / tablet layout: side-by-side panels. -->
<div class="grid h-[calc(100vh-4rem)] grid-cols-1 gap-3 overflow-hidden p-3 lg:grid-cols-2">
  <div id="model-configuration" class="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border">
    <div id="ModelActions"><ModelActions /></div>
    <div id="ExpansionComp" class="min-h-0 flex-1 overflow-hidden">
      <ExpansionComp />
    </div>
  </div>

  <div id="model-output" class="flex min-h-0 flex-col gap-3 overflow-hidden">
    <div class="flex min-h-0 flex-1 flex-col overflow-hidden">
      <div id="ViewActions"><ViewActions /></div>
      <div id="ViewComp" class="min-h-0 flex-1 overflow-hidden"><ViewComp /></div>
    </div>
    <div class="flex min-h-0 flex-1 flex-col overflow-hidden">
      <div id="TextActions"><TextActions /></div>
      <div id="TextComp" class="min-h-0 flex-1 overflow-hidden"><TextComp /></div>
    </div>
  </div>
</div>
{:else}
<!-- Narrow-screen layout: splitters/side-by-side panels don't work well with
     touch on small viewports, so stack the three work areas as swipeable
     tabs instead. Mounted only when isDesktop is false, so this never
     coexists with the desktop layout above. -->
<div class="flex h-[calc(100vh-4rem)] flex-col overflow-hidden">
  <Tabs.Root bind:value={mobileTab} class="flex h-full flex-col">
    <Tabs.List class="flex border-b border-border bg-muted/40">
      <Tabs.Trigger
        value="setup"
        class="flex flex-1 items-center justify-center gap-1.5 px-2 py-2.5 text-sm font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground"
      >
        <Sliders class="h-4 w-4" /> Setup
      </Tabs.Trigger>
      <Tabs.Trigger
        value="results"
        class="flex flex-1 items-center justify-center gap-1.5 px-2 py-2.5 text-sm font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground"
      >
        <LineChart class="h-4 w-4" /> Results
      </Tabs.Trigger>
      <Tabs.Trigger
        value="input"
        class="flex flex-1 items-center justify-center gap-1.5 px-2 py-2.5 text-sm font-medium text-muted-foreground data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-foreground"
      >
        <FileText class="h-4 w-4" /> Input / Log
      </Tabs.Trigger>
    </Tabs.List>

    <div class="min-h-0 flex-1 overflow-hidden">
      <Tabs.Content value="setup" class="flex h-full flex-col overflow-hidden p-2">
        <ModelActions />
        <div class="min-h-0 flex-1 overflow-hidden">
          <ExpansionComp scrollable={false} />
        </div>
      </Tabs.Content>
      <Tabs.Content value="results" class="flex h-full flex-col overflow-hidden p-2">
        <ViewActions />
        <ViewComp />
      </Tabs.Content>
      <Tabs.Content value="input" class="flex h-full flex-col overflow-hidden p-2">
        <TextActions />
        <TextComp />
      </Tabs.Content>
    </div>
  </Tabs.Root>
</div>
{/if}
