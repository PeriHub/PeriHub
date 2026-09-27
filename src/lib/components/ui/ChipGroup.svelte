<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { cn } from '$lib/utils';

  // Multi-pick as toggle chips instead of a native <select multiple>, which
  // needs Ctrl-click and hides what is selected once the list scrolls.
  type Option = string | number;

  interface Props {
    value?: Option[] | null;
    options: readonly Option[];
    ariaLabel: string;
  }

  let { value = $bindable(), options, ariaLabel }: Props = $props();

  function toggle(option: Option) {
    const current = value ?? [];
    value = current.includes(option) ? current.filter((v) => v !== option) : [...current, option];
  }
</script>

<div role="group" aria-label={ariaLabel} class="flex flex-wrap gap-1.5">
  {#each options as option, i (i)}
    {@const selected = value?.includes(option) ?? false}
    <button
      type="button"
      aria-pressed={selected}
      onclick={() => toggle(option)}
      class={cn(
        'focus-visible:ring-ring h-7 rounded-full border px-3 text-xs transition-colors focus-visible:ring-2 focus-visible:outline-none',
        selected
          ? 'border-primary bg-primary text-primary-foreground'
          : 'border-input bg-background hover:bg-muted'
      )}
    >
      {option}
    </button>
  {:else}
    <span class="text-muted-foreground text-xs">Nothing to choose from yet.</span>
  {/each}
</div>
