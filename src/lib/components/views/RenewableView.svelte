<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  import { getPrognosisEnergy } from '$lib/client';
  import { notify } from '$lib/utils/notify';

  let canvas: HTMLCanvasElement;

  onMount(async () => {
    try {
      const response = await getPrognosisEnergy();
      // response is expected as { [timestamp: string]: number } (percent renewable share)
      const entries = Object.entries(response as Record<string, number>);
      new Chart(canvas, {
        type: 'line',
        data: {
          labels: entries.map(([label]) => label),
          datasets: [
            {
              label: 'Percent of renewable energy share',
              data: entries.map(([, value]) => value),
              fill: true,
              tension: 0.3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true } }
        }
      });
    } catch (error) {
      notify.apiError(error);
    }
  });
</script>

<div class="h-full w-full p-2">
  <canvas bind:this={canvas}></canvas>
</div>
