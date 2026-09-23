<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  interface Props {
    /** 0-100. Omit/undefined to show an indeterminate (animated) bar. */
    value?: number | null;
    label?: string;
    class?: string;
  }

  let { value = null, label = '', class: className = '' }: Props = $props();

  const clamped = $derived(value === null || value === undefined ? null : Math.min(100, Math.max(0, value)));
</script>

<div class="w-full {className}">
  {#if label || clamped !== null}
    <div class="mb-1 flex items-center justify-between text-xs text-muted-foreground">
      <span>{label}</span>
      {#if clamped !== null}<span>{clamped.toFixed(0)}%</span>{/if}
    </div>
  {/if}
  <div class="h-1.5 w-full overflow-hidden rounded-full bg-muted">
    {#if clamped === null}
      <div class="h-full w-1/3 animate-[progress-indeterminate_1.2s_ease-in-out_infinite] rounded-full bg-primary"></div>
    {:else}
      <div class="h-full rounded-full bg-primary transition-[width] duration-500 ease-out" style:width="{clamped}%"></div>
    {/if}
  </div>
</div>

<style>
  @keyframes progress-indeterminate {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(300%);
    }
  }
</style>
