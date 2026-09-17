<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { X, RefreshCw } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { getLicenseStatus, refreshLicense } from '$lib/client';
  import type { LicenseStatus } from '$lib/client';
  import { notify } from '$lib/utils/notify';
  import Button from '$lib/components/ui/Button.svelte';

  let { open = $bindable(false) }: { open?: boolean } = $props();

  let status = $state<LicenseStatus | null>(null);
  let loading = $state(false);

  async function load() {
    loading = true;
    try {
      status = await getLicenseStatus();
    } catch (error) {
      notify.apiError(error);
    }
    loading = false;
  }

  async function forceRefresh() {
    loading = true;
    try {
      status = await refreshLicense();
      notify.positive('License status refreshed');
    } catch (error) {
      notify.apiError(error);
    }
    loading = false;
  }

  onMount(load);
</script>

<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 z-50 w-[min(92vw,28rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-5 shadow-lg"
    >
      <div class="mb-3 flex items-center justify-between">
        <Dialog.Title class="text-lg font-semibold">Plan &amp; Licensing</Dialog.Title>
        <Dialog.Close class="rounded-full p-1.5 hover:bg-muted" aria-label="Close">
          <X class="h-4 w-4" />
        </Dialog.Close>
      </div>

      {#if status}
        <dl class="space-y-2 text-sm">
          <div class="flex justify-between gap-4">
            <dt class="text-muted-foreground">Current plan</dt>
            <dd class="font-medium capitalize">{status.plan}</dd>
          </div>
          {#if status.seats != null}
            <div class="flex justify-between gap-4">
              <dt class="text-muted-foreground">Seats</dt>
              <dd class="font-medium">{status.seats}</dd>
            </div>
          {/if}
          {#if status.expires_at}
            <div class="flex justify-between gap-4">
              <dt class="text-muted-foreground">Expires</dt>
              <dd class="font-medium">{new Date(status.expires_at).toLocaleDateString()}</dd>
            </div>
          {/if}
          {#if status.features.length > 0}
            <div>
              <dt class="mb-1 text-muted-foreground">Unlocked features</dt>
              <dd class="flex flex-wrap gap-1">
                {#each status.features as feature, featureIdx (feature ?? featureIdx)}
                  <span class="rounded-full bg-accent/20 px-2 py-0.5 text-xs font-medium">{feature}</span>
                {/each}
              </dd>
            </div>
          {/if}
          {#if !status.license_server_configured}
            <p class="rounded-md bg-muted px-3 py-2 text-muted-foreground">
              No license server is configured for this instance — every open-core feature is
              available by default.
            </p>
          {/if}
        </dl>

        <Button
          variant="outline"
          size="sm"
          class="mt-4 w-full"
          disabled={loading}
          onclick={forceRefresh}
        >
          <RefreshCw class="h-4 w-4" /> Refresh status
        </Button>
      {:else}
        <p class="text-sm text-muted-foreground">Loading…</p>
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
