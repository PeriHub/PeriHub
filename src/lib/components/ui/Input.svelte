<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { X } from 'lucide-svelte';
  import { cn } from '$lib/utils';
  import type { HTMLInputAttributes } from 'svelte/elements';

  let {
    class: className,
    value = $bindable(),
    clearable = false,
    ...rest
  }: HTMLInputAttributes & { class?: string; clearable?: boolean } = $props();

  function clear() {
    value = null;
  }
</script>

<div class="relative flex w-full items-center">
  <input
    bind:value
    class={cn(
      'border-input bg-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-9 w-full rounded-md border px-3 py-1 text-sm shadow-sm transition-colors focus-visible:ring-2 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50',
      clearable && value != null && 'pr-7',
      className
    )}
    {...rest}
  />
  {#if clearable && value != null}
    <button
      type="button"
      aria-label="Clear value"
      onclick={clear}
      class="text-muted-foreground hover:text-foreground absolute inset-y-0 right-2 flex cursor-pointer items-center transition-colors"
    >
      <X class="h-4 w-4" />
    </button>
  {/if}
</div>
