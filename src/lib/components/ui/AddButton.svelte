<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Copy, Plus } from 'lucide-svelte';
  import Button from '$lib/components/ui/Button.svelte';

  // The setup panels' add handlers copy the last row, so say so: "Duplicate
  // BC_2" (or "Duplicate last node set" for unnamed rows), "Add ..." when empty.
  interface Props {
    noun: string;
    items: readonly unknown[] | null | undefined;
    onclick: () => void;
    class?: string;
  }

  let { noun, items, onclick, class: className }: Props = $props();

  const last = $derived(items?.at(-1) as { name?: unknown } | undefined);
  const lastName = $derived(typeof last?.name === 'string' && last.name ? last.name : null);
</script>

<Button variant="outline" size="sm" class={className} {onclick}>
  {#if last}
    <Copy class="h-4 w-4" /> Duplicate {lastName ?? `last ${noun}`}
  {:else}
    <Plus class="h-4 w-4" /> Add {noun}
  {/if}
</Button>
