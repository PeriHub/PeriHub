<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { LogOut, X } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { authStore } from '$lib/stores/auth-store.svelte';
  import { publicConfig } from '$lib/config';
  import { leaveGuestSession } from '$lib/auth/oauth';
  import {
    getCurrentUserInfo,
    getLicenseStatus,
    getMyUsage,
    getVersion,
    listAllRuns
  } from '$lib/client';
  import type { LicenseStatus, MeResponse, UsageSummary, VersionData } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';

  let { open = $bindable(false) }: { open?: boolean } = $props();

  let profile = $state<MeResponse | null>(null);
  let usage = $state<UsageSummary | null>(null);
  let license = $state<LicenseStatus | null>(null);
  let version = $state<Partial<VersionData>>({});
  let activeJobs = $state<number | null>(null);

  const providerLabel: Record<string, string> = {
    local: 'Email & password',
    oauth: 'Single sign-on'
  };

  // Everything here can change while the app is open (jobs, plan, a new
  // release), so reload on every open rather than once on mount. Each
  // request is independent - one failing (e.g. an endpoint that is
  // not available for guests) just leaves its section empty.
  async function load() {
    const [me, myUsage, licenseStatus, versionData, runs] = await Promise.allSettled([
      authStore.authenticated ? getCurrentUserInfo() : Promise.reject(),
      getMyUsage(),
      getLicenseStatus(),
      getVersion(),
      authStore.authenticated ? listAllRuns() : Promise.reject()
    ]);
    profile = me.status === 'fulfilled' ? me.value : null;
    usage = myUsage.status === 'fulfilled' ? myUsage.value : null;
    license = licenseStatus.status === 'fulfilled' ? licenseStatus.value : null;
    if (versionData.status === 'fulfilled') version = versionData.value;
    activeJobs =
      runs.status === 'fulfilled'
        ? runs.value.filter((run) => run.status === 'queued' || run.status === 'running').length
        : null;
  }

  $effect(() => {
    if (open) load();
  });

  // Release tags carry a "v" prefix ("v3.2.3") and nightlies can be ahead
  // of the latest release, so compare numerically rather than by equality.
  function isOutdated(current?: string, latest?: string) {
    if (!current || !latest) return false;
    const parse = (v: string) =>
      v
        .replace(/^v/i, '')
        .split('.')
        .map((part) => parseInt(part, 10) || 0);
    const [a, b] = [parse(current), parse(latest)];
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      if ((a[i] ?? 0) !== (b[i] ?? 0)) return (a[i] ?? 0) < (b[i] ?? 0);
    }
    return false;
  }
</script>

