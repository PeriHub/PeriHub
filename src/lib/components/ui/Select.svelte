<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { cn } from '$lib/utils';
  import { ChevronDown } from 'lucide-svelte';
  import type { HTMLSelectAttributes } from 'svelte/elements';

  let {
    class: className,
    value = $bindable(),
    children,
    ...rest
  }: HTMLSelectAttributes & { class?: string; children?: import('svelte').Snippet } = $props();
</script>

<div class="relative">
  <select
    bind:value
    class={cn(
      'flex h-9 w-full appearance-none rounded-md border border-input bg-background px-3 py-1 pr-8 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
      className
    )}
    {...rest}
  >
    {@render children?.()}
  </select>
  <ChevronDown class="pointer-events-none absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
</div>
