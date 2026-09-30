<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { RefreshCw } from 'lucide-svelte';
  import { adminGetUsage, adminListJobs, cancelRun } from '$lib/client';
  import type { AdminJob, UsageSummary } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import { notify } from '$lib/utils/notify';

  let activeOnly = $state(true);
  let jobs = $state<AdminJob[]>([]);
  let usage = $state<UsageSummary | null>(null);

  async function load(onlyActive: boolean) {
    try {
      [jobs, usage] = await Promise.all([
        adminListJobs({ activeOnly: onlyActive }),
        adminGetUsage()
      ]);
    } catch (e) {
      notify.apiError(e);
    }
  }

  async function cancel(job: AdminJob) {
    try {
      await cancelRun({ runId: job.id });
      notify.positive(`Cancelled ${job.model_name} of ${job.owner}`);
    } catch (e) {
      notify.apiError(e);
    }
    await load(activeOnly);
  }

  const isActive = (job: AdminJob) => job.status === 'queued' || job.status === 'running';
  const perUser = $derived(
    Object.entries(usage?.jobs_per_user ?? {}).sort(([, a], [, b]) => Number(b) - Number(a))
  );

  $effect(() => {
    load(activeOnly);
  });
</script>

<div class="flex items-center justify-between gap-4">
  <Toggle label="Running only" bind:checked={activeOnly} />
  <Button variant="outline" size="sm" onclick={() => load(activeOnly)}>
    <RefreshCw /> Refresh
  </Button>
</div>

<div class="mt-4 overflow-x-auto">
  <table class="w-full text-left text-sm">
    <thead class="text-muted-foreground border-border border-b">
      <tr>
        <th class="py-2 pr-4 font-medium">User</th>
        <th class="py-2 pr-4 font-medium">Model</th>
        <th class="py-2 pr-4 font-medium">Status</th>
        <th class="py-2 pr-4 font-medium">Submitted</th>
        <th class="py-2"></th>
      </tr>
    </thead>
    <tbody>
      {#each jobs as job (job.id)}
        <tr class="border-border border-b last:border-0">
          <td class="py-2 pr-4">{job.owner}</td>
          <td class="py-2 pr-4">{job.model_name} / {job.model_folder_name}</td>
          <td class="py-2 pr-4">{job.status}</td>
          <td class="py-2 pr-4">{new Date(job.submitted_at).toLocaleString()}</td>
          <td class="py-2 text-right">
            {#if isActive(job)}
              <Button variant="destructive" size="sm" onclick={() => cancel(job)}>Cancel</Button>
            {/if}
          </td>
        </tr>
      {:else}
        <tr><td colspan="5" class="text-muted-foreground py-4">No jobs.</td></tr>
      {/each}
    </tbody>
  </table>
</div>

<h2 class="mt-10 text-lg font-semibold">Usage</h2>
{#if usage}
  <p class="text-muted-foreground mt-1 text-sm">
    {usage.total_jobs_submitted} jobs submitted, {usage.total_jobs_cancelled} cancelled.
  </p>
  <table class="mt-3 w-full max-w-md text-left text-sm">
    <thead class="text-muted-foreground border-border border-b">
      <tr>
        <th class="py-2 pr-4 font-medium">User</th>
        <th class="py-2 text-right font-medium">Jobs</th>
      </tr>
    </thead>
    <tbody>
      {#each perUser as [user, count] (user)}
        <tr class="border-border border-b last:border-0">
          <td class="py-2 pr-4">{user}</td>
          <td class="py-2 text-right">{count}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}
