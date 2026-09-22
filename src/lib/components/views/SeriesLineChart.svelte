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
  const PALETTE = [
    '#00658b',
    '#d2ae3d',
    '#82a043',
    '#666666',
    '#3b98cb',
    '#f2cd51',
    '#a6bf51',
    '#858585'
  ];

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

  // Simulation output ranges over many orders of magnitude in the same
  // chart (near-zero forces alongside triple-digit displacements), so a
  // fixed-decimal tick format shows "0.00" for most of the smaller series.
  // Format ticks in scientific notation instead. Guard against non-number
  // input defensively - a thrown error while formatting one tick can take
  // down the whole axis (both the label AND its tick mark), which is why
  // ticks disappeared entirely rather than just rendering wrong.
  const scientificFormat = (value: unknown) => {
    const num = typeof value === 'number' ? value : Number(value);
    return Number.isFinite(num) ? num.toExponential(1) : String(value ?? '');
  };

  // layerchart's default padding is sized for short, fixed-decimal tick
  // labels. Scientific notation ticks ("1.23e+2") are wider, and the
  // reserved bottom space also needs to fit the x-axis title above the
  // legend row rendered below the chart - otherwise the title overflows
  // the plot area and renders on top of/underneath the legend. Widen
  // left/bottom padding to fit both.
  const chartPadding = { top: 8, right: 16, bottom: 48, left: 64 };
</script>

<div class="relative flex h-[28rem] w-full flex-col {className}">
  {#if xDomain}
    <button
      type="button"
      onclick={() => (xDomain = undefined)}
      class="border-border bg-background/90 text-muted-foreground hover:text-foreground absolute top-2 right-2 z-10 rounded border px-2 py-1 text-xs"
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
    padding={chartPadding}
    brush={{
      // Default brush styling relies on @layerstack/tailwind tokens this
      // app's OKLCH theme doesn't define (same issue worked around for
      // axis/grid/tooltip above), so the drag-selection rectangle rendered
      // with no visible fill/stroke at all. Use this app's own tokens.
      classes: {
        range: 'fill-primary/15 stroke-primary',
        handle: 'bg-primary'
      }
    }}
    props={{
      xAxis: { label: xLabel, classes: axisClasses, format: scientificFormat, tickOcclusion: true },
      yAxis: { label: yLabel, classes: axisClasses, format: scientificFormat, tickOcclusion: true },
      grid: { class: 'stroke-border/40' },
      rule: { class: 'stroke-border' },
      legend: {
        placement: 'bottom',
        classes: { root: 'text-xs shrink-0', label: 'text-muted-foreground text-xs' }
      },
      tooltip: {
        root: {
          class:
            'rounded-md border border-border bg-popover text-popover-foreground shadow-md px-2 py-1.5 text-xs'
        }
      }
    }}
  />
</div>
