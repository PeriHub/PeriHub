<script lang="ts">
  import { Download, Pencil, Trash2, X } from 'lucide-svelte';
  import { onMount, onDestroy } from 'svelte';
  import { Dialog } from 'bits-ui';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { isCurrentShape } from '$lib/utils/model-shape';
  import { downloadFile } from '$lib/utils/download';
  import { api } from '$lib/api/client';
  import {
    cancelRun as cancelRunApi,
    deleteRun as deleteRunApi,
    deleteModelRuns,
    getRunInput,
    getValves,
    listAllRuns
  } from '$lib/client';
  import type { ModelData, RunStatus } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import ProgressBar from '$lib/components/ui/ProgressBar.svelte';

  let loading = $state(false);
  let runs = $state<RunStatus[]>([]);
  let pollTimer: ReturnType<typeof setInterval> | undefined;
  // Run awaiting confirmation in the delete dialog (null = dialog closed).
  let runToDelete = $state<RunStatus | null>(null);
  // Model whose runs and folders await confirmation (null = dialog closed).
  let modelToDelete = $state<string | null>(null);

  // model name -> subname -> runs (newest first, as sorted by GET /jobs/runs)
  const groups = $derived.by(() => {
    const byModel = new Map<string, Map<string, RunStatus[]>>();
    for (const run of runs) {
      let bySubname = byModel.get(run.model_name);
      if (!bySubname) byModel.set(run.model_name, (bySubname = new Map()));
      const list = bySubname.get(run.model_folder_name) ?? [];
      list.push(run);
      bySubname.set(run.model_folder_name, list);
    }
    return byModel;
  });

  const statusClass: Record<string, string> = {
    queued: 'bg-muted text-muted-foreground',
    running: 'bg-primary/20 text-primary',
    done: 'bg-success/20 text-success',
    failed: 'bg-destructive/20 text-destructive',
    cancelled: 'bg-muted text-muted-foreground'
  };

  function isActive(run: RunStatus) {
    return run.status === 'queued' || run.status === 'running';
  }

  function modelTitle(modelName: string) {
    return (
      (modelStore.availableModels.find((m) => m.file === modelName)?.title as string) ?? modelName
    );
  }

  // The run whose log is already being polled by TextActions.svelte - its
  // progress comes from that log directly, which is fresher than this list.
  function isLoggedRun(run: RunStatus) {
    return run.id === defaultStore.status.run_id && isActive(run);
  }

  function progressFor(run: RunStatus) {
    if (isLoggedRun(run) && viewStore.logProgress) {
      return {
        percent: viewStore.logProgress.percent,
        currentStep: viewStore.logProgress.currentStep,
        totalSteps: viewStore.logProgress.totalSteps
      };
    }
    return {
      // PeriLab reports a 0-1 fraction, ProgressBar expects 0-100.
      percent: run.progress == null ? null : run.progress * 100,
      currentStep: run.currentStep,
      totalSteps: run.totalSteps
    };
  }

  async function fetchJobs() {
    loading = true;
    try {
      runs = await listAllRuns();
    } catch (error) {
      notify.apiError(error);
    } finally {
      loading = false;
    }
  }

  // Used by the background poll below - same fetch, without the loading
  // state/toast on every refresh.
  async function refreshJobsSilently() {
    try {
      runs = await listAllRuns();
    } catch {
      // A transient failure here shouldn't interrupt the poll or spam toasts.
    }
  }

  // Points the workspace at this run's model/subname, the same way picking
  // them in the Model expansion does.
  function selectRun(run: RunStatus) {
    modelStore.selectedModel = { title: modelTitle(run.model_name), file: run.model_name };
    localStorage.setItem('selectedModel', JSON.stringify(modelStore.selectedModel));
    modelStore.modelData.model.modelFolderName = run.model_folder_name;
  }

  // Loads everything of the run: its config into the editor, its log, the input deck it was started with and
  // its results.
  async function editRun(run: RunStatus) {
    selectRun(run);
    if (!run.model) {
      notify.negative(`No saved config for ${run.model_name} / ${run.model_folder_name}`);
    } else if (!isCurrentShape(run.model)) {
      notify.negative('Config saved in an older PeriHub format – not supported anymore');
    } else {
      modelStore.modelData = {
        ...$state.snapshot(run.model as ModelData),
        model: { ...(run.model as ModelData).model, modelFolderName: run.model_folder_name }
      };
      modelStore.modelDataFile = run.model_name;
      try {
        modelStore.modelParams = await getValves({ modelName: run.model_name });
        modelStore.modelParamsFile = run.model_name;
      } catch (error) {
        notify.apiError(error);
      }
    }
    if (run.files_missing) {
      notify.warning("This run's files are gone from the server - only its config could be loaded");
      bus.emit('getStatus' as never);
      return;
    }
    // Set the run up front so the log poll targets it right away instead of
    // whatever getStatus returned for the previously selected folder.
    defaultStore.status = { ...defaultStore.status, run_id: run.id, submitted: isActive(run) };
    viewStore.textId = 'log';
    bus.emit('getStatus' as never);
    bus.emit('getJobFolders' as never);
    // The log stream replays a finished run's whole log and then closes, so
    // it serves finished runs too.
    bus.emit('enableWebsocket' as never, { force: true } as never);
    // The deck the run was started with - the folder's own may have been
    // regenerated since.
    getRunInput({ runId: run.id })
      .then((input) => (viewStore.textOutput = input))
      .catch((error) => {
        viewStore.textOutput = '';
        notify.apiError(error);
      });
    if (!isActive(run) && run.results) viewStore.viewId = 'results';
  }

  // The run's whole result folder (results, log, input deck) as a zip.
  let downloading = $state<string | null>(null);

  async function downloadRun(run: RunStatus) {
    downloading = run.id;
    try {
      const response = await api.get('/results/download', {
        params: {
          model_name: run.model_name,
          model_folder_name: run.model_folder_name,
          all_data: true,
          run_id: run.id
        },
        responseType: 'blob'
      });
      downloadFile(
        `${run.model_name}_${run.model_folder_name}_${run.perilab_job_id ?? run.id}.zip`,
        response.data
      );
    } catch {
      notify.negative('Could not download the results');
    }
    downloading = null;
  }

  async function cancelJob(run: RunStatus) {
    loading = true;
    try {
      await cancelRunApi({ runId: run.id });
      notify.positive('Job canceled');
    } catch (error) {
      notify.apiError(error);
    }
    bus.emit('getStatus' as never);
    fetchJobs();
  }

  async function deleteJob() {
    const run = runToDelete;
    runToDelete = null;
    if (!run) return;
    try {
      await deleteRunApi({ runId: run.id });
      runs = runs.filter((r) => r.id !== run.id);
      notify.positive('Job deleted');
    } catch (error) {
      notify.apiError(error);
    }
    bus.emit('getStatus' as never);
    fetchJobs();
  }

  async function deleteModel() {
    const modelName = modelToDelete;
    modelToDelete = null;
    if (!modelName) return;
    try {
      await deleteModelRuns({ modelName });
      runs = runs.filter((r) => r.model_name !== modelName);
      notify.positive(`${modelTitle(modelName)} deleted`);
    } catch (error) {
      notify.apiError(error);
    }
    bus.emit('getStatus' as never);
    fetchJobs();
  }

  // Tabs.Content keeps this view mounted while hidden, so only fetch/poll
  // while the Jobs tab is shown. Not gated on "any active run in the list":
  // a run submitted after the last fetch isn't in `runs` yet (submitting
  // switches to this tab, which refetches).
  const shown = () => viewStore.viewId === 'jobs';

  $effect(() => {
    if (shown()) fetchJobs();
  });

  onMount(() => {
    bus.on('resetData', fetchJobs);
    bus.on('getJobs' as never, fetchJobs);

    pollTimer = setInterval(() => {
      if (shown() && !document.hidden) refreshJobsSilently();
    }, 3000);

    return () => {
      bus.off('resetData', fetchJobs);
      bus.off('getJobs' as never, fetchJobs);
    };
  });

  onDestroy(() => clearInterval(pollTimer));
