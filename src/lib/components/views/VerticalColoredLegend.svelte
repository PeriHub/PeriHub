<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  interface Props {
    min: number;
    max: number;
  }

  let { min, max }: Props = $props();

  const mid = $derived((min + max) / 2);
  // Matches vtk.js's own default lookup table (hueRange [0.0, 0.6667]):
  // a rainbow sweep from red at the low end to blue at the high end.
  const GRADIENT = 'linear-gradient(to top, red, yellow, lime, cyan, blue)';
</script>

<div class="flex h-48 items-stretch gap-3 rounded-md bg-background/80 p-3 text-sm shadow-sm backdrop-blur-sm">
  <div class="flex flex-col justify-between text-right text-muted-foreground">
    <span>{max.toPrecision(3)}</span>
    <span>{mid.toPrecision(3)}</span>
    <span>{min.toPrecision(3)}</span>
  </div>
  <div class="w-6 rounded-sm border border-border" style:background={GRADIENT}></div>
</div>
