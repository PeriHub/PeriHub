<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Accordion } from 'bits-ui';
  import { ChevronDown } from 'lucide-svelte';
  import type { Component } from 'svelte';
  import { cn } from '$lib/utils';

  interface Props {
    value: string;
    label: string;
    icon: Component;
    /** Optional required-fields-filled-in indicator (see schemaValidation.ts). Omit to hide. */
    complete?: boolean;
    children?: import('svelte').Snippet;
  }

  let { value, label, icon: Icon, complete, children }: Props = $props();
</script>

<Accordion.Item {value} class="border-border border-b last:border-b-0">
  <Accordion.Header>
    <Accordion.Trigger
      class="hover:bg-muted flex w-full items-center gap-3 px-4 py-3 text-left text-sm font-medium transition-colors [&[data-state=open]>svg]:rotate-180"
    >
      <Icon class="text-primary h-4 w-4 shrink-0" />
      <span class="flex-1">{label}</span>
      {#if complete !== undefined}
        <span
          class={cn('h-2 w-2 shrink-0 rounded-full', complete ? 'bg-success' : 'bg-warning')}
          title={complete ? 'Required fields filled in' : 'Missing required fields'}
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
