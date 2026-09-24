<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { X } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { getVersion } from '$lib/client';
  import type { VersionData } from '$lib/client';

  let { open = $bindable(false) }: { open?: boolean } = $props();

  let version = $state<Partial<VersionData>>({});

  onMount(async () => {
    try {
      version = await getVersion();
    } catch (error) {
      console.error(error);
    }
  });
</script>

<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,32rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <div class="mb-3 flex items-center justify-between">
        <Dialog.Title class="text-lg font-semibold">Settings</Dialog.Title>
        <Dialog.Close class="hover:bg-muted rounded-full p-1.5">
          <X class="h-4 w-4" />
        </Dialog.Close>
      </div>

      <dl class="space-y-2 text-sm">
        <div class="flex justify-between gap-4">
          <dt class="text-muted-foreground">Logged in as</dt>
          <dd class="font-medium">{defaultStore.username}</dd>
        </div>
        {#if defaultStore.trial}
          <div class="bg-warning/20 text-warning-foreground rounded-md px-3 py-2">
            Trial mode enabled — some features are disabled.
          </div>
        {/if}
        {#if defaultStore.cluster}
          <div class="flex justify-between gap-4">
            <dt class="text-muted-foreground">Configured cluster</dt>
            <dd class="font-medium">{defaultStore.cluster}</dd>
          </div>
        {/if}
        <div class="flex justify-between gap-4">
          <dt class="text-muted-foreground">PeriHub version</dt>
          <dd class="font-medium">{version.current ?? '—'} / {version.latest ?? '—'}</dd>
        </div>
        <div class="flex justify-between gap-4">
          <dt class="text-muted-foreground">PeriLab version</dt>
          <dd class="font-medium">
            {version.perilab_current ?? '—'} / {version.perilab_latest ?? '—'}
          </dd>
        </div>
      </dl>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
