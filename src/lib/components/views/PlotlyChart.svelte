<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  interface Props {
    data: Record<string, unknown>[];
    layout?: Record<string, unknown>;
    class?: string;
  }

  let { data, layout = {}, class: className = '' }: Props = $props();

  let el: HTMLDivElement;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let Plotly: any;

  const config = { responsive: true, scrollZoom: true, displayModeBar: true };

  onMount(async () => {
    Plotly = (await import('plotly.js-dist-min')).default;
    Plotly.newPlot(el, data, layout, config);
  });

  $effect(() => {
    // re-render on data/layout change
    if (Plotly && el) {
      Plotly.react(el, data, layout, config);
    }
  });

  onDestroy(() => {
    if (Plotly && el) Plotly.purge(el);
  });
</script>

<div bind:this={el} class="h-96 w-full {className}"></div>
