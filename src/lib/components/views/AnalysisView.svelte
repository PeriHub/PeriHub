<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  // The image a model's @analysis function returned (run from ViewActions).
  import { Download } from 'lucide-svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { buttonVariants } from '$lib/components/ui/Button.svelte';

  const image = $derived(viewStore.analysisImage);
</script>

<div class="flex h-full flex-col">
  {#if image}
    <div class="border-border flex items-center justify-between gap-2 border-b px-3 py-1.5">
      <h2 class="truncate text-sm font-medium">{image.label}</h2>
      <a
        href={image.url}
        download={image.filename}
        class={buttonVariants({ variant: 'ghost', size: 'sm' })}
        title="Download image"
      >
        <Download class="h-4 w-4" /> Download
      </a>
    </div>
    <div class="flex min-h-0 flex-1 items-center justify-center bg-white p-2">
      <img src={image.url} alt={image.label} class="max-h-full max-w-full object-contain" />
    </div>
  {:else}
    <p class="text-muted-foreground m-auto text-sm">
      Run an analysis from the toolbar to see its result here.
    </p>
  {/if}
</div>