{#snippet versionRow(label: string, current?: string, latest?: string)}
  <div class="flex items-center justify-between gap-4">
    <dt class="text-muted-foreground">{label}</dt>
    <dd class="flex items-center gap-2 font-medium">
      {current ?? '—'}
      {#if isOutdated(current, latest)}
        <span
          class="bg-warning/20 text-warning-foreground rounded-full px-2 py-0.5 text-xs"
          title={`Latest: ${latest}`}
        >
          Update available: {latest}
        </span>
      {:else if current && latest}
        <span class="bg-success/20 text-success rounded-full px-2 py-0.5 text-xs">Up to date</span>
      {/if}
    </dd>
  </div>
{/snippet}

{#snippet statRow(label: string, value: number | string | null | undefined)}
  <div class="flex justify-between gap-4">
    <dt class="text-muted-foreground">{label}</dt>
    <dd class="font-medium">{value ?? '—'}</dd>
  </div>
{/snippet}

<Dialog.Root bind:open>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,32rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <div class="mb-4 flex items-center justify-between">
        <Dialog.Title class="text-lg font-semibold">Settings</Dialog.Title>
        <Dialog.Close class="hover:bg-muted rounded-full p-1.5">
          <X class="h-4 w-4" />
        </Dialog.Close>
      </div>

      <!-- Profile -->
      <div class="flex items-center gap-3">
        <div
          class="bg-primary/15 text-primary flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-full text-base font-semibold"
        >
          {#if defaultStore.useGravatar}
            <img
              src={defaultStore.gravatarUrl}
              alt="User avatar"
              class="h-full w-full object-cover"
            />
          {:else}
            {defaultStore.gravatarUrl || defaultStore.username.charAt(0).toUpperCase()}
          {/if}
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <span class="truncate font-medium">
              {profile?.display_name ?? defaultStore.username}
            </span>
            {#if profile}
              <span class="bg-muted text-muted-foreground rounded-full px-2 py-0.5 text-xs">
                {profile.role}
              </span>
            {/if}
          </div>
          {#if profile?.email}
            <div class="text-muted-foreground truncate text-sm">{profile.email}</div>
          {/if}
          {#if profile}
            <div class="text-muted-foreground text-xs">
              {providerLabel[profile.auth_provider] ?? profile.auth_provider}
            </div>
          {/if}
        </div>
      </div>

      {#if authStore.isGuest}
        <div class="bg-warning/20 text-warning-foreground mt-3 rounded-md px-3 py-2 text-sm">
          <p>
            You're using PeriHub as a guest: built-in models only, no uploads, and your data is
            deleted after {publicConfig.guestLimits?.retention_days ?? 1} day(s).
          </p>
          {#if publicConfig.guestLimits}
            <p class="mt-1 text-xs">
              Limits: {publicConfig.guestLimits.max_nodes} nodes, {publicConfig.guestLimits
                .max_output_steps} output steps, {publicConfig.guestLimits.max_job_minutes} min per job,
              {publicConfig.guestLimits.max_concurrent_jobs} job(s) at a time.
            </p>
          {/if}
          <Button size="sm" variant="outline" class="mt-2" onclick={leaveGuestSession}
            >Log in</Button
          >
        </div>
      {/if}

      <!-- Usage & plan -->
      <section class="border-border mt-4 border-t pt-3">
        <h3 class="text-muted-foreground mb-2 text-xs font-semibold tracking-wide uppercase">
          Usage & plan
        </h3>
        <dl class="space-y-1.5 text-sm">
          {#if license}
            <div class="flex justify-between gap-4">
              <dt class="text-muted-foreground">Plan</dt>
              <dd class="font-medium capitalize">
                {license.plan}
                {#if license.expires_at}
                  <span class="text-muted-foreground text-xs font-normal normal-case">
                    (until {new Date(license.expires_at).toLocaleDateString()})
                  </span>
                {/if}
              </dd>
            </div>
          {/if}
          {@render statRow('Active jobs', activeJobs)}
          {@render statRow('Jobs submitted', usage?.total_jobs_submitted)}
          {@render statRow('Jobs cancelled', usage?.total_jobs_cancelled)}
          {#if usage?.jobs_per_model && Object.keys(usage.jobs_per_model).length}
            <div class="flex justify-between gap-4">
              <dt class="text-muted-foreground">Most used model</dt>
              <dd class="font-medium">
                {Object.entries(usage.jobs_per_model).sort(
                  ([, a], [, b]) => Number(b) - Number(a)
                )[0][0]}
              </dd>
            </div>
          {/if}
        </dl>
      </section>

      <!-- System -->
      <section class="border-border mt-4 border-t pt-3">
        <h3 class="text-muted-foreground mb-2 text-xs font-semibold tracking-wide uppercase">
          System
        </h3>
        <dl class="space-y-1.5 text-sm">
          {@render versionRow('PeriHub', version.current, version.latest)}
          {@render versionRow('PeriLab', version.perilab_current, version.perilab_latest)}
        </dl>
      </section>

      {#if authStore.authenticated && !authStore.isGuest}
        <div class="border-border mt-4 flex justify-end border-t pt-4">
          <Button variant="outline" onclick={() => authStore.logout()}>
            <LogOut class="h-4 w-4" />
            Log out
          </Button>
        </div>
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
