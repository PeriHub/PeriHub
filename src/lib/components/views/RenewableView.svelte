<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { LineChart, Rule } from 'layerchart';
  import { getPrognosisEnergy } from '$lib/client';
  import { notify } from '$lib/utils/notify';

  let data = $state<{ date: Date; share: number }[]>([]);
  const now = new Date();

  onMount(async () => {
    try {
      // response is { "<UTC ISO time>": percent renewable share }
      const response = (await getPrognosisEnergy()) as Record<string, number>;
      data = Object.entries(response).map(([time, share]) => ({
        date: new Date(time),
        share
      }));
    } catch (error) {
      notify.apiError(error);
    }
  });
</script>

<div class="h-full min-h-64 w-full p-2">
  <LineChart
    {data}
    x="date"
    y="share"
    yDomain={[0, null]}
    series={[{ key: 'share', label: 'Percent of renewable energy share', color: '#82a043' }]}
    points={false}
    props={{
      xAxis: {
        format: (d: Date | number) =>
          new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        classes: { tickLabel: 'fill-muted-foreground text-[10px]' }
      },
      yAxis: { classes: { tickLabel: 'fill-muted-foreground text-[10px]' } },
      grid: { class: 'stroke-border/40' }
    }}
  >
    <svelte:fragment slot="aboveMarks">
      <Rule x={now} class="stroke-foreground/60 [stroke-dasharray:4_3]" />
    </svelte:fragment>
  </LineChart>
</div>
