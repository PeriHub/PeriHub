<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { LineChart } from 'layerchart';

  interface Series {
    name: string;
    x: number[];
    y: number[];
    color?: string;
  }

  interface Props {
    series: Series[];
    xLabel?: string;
    yLabel?: string;
    class?: string;
  }

  let { series, xLabel = '', yLabel = '', class: className = '' }: Props = $props();

  // Bound to LineChart's xDomain: undefined means "full extent". Set by
  // dragging a selection (brush), cleared by the reset button below.
  let xDomain = $state<[number, number] | undefined>(undefined);

  // Same brand palette already used for the old Plotly series colours.
  const PALETTE = ['#00658b', '#d2ae3d', '#82a043', '#666666', '#3b98cb', '#f2cd51', '#a6bf51', '#858585'];

  // LayerChart's LineChart takes each series as its own {key, data, value}
  // entry rather than Plotly's flat {data, layout} shape, so each series
  // carries its own {x, y} points and an explicit `value: 'y'` accessor
  // (without it, a series that supplies its own `data` gets no y accessor
  // at all and silently fails to render).
  const lcSeries = $derived(
    series.map((s, i) => ({
      key: s.name,
      label: s.name,
      value: 'y' as const,
      color: s.color ?? PALETTE[i % PALETTE.length],
      data: s.x.map((xVal, idx) => ({ x: xVal, y: s.y[idx] }))
    }))
  );

  // LayerChart's own default styling leans on @layerstack/tailwind's design
  // tokens (surface-*, color-primary as a bare HSL triplet), which this
  // app's OKLCH-based theme doesn't define, so axis/grid/tooltip would
  // otherwise render with no visible color at all. Overriding with this
  // app's own tokens throughout instead.
  const axisClasses = {
    rule: 'stroke-border',
    tick: 'stroke-border',
    tickLabel: 'fill-muted-foreground text-[10px]',
    label: 'fill-muted-foreground text-xs'
  };
</script>

<div class="relative h-96 w-full {className}">
  {#if xDomain}
    <button
      type="button"
      onclick={() => (xDomain = undefined)}
      class="absolute right-2 top-2 z-10 rounded border border-border bg-background/90 px-2 py-1 text-xs text-muted-foreground hover:text-foreground"
    >
      Reset zoom
    </button>
  {/if}
  <LineChart
    data={[]}
    x="x"
    y="y"
    series={lcSeries}
    legend={series.length > 1}
    points={false}
    bind:xDomain
    brush={{ resetOnEnd: true }}
    props={{
      xAxis: { label: xLabel, classes: axisClasses },
      yAxis: { label: yLabel, classes: axisClasses },
      grid: { class: 'stroke-border/40' },
      rule: { class: 'stroke-border' },
      legend: { classes: { root: 'text-xs', label: 'text-muted-foreground text-xs' } },
      tooltip: {
        root: {
          class: 'rounded-md border border-border bg-popover text-popover-foreground shadow-md px-2 py-1.5 text-xs'
        }
      }
    }}
  />
</div>
