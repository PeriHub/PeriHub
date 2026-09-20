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

  // Merge in a stable uirevision so that Plotly.react() preserves the
  // user's current zoom/pan across re-renders instead of re-applying
  // whatever ranges happen to be in `layout` every time data/layout change.
  function mergedLayout() {
    return { uirevision: 'plotly-chart', ...layout };
  }

  onMount(async () => {
    Plotly = (await import('plotly.js-dist-min')).default;
    Plotly.newPlot(el, data, mergedLayout(), config);
  });

  $effect(() => {
    // re-render on data/layout change
    if (Plotly && el) {
      Plotly.react(el, data, mergedLayout(), config);
    }
  });

  onDestroy(() => {
    if (Plotly && el) Plotly.purge(el);
  });

  // Forces a real reset to the full data extent, even if `layout` itself
  // carries explicit (zoomed-in) axis ranges — the built-in "reset axes"
  // modebar button only restores whatever range is in `layout`, which is
  // not helpful if that range is the zoomed-in one.
  export function resetZoom() {
    if (Plotly && el) {
      Plotly.relayout(el, { 'xaxis.autorange': true, 'yaxis.autorange': true });
    }
  }
</script>

<div bind:this={el} class="h-96 w-full {className}"></div>
