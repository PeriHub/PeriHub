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
  // Same blue-white-red diverging scale used for the ModelView point cloud,
  // so the two views read consistently.
  const GRADIENT = 'linear-gradient(to top, rgb(59, 76, 192), rgb(221, 221, 221), rgb(180, 4, 38))';
</script>

<div class="flex h-48 items-stretch gap-3 rounded-md bg-background/80 p-3 text-sm shadow-sm backdrop-blur-sm">
  <div class="flex flex-col justify-between text-right text-muted-foreground">
    <span>{max.toPrecision(3)}</span>
    <span>{mid.toPrecision(3)}</span>
    <span>{min.toPrecision(3)}</span>
  </div>
  <div class="w-6 rounded-sm border border-border" style:background={GRADIENT}></div>
</div>
