<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  interface Props {
    min: number;
    max: number;
    numValues?: number;
  }

  let { min, max, numValues = 11 }: Props = $props();

  // Evenly spaced tick values from min to max, low to high - matches the
  // old Vue component's default of 11 labeled steps instead of just
  // min/mid/max.
  const values = $derived.by(() => {
    const interval = (max - min) / (numValues - 1);
    return Array.from({ length: numValues }, (_, i) => min + i * interval);
  });

  // Exact colours from the old Vue component's gradient, top (max, red) to
  // bottom (min, blue) - a rainbow sweep, not vtk.js's own red-to-blue
  // default direction.
  const GRADIENT =
    'linear-gradient(to bottom, #ec3c3f, #fb8620, #f3b500, #ded302, #bae216, #7fe345, #41da8a, #14c6c7, #21a1e7, #3f72f0, #5125ee)';
</script>

<div class="flex h-56 items-stretch gap-2 rounded-md p-1 pr-2 text-sm shadow-sm backdrop-blur-sm">
  <div class="relative w-6 rounded-sm border border-border" style:background={GRADIENT}>
    {#each values as value, index (index)}
      <span
        class="absolute left-full ml-1. translate-y-1/2 whitespace-nowrap text-xs text-white"
        style:bottom={`${(index / (numValues - 1)) * 100}%`}
      >
        &#8213; {value.toExponential(2)}
      </span>
    {/each}
  </div>
</div>
