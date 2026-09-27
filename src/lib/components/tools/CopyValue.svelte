<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Copy } from 'lucide-svelte';
  import { copyText } from '$lib/utils/clipboard';

  let { value, unit = '', label }: { value: string; unit?: string; label: string } = $props();
</script>

<button
  type="button"
  onclick={() => copyText(value)}
  aria-label={`Copy ${label}`}
  title="Copy"
  class="group hover:bg-muted focus-visible:ring-ring -mx-1.5 inline-flex max-w-full flex-wrap items-baseline gap-x-1.5 rounded px-1.5 py-1 text-left font-mono text-sm transition-colors focus-visible:ring-2 focus-visible:outline-none"
>
  <span class="break-all">{value}</span>
  {#if unit}<span class="text-muted-foreground shrink-0 text-xs">{unit}</span>{/if}
  <Copy
    class="text-muted-foreground size-3.5 shrink-0 opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100 pointer-coarse:opacity-60"
    aria-hidden="true"
  />
</button>
