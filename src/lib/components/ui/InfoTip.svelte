<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<!--
  Info icon with a spec-card tooltip: the input-deck key as written in the YAML, a description, and short
  facts (range, default, quantity) in the code face. The text is also rendered sr-only under `id` so a field
  can point aria-describedby at it - the tooltip itself only exists in the DOM while open.
-->
<script lang="ts">
  import { Tooltip } from 'bits-ui';
  import { Info } from 'lucide-svelte';

  interface Props {
    /** Heading, e.g. the YAML key ("Yield Stress"). */
    title: string;
    text?: string;
    facts?: string[];
    /** Id of the sr-only description, for aria-describedby on the field. */
    id?: string;
  }

  let { title, text = '', facts = [], id }: Props = $props();
</script>

<Tooltip.Provider delayDuration={200}>
  <Tooltip.Root>
    <Tooltip.Trigger
      type="button"
      class="text-muted-foreground hover:text-foreground focus-visible:ring-ring inline-flex h-4 w-4 cursor-help items-center justify-center rounded-full transition-colors focus-visible:ring-2 focus-visible:outline-none"
      aria-label="About {title}"
    >
      <Info class="h-3.5 w-3.5" aria-hidden="true" />
    </Tooltip.Trigger>
    <Tooltip.Portal>
      <Tooltip.Content
        side="top"
        sideOffset={6}
        collisionPadding={8}
        class="bg-foreground text-background data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=delayed-open]:animate-in data-[state=delayed-open]:fade-in-0 data-[state=delayed-open]:zoom-in-95 data-[state=instant-open]:animate-in data-[state=instant-open]:fade-in-0 data-[side=bottom]:slide-in-from-top-1 data-[side=top]:slide-in-from-bottom-1 z-50 max-w-72 rounded-lg px-3 py-2.5 shadow-lg motion-reduce:animate-none"
      >
        <p class="font-code text-[11px] tracking-tight opacity-70">{title}:</p>
        {#if text}
          <p class="mt-1 text-[13px] leading-snug">{text}</p>
        {/if}
        {#if facts.length}
          <ul class="mt-2 flex flex-wrap gap-1" aria-label="Facts">
            {#each facts as fact (fact)}
              <li class="bg-background/15 font-code rounded px-1.5 py-0.5 text-[11px] leading-none">
                {fact}
              </li>
            {/each}
          </ul>
        {/if}
        <Tooltip.Arrow class="text-foreground" />
      </Tooltip.Content>
    </Tooltip.Portal>
  </Tooltip.Root>
</Tooltip.Provider>
{#if id}
  <span {id} class="sr-only">{[text, ...facts].filter(Boolean).join('. ')}</span>
{/if}