</script>

<div class="space-y-4 overflow-x-auto p-3 text-sm">
  {#if loading && runs.length === 0}
    <p class="text-muted-foreground py-6 text-center">Loading…</p>
  {:else if runs.length === 0}
    <p class="text-muted-foreground py-6 text-center">No jobs submitted yet</p>
  {:else}
    {#each [...groups] as [modelName, bySubname] (modelName)}
      <section>
        <div class="flex items-center justify-between">
          <h3 class="text-base font-semibold">{modelTitle(modelName)}</h3>
          <Button
            variant="ghost"
            size="sm"
            disabled={[...bySubname.values()].flat().some(isActive)}
            onclick={() => (modelToDelete = modelName)}
            title="Delete all jobs and files of this model"
          >
            <Trash2 class="h-4 w-4" /> Delete all
          </Button>
        </div>
        {#each [...bySubname] as [subname, subRuns] (subname)}
          <div class="mt-2 pl-3">
            <h4 class="text-muted-foreground font-medium">{subname}</h4>
            <table class="mt-1 w-full text-left">
              <thead class="border-border text-muted-foreground border-b text-xs">
                <tr>
                  <th class="px-3 py-1 font-medium">Status</th>
                  <th class="px-3 py-1 font-medium">Progress</th>
                  <th class="px-3 py-1 font-medium">Job ID</th>
                  <th class="px-3 py-1 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {#each subRuns as run (run.id)}
                  <tr class="border-border hover:bg-muted/50 border-b">
                    <td class="w-28 px-3 py-2">
                      <span
                        class="rounded-full px-2 py-0.5 text-xs font-medium {statusClass[
                          run.status
                        ] ?? 'bg-muted text-muted-foreground'}"
                        title={run.error ?? undefined}
                      >
                        {run.status}
                      </span>
                      {#if run.files_missing}
                        <span
                          class="ml-1 rounded-full bg-amber-500/15 px-2 py-0.5 text-xs font-medium whitespace-nowrap text-amber-600"
                          title="This run's files no longer exist on the server - they were deleted, moved or cleaned up. Its log and results can't be loaded; delete the run to clean up."
                        >
                          files missing
                        </span>
                      {/if}
                    </td>
                    <td class="w-40 px-3 py-2">
                      {#if isActive(run)}
                        {@const p = progressFor(run)}
                        <ProgressBar
                          value={p.percent}
                          label={p.currentStep && p.totalSteps
                            ? `${p.currentStep} / ${p.totalSteps}`
                            : ''}
                          class="w-32"
                        />
                      {:else if run.status === 'done'}
                        <span class="text-xs">100%</span>
                      {:else}
                        <span class="text-muted-foreground text-xs">–</span>
                      {/if}
                    </td>
                    <td class="px-3 py-2 font-mono text-xs" title={`Run ${run.id}`}>
                      {run.perilab_job_id ?? '–'}
                    </td>
                    <td class="px-3 py-2 text-right whitespace-nowrap">
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={run.files_missing && !run.model}
                        onclick={() => editRun(run)}
                        title="Open config, log, input and results"
                      >
                        <Pencil class="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={isActive(run) ||
                          run.files_missing ||
                          !(run.results || run.csvResults) ||
                          downloading === run.id}
                        onclick={() => downloadRun(run)}
                        title="Download results"
                      >
                        <Download class="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={!isActive(run)}
                        onclick={() => cancelJob(run)}
                        title="Cancel"
                      >
                        <X class="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={isActive(run)}
                        onclick={() => (runToDelete = run)}
                        title={isActive(run) ? 'Cancel the job before deleting it' : 'Delete'}
                      >
                        <Trash2 class="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/each}
      </section>
    {/each}
  {/if}
</div>

<Dialog.Root
  open={runToDelete !== null}
  onOpenChange={(open) => {
    if (!open) runToDelete = null;
  }}
>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,32rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-2 text-lg font-semibold">Delete Job</Dialog.Title>
      <p class="text-muted-foreground text-sm">
        Delete job <span class="font-mono">{runToDelete?.perilab_job_id ?? runToDelete?.id}</span>
        of {runToDelete?.model_name} / {runToDelete?.model_folder_name}? Its log and result files
        are removed permanently. The model's input files are kept.
      </p>
      <div class="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (runToDelete = null)}>Cancel</Button>
        <Button variant="destructive" onclick={deleteJob}>Delete</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root
  open={modelToDelete !== null}
  onOpenChange={(open) => {
    if (!open) modelToDelete = null;
  }}
>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,32rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-2 text-lg font-semibold">Delete all jobs</Dialog.Title>
      <p class="text-muted-foreground text-sm">
        Delete every job of {modelToDelete ? modelTitle(modelToDelete) : ''}? Their logs and result
        files, and the model's input files on the server, are removed permanently.
      </p>
      <div class="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (modelToDelete = null)}>Cancel</Button>
        <Button variant="destructive" onclick={deleteModel}>Delete</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
