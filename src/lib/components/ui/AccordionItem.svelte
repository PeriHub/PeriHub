<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Accordion } from 'bits-ui';
  import { ChevronDown } from 'lucide-svelte';
  import type { Component } from 'svelte';
  import { cn } from '$lib/utils';
  import type { SectionStatus } from '$lib/utils/schemaValidation';

  interface Props {
    value: string;
    label: string;
    icon: Component;
    /** Optional required-fields-filled-in indicator (see schemaValidation.ts). Omit to hide. */
    status?: SectionStatus;
    children?: import('svelte').Snippet;
  }

  let { value, label, icon: Icon, status, children }: Props = $props();

  const STATUS_STYLE: Record<SectionStatus, { class: string; title: string }> = {
    complete: { class: 'bg-success', title: 'Required fields filled in' },
    incomplete: { class: 'bg-warning', title: 'Missing required fields' },
    unused: { class: 'border-muted-foreground border', title: 'Not used (optional)' }
  };
</script>

<Accordion.Item {value} class="border-border border-b last:border-b-0">
  <Accordion.Header>
    <Accordion.Trigger
      class="hover:bg-muted flex w-full items-center gap-3 px-4 py-3 text-left text-sm font-medium transition-colors [&[data-state=open]>svg]:rotate-180"
    >
      <Icon class="text-primary h-4 w-4 shrink-0" />
      <span class="flex-1">{label}</span>
      {#if status}
        <span
          class={cn('h-2 w-2 shrink-0 rounded-full', STATUS_STYLE[status].class)}
          title={STATUS_STYLE[status].title}
        ></span>
      {/if}
      <ChevronDown class="text-muted-foreground h-4 w-4 shrink-0 transition-transform" />
    </Accordion.Trigger>
  </Accordion.Header>
  <Accordion.Content class="overflow-hidden data-[state=closed]:animate-none">
    <div class="px-1 py-1">
      {@render children?.()}
    </div>
  </Accordion.Content>
</Accordion.Item>
