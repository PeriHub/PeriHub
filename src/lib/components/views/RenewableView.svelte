<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { LineChart } from 'layerchart';
  import { getPrognosisEnergy } from '$lib/client';
  import { notify } from '$lib/utils/notify';

  let data = $state<{ date: Date; share: number }[]>([]);

  onMount(async () => {
    try {
      // response is { "YYYY-MM-DD HH:MM:SS": percent renewable share }
      const response = (await getPrognosisEnergy()) as Record<string, number>;
      data = Object.entries(response).map(([label, share]) => ({
        date: new Date(label.replace(' ', 'T')),
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
      xAxis: { classes: { tickLabel: 'fill-muted-foreground text-[10px]' } },
      yAxis: { classes: { tickLabel: 'fill-muted-foreground text-[10px]' } },
      grid: { class: 'stroke-border/40' }
    }}
  />
</div>
