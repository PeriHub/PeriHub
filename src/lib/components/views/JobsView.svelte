<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { X } from 'lucide-svelte';
  import { onMount, onDestroy } from 'svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { cancelJob as cancelJobApi, getJobs } from '$lib/client';
  import type { Jobs, ModelData } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import ProgressBar from '$lib/components/ui/ProgressBar.svelte';

  let loading = $state(false);
  let rows = $state<Jobs[]>([]);
  let pollTimer: ReturnType<typeof setInterval> | undefined;

  async function fetchJobs() {
    loading = true;
    try {
      rows = await getJobs({
        modelName: modelStore.selectedModel.file,
        sbatch: modelStore.modelData.job.sbatch
      });
      notify.info('Jobs found');
    } catch (error) {
      notify.apiError(error);
    } finally {
      loading = false;
    }
  }

  // Used by the background poll below - same fetch, without the toast on
  // every refresh (that would fire every few seconds while a job runs).
  async function refreshJobsSilently() {
    try {
      rows = await getJobs({
        modelName: modelStore.selectedModel.file,
        sbatch: modelStore.modelData.job.sbatch
      });
    } catch {
      // A transient failure here shouldn't interrupt the poll or spam toasts.
    }
  }

  async function cancelJob(row: Jobs) {
    loading = true;
    try {
      await cancelJobApi({
        modelName: row.name,
        modelFolderName: row.sub_name,
        cluster: row.cluster,
        sbatch: true
      });
      notify.positive('Job canceled');
    } catch {
      notify.negative('Failed');
    }
    bus.emit('resetData');
    fetchJobs();
  }

  function onRowClick(row: Jobs) {
    modelStore.modelData = row.model as ModelData;
  }

  onMount(() => {
    fetchJobs();
    bus.on('resetData', fetchJobs);
    bus.on('getJobs' as never, fetchJobs);

    // Keep progress bars live for any job that's running but has no results
    // yet, without the user needing to manually refresh.
    pollTimer = setInterval(() => {
      const hasRunningJob = rows.some((row) => row.submitted && !row.results);
      if (hasRunningJob) refreshJobsSilently();
    }, 3000);

    return () => {
      bus.off('resetData', fetchJobs);
      bus.off('getJobs' as never, fetchJobs);
    };
  });

  onDestroy(() => clearInterval(pollTimer));
</script>

<div class="overflow-x-auto">
  <table class="w-full text-left text-sm">
    <thead class="border-b border-border text-muted-foreground">
      <tr>
        <th class="px-3 py-2 font-medium">Model Name</th>
        <th class="px-3 py-2 font-medium">Cluster</th>
        <th class="px-3 py-2 font-medium">Submitted</th>
        <th class="px-3 py-2 font-medium">Progress</th>
        <th class="px-3 py-2 font-medium">Results</th>
        <th class="px-3 py-2 font-medium"></th>
      </tr>
    </thead>
    <tbody>
      {#if loading}
        <tr><td colspan="6" class="px-3 py-6 text-center text-muted-foreground">Loading…</td></tr>
      {:else if rows.length === 0}
        <tr><td colspan="6" class="px-3 py-6 text-center text-muted-foreground">No jobs found</td></tr>
      {:else}
        {#each rows as row (row.id)}
          <tr class="border-b border-border hover:bg-muted/50">
            <td class="cursor-pointer px-3 py-2" onclick={() => onRowClick(row)}>
              {row.name} ({row.sub_name})
            </td>
            <td class="px-3 py-2">
              <span class="rounded-full bg-accent/20 px-2 py-0.5 text-xs font-medium text-accent-foreground">
                {row.cluster}
              </span>
            </td>
            <td class="px-3 py-2">
              <span
                class="rounded-full px-2 py-0.5 text-xs font-medium {row.submitted
                  ? 'bg-success/20 text-success'
                  : 'bg-destructive/20 text-destructive'}"
              >
                {row.submitted}
              </span>
            </td>
            <td class="px-3 py-2">
              {#if row.submitted && !row.results}
                <ProgressBar
                  value={row.progress}
                  label={row.currentStep && row.totalSteps ? `${row.currentStep} / ${row.totalSteps}` : ''}
                  class="w-32"
                />
              {:else}
                <span class="text-xs text-muted-foreground">–</span>
              {/if}
            </td>
            <td class="px-3 py-2">
              <span
                class="rounded-full px-2 py-0.5 text-xs font-medium {row.results
                  ? 'bg-success/20 text-success'
                  : 'bg-destructive/20 text-destructive'}"
              >
                {row.results}
              </span>
            </td>
            <td class="px-3 py-2 text-right">
              <Button
                variant="ghost"
                size="icon"
                disabled={!row.submitted}
                onclick={() => cancelJob(row)}
                title="Cancel job"
              >
                <X class="h-4 w-4" />
              </Button>
            </td>
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
</div>
