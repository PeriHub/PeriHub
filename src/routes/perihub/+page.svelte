<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Tabs } from 'bits-ui';
  import {
    Sliders,
    LineChart,
    FileText,
    ChevronLeft,
    ChevronRight,
    ChevronUp,
    ChevronDown
  } from 'lucide-svelte';
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

  // Draggable split between the setup panel and the output panels, plus a
  // one-click collapse for when the user wants to give the output side the
  // full width (e.g. while just watching a running simulation). Persisted
  // so the layout a person settles on sticks across visits.
  const COLLAPSED_WIDTH_PX = 44;
  let setupWidthPercent = $state(42);
  let setupCollapsed = $state(false);
  let dragging = $state(false);
  let gridEl: HTMLDivElement | undefined;

  onMount(() => {
    const savedWidth = localStorage.getItem('periHubSetupWidth');
    if (savedWidth) setupWidthPercent = Number(savedWidth);
    setupCollapsed = localStorage.getItem('periHubSetupCollapsed') === 'true';
  });

  function startDrag(e: PointerEvent) {
    if (setupCollapsed) return;
    dragging = true;
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  }

  function onDrag(e: PointerEvent) {
    if (!dragging || !gridEl) return;
    const rect = gridEl.getBoundingClientRect();
    const pct = ((e.clientX - rect.left) / rect.width) * 100;
    setupWidthPercent = Math.min(65, Math.max(20, pct));
  }

  function stopDrag() {
    if (!dragging) return;
    dragging = false;
    localStorage.setItem('periHubSetupWidth', String(setupWidthPercent));
  }

  function toggleSetupCollapsed() {
    setupCollapsed = !setupCollapsed;
    localStorage.setItem('periHubSetupCollapsed', String(setupCollapsed));
  }

  // Same drag-to-resize / collapse pattern, applied vertically to the
  // ViewComp/TextComp split on the output side.
  const COLLAPSED_HEIGHT_PX = 40;
  let outputHeightPercent = $state(55);
  let textCollapsed = $state(false);
  let draggingV = $state(false);
  let outputEl: HTMLDivElement | undefined;

  onMount(() => {
    const savedHeight = localStorage.getItem('periHubOutputHeight');
    if (savedHeight) outputHeightPercent = Number(savedHeight);
    textCollapsed = localStorage.getItem('periHubTextCollapsed') === 'true';
  });

  function startDragV(e: PointerEvent) {
    if (textCollapsed) return;
    draggingV = true;
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  }

  function onDragV(e: PointerEvent) {
    if (!draggingV || !outputEl) return;
    const rect = outputEl.getBoundingClientRect();
    const pct = ((e.clientY - rect.top) / rect.height) * 100;
    outputHeightPercent = Math.min(80, Math.max(20, pct));
  }

  function stopDragV() {
    if (!draggingV) return;
    draggingV = false;
    localStorage.setItem('periHubOutputHeight', String(outputHeightPercent));
  }

  function toggleTextCollapsed() {
    textCollapsed = !textCollapsed;
    localStorage.setItem('periHubTextCollapsed', String(textCollapsed));
  }

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
          description:
            'Here you are able to submit your simulation, view your results and download them',
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
  <!-- Desktop / tablet layout: side-by-side panels, split adjustable via the
     drag handle and collapsible via its double-click / chevron toggle. -->
  <div
    bind:this={gridEl}
    class="grid h-full gap-0 overflow-hidden p-3"
    style="grid-template-columns: {setupCollapsed
      ? `${COLLAPSED_WIDTH_PX}px`
      : `${setupWidthPercent}%`} 10px 1fr;"
    onpointermove={onDrag}
    onpointerup={stopDrag}
  >
    <div
      id="model-configuration"
      class="border-border relative flex min-h-0 flex-col overflow-hidden rounded-lg border"
    >
      <button
        type="button"
        onclick={toggleSetupCollapsed}
        title="Expand setup panel"
        class="bg-background text-muted-foreground hover:text-foreground absolute inset-0 z-10 flex flex-col items-center gap-2 py-3 {setupCollapsed
          ? ''
          : 'hidden'}"
      >
        <ChevronRight class="h-4 w-4" />
        <span class="text-xs font-medium [writing-mode:vertical-rl]">Setup</span>
      </button>
      <div class="flex min-h-0 flex-1 flex-col {setupCollapsed ? 'invisible' : ''}">
        <div id="ModelActions"><ModelActions /></div>
        <div id="ExpansionComp" class="min-h-0 flex-1 overflow-hidden">
          <ExpansionComp />
        </div>
      </div>
    </div>

    <div
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize setup panel"
      tabindex="0"
      class="group relative mx-1 flex items-center justify-center {setupCollapsed
        ? ''
        : 'cursor-col-resize'}"
      onpointerdown={startDrag}
      ondblclick={toggleSetupCollapsed}
    >
      <div class="bg-border group-hover:bg-primary h-full w-px transition-colors"></div>
      <button
        type="button"
        onclick={toggleSetupCollapsed}
        title={setupCollapsed ? 'Expand setup panel' : 'Collapse setup panel'}
        class="border-border bg-background text-muted-foreground hover:text-foreground absolute rounded-full border p-0.5 shadow-sm"
      >
        {#if setupCollapsed}
          <ChevronRight class="h-3 w-3" />
        {:else}
          <ChevronLeft class="h-3 w-3" />
        {/if}
      </button>
    </div>

    <div
      bind:this={outputEl}
      id="model-output"
      class="grid min-h-0 overflow-hidden"
      style="grid-template-rows: {textCollapsed
        ? '1fr'
        : `${outputHeightPercent}%`} 10px {textCollapsed ? `${COLLAPSED_HEIGHT_PX}px` : '1fr'};"
      onpointermove={onDragV}
      onpointerup={stopDragV}
    >
      <div class="flex min-h-0 flex-col overflow-hidden">
        <div id="ViewActions"><ViewActions /></div>
        <div id="ViewComp" class="min-h-0 flex-1 overflow-hidden"><ViewComp /></div>
      </div>

      <div
        role="separator"
        aria-orientation="horizontal"
        aria-label="Resize input/log panel"
        tabindex="0"
        class="group relative my-1 flex items-center justify-center {textCollapsed
          ? ''
          : 'cursor-row-resize'}"
        onpointerdown={startDragV}
        ondblclick={toggleTextCollapsed}
      >
        <div class="bg-border group-hover:bg-primary h-px w-full transition-colors"></div>
        <button
          type="button"
          onclick={toggleTextCollapsed}
          title={textCollapsed ? 'Expand input/log panel' : 'Collapse input/log panel'}
          class="border-border bg-background text-muted-foreground hover:text-foreground absolute rounded-full border p-0.5 shadow-sm"
        >
          {#if textCollapsed}
            <ChevronUp class="h-3 w-3" />
          {:else}
            <ChevronDown class="h-3 w-3" />
          {/if}
        </button>
      </div>

      <div class="relative flex min-h-0 flex-col overflow-hidden">
        <button
          type="button"
          onclick={toggleTextCollapsed}
          title="Expand input/log panel"
          class="bg-background text-muted-foreground hover:text-foreground absolute inset-0 z-10 flex flex-row items-center justify-center gap-2 {textCollapsed
            ? ''
            : 'hidden'}"
        >
          <ChevronUp class="h-4 w-4" />
          <span class="text-xs font-medium">Input / Log</span>
        </button>
        <div
          class="flex min-h-0 flex-1 flex-col overflow-hidden {textCollapsed ? 'invisible' : ''}"
        >
          <div id="TextActions"><TextActions /></div>
          <div id="TextComp" class="min-h-0 flex-1 overflow-hidden"><TextComp /></div>
        </div>
      </div>
    </div>
  </div>
{:else}
  <!-- Narrow-screen layout: splitters/side-by-side panels don't work well with
     touch on small viewports, so stack the three work areas as swipeable
     tabs instead. Mounted only when isDesktop is false, so this never
     coexists with the desktop layout above. -->
  <div class="flex h-full flex-col overflow-hidden">
    <Tabs.Root bind:value={mobileTab} class="flex h-full flex-col">
      <Tabs.List class="border-border bg-muted/40 flex border-b">
        <Tabs.Trigger
          value="setup"
          class="text-muted-foreground data-[state=active]:border-primary data-[state=active]:text-foreground flex flex-1 items-center justify-center gap-1.5 px-2 py-2.5 text-sm font-medium data-[state=active]:border-b-2"
        >
          <Sliders class="h-4 w-4" /> Setup
        </Tabs.Trigger>
        <Tabs.Trigger
          value="results"
          class="text-muted-foreground data-[state=active]:border-primary data-[state=active]:text-foreground flex flex-1 items-center justify-center gap-1.5 px-2 py-2.5 text-sm font-medium data-[state=active]:border-b-2"
        >
          <LineChart class="h-4 w-4" /> Results
        </Tabs.Trigger>
        <Tabs.Trigger
          value="input"
          class="text-muted-foreground data-[state=active]:border-primary data-[state=active]:text-foreground flex flex-1 items-center justify-center gap-1.5 px-2 py-2.5 text-sm font-medium data-[state=active]:border-b-2"
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
