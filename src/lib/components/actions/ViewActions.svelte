<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onDestroy } from 'svelte';
  import { Dialog } from 'bits-ui';
  import { Play, X, Download, Eye, LineChart, Trash2, Check, ImageIcon } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { downloadFile } from '$lib/utils/download';
  import { api } from '$lib/api/client';
  import {
    getCurrentEnergy,
    runModel as runModelApi,
    cancelRun as cancelRunApi,
    getPlot,
    getAnalyses,
    deleteModel as deleteModelApi,
    deleteUserData as deleteUserDataApi,
    type AnalysisInfo,
    type Valve
  } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import RenewableView from '$lib/components/views/RenewableView.svelte';

  const PALETTE = [
    '#00658b',
    '#d2ae3d',
    '#82a043',
    '#666666',
    '#3b98cb',
    '#f2cd51',
    '#a6bf51',
    '#858585'
  ];

  const modelData = $derived(modelStore.modelData);
  const outputs = $derived(modelData.outputs ?? []);
  const status = $derived(defaultStore.status);
  // True as soon as a job has been submitted for this model, even before
  // the pid.txt-backed `status.submitted` flag catches up on the next
  // getStatus poll (up to 5s later) - driven by the same logStatus the Log
  // tab uses, so Cancel becomes available immediately, including during
  // the "waiting for the log file" window right after submit.
  const jobActive = $derived(
    status.submitted || viewStore.logStatus === 'waiting' || viewStore.logStatus === 'streaming'
  );

  type StepState = 'done' | 'active' | 'todo';
  const hasResults = $derived(Boolean(status.results || status.csvResults));
  const meshReady = $derived(Boolean(status.created && status.meshfileExist));
  const steps = $derived.by(() => {
    const configured = viewStore.setupComplete;
    const state = (done: boolean, active: boolean): StepState =>
      done ? 'done' : active ? 'active' : 'todo';
    return [
      { label: 'Configure', state: state(configured, true), hint: 'fill in required fields' },
      { label: 'Mesh', state: state(meshReady, configured), hint: 'generate the mesh' },
      {
        label: 'Run',
        state: state(hasResults && !jobActive, jobActive || (meshReady && !hasResults)),
        hint: jobActive ? 'running' : 'ready to run'
      },
      { label: 'Results', state: state(hasResults && !jobActive, false), hint: '' }
    ];
  });

  let submitLoading = $state(false);
  let resultsLoading = $state(false);
  let timer: ReturnType<typeof setInterval> | null = null;
  let intervalCount = 0;
  // Bridges the gap between submit and the next getStatus poll (up to 5s):
  // status.run_id lags behind by one poll, so cancelling right after
  // submit would otherwise have nothing to target yet.
  let lastSubmittedRunId = $state<string | null>(null);
  const activeRunId = $derived(status.run_id ?? lastSubmittedRunId);

  let dialogEnergySavings = $state(false);
  let dialogDownload = $state(false);
  let dialogPlot = $state(false);
  let dialogDelete = $state(false);
  let dialogConfirm = $state<null | 'model' | 'localSettings' | 'userData'>(null);

  let energyPercent = $state(0);
  // let plotVariables = $state<string[]>([]);
  let plotOutput = $state('');

  async function checkEnergy() {
    if (defaultStore.saveEnergy) {
      try {
        energyPercent = await getCurrentEnergy();
      } catch {
        notify.negative('Failed to check renewable energy share');
      }
      dialogEnergySavings = true;
    } else {
      await _runModel();
    }
  }

  async function _runModel(jobIds: string | null = null) {
    submitLoading = true;
    viewStore.textLoading = true;

    try {
      const response = await runModelApi({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName,
        verbose: modelData.job.verbose,
        jobIds,
        requestBody: modelData
      });
      lastSubmittedRunId = (response as { run_id: string }).run_id;
      // The log poll (TextActions.svelte) keys off status.run_id, which
      // would otherwise still point at the previous run until the next
      // getStatus call.
      defaultStore.status = { ...status, run_id: lastSubmittedRunId, submitted: true };
      notify.positive('Job submitted');
      viewStore.textId = 'log';
      viewStore.viewId = 'jobs';
      bus.emit('getJobs' as never);

      // Open the log stream right away instead of guessing a fixed delay:
      // the backend now waits for the .log file to appear on its own and
      // reports "waiting" over the socket, so the user sees progress
      // immediately instead of a blank tab for the next 20+ seconds.
      bus.emit('enableWebsocket' as never, { force: true } as never);

      // The submit request itself is done - jobActive (driven by
      // viewStore.logStatus, set above) now shows the Cancel button, and it
      // should be usable right away rather than staying disabled until the
      // slower getStatus poll below confirms pid.txt exists.
      submitLoading = false;

      // Separately, keep polling getStatus so `submitted` (pid.txt present)
      // and the other status flags used elsewhere in the UI stay current.
      // This no longer gates the log view or the Cancel button.
      intervalCount = 0;
      timer = setInterval(checkStatus, 5000);
    } catch (error) {
      notify.apiError(error);
      submitLoading = false;
      viewStore.textLoading = false;
    }
  }

  async function checkStatus() {
    bus.emit('getStatus' as never);
    intervalCount += 1;

    if (status.submitted) {
      if (timer) clearInterval(timer);
      return;
    }

    // A generous cap (~2 minutes) before giving up on polling the
    // "submitted" flag - the log stream itself already reports if the job
    // never actually started (via its own, longer timeout).
    if (intervalCount > 24) {
      if (timer) clearInterval(timer);
    }
  }

  async function cancelJob() {
    if (!activeRunId) {
      notify.negative('No active run to cancel');
      return;
    }
    submitLoading = true;
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    try {
      await cancelRunApi({ runId: activeRunId });
      notify.positive('Job canceled');
      bus.emit('stopWebsocket' as never);
    } catch {
      notify.negative('Could not cancel the job');
    }
    lastSubmittedRunId = null;
    bus.emit('getStatus' as never);
    submitLoading = false;
  }

  async function saveResults(allData: boolean) {
    resultsLoading = true;
    dialogDownload = false;
    try {
      const params = {
        model_name: modelStore.selectedModel.file,
        model_folder_name: modelData.model.modelFolderName,
        output: plotOutput,
        all_data: allData,
        run_id: status.run_id
      };
      const response = await api.get('/results/getResults', { params, responseType: 'blob' });
      const filename = allData
        ? `${modelStore.selectedModel.file}_${modelData.model.modelFolderName}.zip`
        : `${modelStore.selectedModel.file}_${modelData.model.modelFolderName}_${outputs[0]?.name}.e`;
      downloadFile(filename, response.data);
    } catch {
      notify.negative('Could not download the results');
    }
    resultsLoading = false;
  }

  function updatePlotVariables() {
    // plotVariables = [...(modelData.computes ?? []).map((c) => c.name), 'Time'];
    plotOutput = outputs[0]?.name ?? '';
    dialogPlot = true;
  }

  async function _getPlot() {
    viewStore.modelLoading = true;
    dialogPlot = false;
    try {
      const plotRawData = (await getPlot({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName,
        output: plotOutput,
        deviationsEnabled: modelData.deviations?.enabled ?? false,
        runId: status.run_id
      })) as Record<string, (number | string)[]>;

      notify.positive('Plot loaded');

      // The API can hand back numeric-looking values as strings (e.g. raw
      // CSV cells); coerce explicitly rather than trusting the type cast
      // above, since a chart's axis domain needs real numbers to compare
      // correctly - comparing strings numerically-but-not ("10" < "9")
      // silently produces a corrupted axis range that "reset zoom" can't fix.
      const toNumbers = (values: (number | string)[]): number[] =>
        values.map((v) => (typeof v === 'number' ? v : Number(v)));

      const firstProperty = Object.keys(plotRawData)[0]!;
      const xValues = toNumbers(plotRawData[firstProperty]!);
      const tempData = Object.entries(plotRawData)
        .filter(([name]) => name !== firstProperty)
        .map(([name, values], i) => ({
          name,
          x: xValues,
          y: toNumbers(values),
          type: 'scatter',
          marker: { color: PALETTE[i % PALETTE.length] }
        }));

      viewStore.plotData = tempData;
      viewStore.plotLayout = {
        ...viewStore.plotLayout,
        xaxis: { ...viewStore.plotLayout.xaxis, title: firstProperty }
      };
      viewStore.viewId = 'plotly';
    } catch (error) {
      console.error(error);
      notify.negative('Could not load the plot');
    }
    viewStore.modelLoading = false;
  }

  // The model's @analysis functions (result images), refetched when the model changes.
  let analyses = $state<AnalysisInfo[]>([]);
  let dialogAnalysis = $state(false);
  let analysisId = $state('');
  let analysisValues = $state<Record<string, string | number | boolean>>({});
  let analysisLoading = $state(false);
  const selectedAnalysis = $derived(analyses.find((a) => a.id === analysisId));

  $effect(() => {
    const modelName = modelStore.selectedModel.file;
    getAnalyses({ modelName })
      .then((list) => {
        if (modelStore.selectedModel.file === modelName) analyses = list;
      })
      .catch(() => (analyses = []));
  });

  /** "computes" / "outputs" mean: the names configured in this model. */
  function analysisOptions(param: Valve): string[] {
    if (Array.isArray(param.options)) return param.options;
    if (param.options === 'computes') return (modelData.computes ?? []).map((c) => c.name ?? '');
    if (param.options === 'outputs') return outputs.map((o) => o.name ?? '');
    return param.options ? [param.options] : [];
  }

  function selectAnalysis(id: string) {
    analysisId = id;
    const analysis = analyses.find((a) => a.id === id);
    analysisValues = Object.fromEntries((analysis?.params ?? []).map((p) => [p.name, p.value]));
  }

  function openAnalysisDialog() {
    if (!analyses.some((a) => a.id === analysisId)) selectAnalysis(analyses[0]?.id ?? '');
    dialogAnalysis = true;
  }

  async function runAnalysis() {
    const analysis = selectedAnalysis;
    if (!analysis) return;
    dialogAnalysis = false;
    analysisLoading = true;
    try {
      const response = await api.post(
        '/results/analysis',
        { data: modelData, valves: modelStore.modelParams, analysis_params: analysisValues },
        {
          params: {
            model_name: modelStore.selectedModel.file,
            analysis_id: analysis.id,
            model_folder_name: modelData.model.modelFolderName,
            run_id: status.run_id
          },
          responseType: 'blob'
        }
      );
      viewStore.setAnalysisImage({
        label: analysis.label,
        blob: response.data,
        filename: `${modelStore.selectedModel.file}_${analysis.id}.png`
      });
      viewStore.viewId = 'analysis';
    } catch (error) {
      // With responseType blob, the JSON error body arrives as a Blob too.
      const body = (error as { response?: { data?: unknown } }).response?.data;
      let detail = '';
      if (body instanceof Blob) {
        try {
          detail = JSON.parse(await body.text()).detail ?? '';
        } catch {
          /* not JSON */
        }
      }
      notify.negative(`Analysis failed${detail ? `: ${detail}` : ''}`);
    }
    analysisLoading = false;
  }

  async function deleteModelData() {
    try {
      await deleteModelApi({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName
      });
      notify.positive('Model data deleted');
    } catch {
      notify.negative('Could not delete the model data');
    }
  }

  function deleteLocalSettings() {
    localStorage.removeItem('darkMode');
    localStorage.removeItem('modelData');
    localStorage.removeItem('selectedModel');
    localStorage.removeItem('modelParams');
    localStorage.removeItem('panel');
  }

  async function deleteUserData() {
    try {
      await deleteUserDataApi({ checkDate: false });
      notify.positive('User data deleted');
    } catch {
      notify.negative('Could not delete the user data');
    }
    bus.emit('getStatus' as never);
  }

  function confirmDelete() {
    if (dialogConfirm === 'model') deleteModelData();
    else if (dialogConfirm === 'localSettings') deleteLocalSettings();
    else if (dialogConfirm === 'userData') deleteUserData();
    dialogConfirm = null;
    dialogDelete = false;
  }

  onDestroy(() => timer && clearInterval(timer));
</script>

<!-- Where this model stands in configure → mesh → run → results, derived from
     the same flags that gate the buttons below, so a disabled button is
     explained by the step that isn't done yet. -->
<ol
  class="border-border text-muted-foreground flex items-center gap-2 overflow-x-auto border-b px-3 py-1.5 text-xs whitespace-nowrap"
  aria-label="Simulation progress"
>
  {#each steps as step, i (step.label)}
    {#if i > 0}<li aria-hidden="true" class="bg-border h-px w-4 shrink-0 sm:w-8"></li>{/if}
    <li
      class="flex items-center gap-1.5 {step.state === 'todo' ? '' : 'text-foreground font-medium'}"
      aria-current={step.state === 'active' ? 'step' : undefined}
    >
      <span
        class="flex h-4 w-4 items-center justify-center rounded-full border {step.state === 'done'
          ? 'border-success bg-success text-white'
          : step.state === 'active'
            ? 'border-primary'
            : 'border-border'}"
      >
        {#if step.state === 'done'}
          <Check class="h-3 w-3" />
        {:else if step.state === 'active'}
          <span class="bg-primary h-1.5 w-1.5 rounded-full motion-safe:animate-pulse"></span>
        {/if}
      </span>
      {step.label}
      {#if step.state === 'active' && step.hint}
        <span class="text-muted-foreground font-normal">· {step.hint}</span>
      {/if}
    </li>
  {/each}
</ol>

<div class="border-border bg-muted/30 flex flex-wrap items-center gap-1 border-b px-2 py-1">
  {#if !jobActive}
    <Button
      size="sm"
      onclick={checkEnergy}
      disabled={submitLoading || !status.created || !status.meshfileExist}
      title={!status.created
        ? 'Generate the mesh first'
        : !status.meshfileExist
          ? 'Generate or upload a mesh first'
          : 'Run simulation'}
    >
      <Play class="h-4 w-4" />
      Run simulation
    </Button>
  {:else}
    <Button variant="outline" size="sm" onclick={cancelJob} disabled={submitLoading}>
      <X class="h-4 w-4" />
      Cancel job
    </Button>
  {/if}

  <Button
    variant="ghost"
    size="icon"
    onclick={() => (dialogDownload = true)}
    disabled={resultsLoading || (!status.results && !status.csvResults)}
    title="Download Results"
  >
    <Download class="h-4 w-4" />
  </Button>

  <Button
    variant="ghost"
    size="icon"
    onclick={() => (viewStore.viewId = 'results')}
    disabled={!status.results || !outputs.some((o) => o.selectedFileType === 'Exodus')}
    title={!status.results ? 'Results not generated yet' : 'Show Results'}
  >
    <Eye class="h-4 w-4" />
  </Button>

  <Button variant="ghost" size="icon" onclick={updatePlotVariables} title="Plot Results">
    <LineChart class="h-4 w-4" />
  </Button>

  {#if analyses.length}
    <Button
      variant="ghost"
      size="icon"
      onclick={openAnalysisDialog}
      disabled={analysisLoading || !hasResults}
      title={!hasResults ? 'Results not generated yet' : 'Run an analysis'}
    >
      <ImageIcon class="h-4 w-4" />
    </Button>
  {/if}

  <div class="flex-1"></div>

  <Button variant="ghost" size="icon" onclick={() => (dialogDelete = true)} title="Delete data">
    <Trash2 class="h-4 w-4" />
  </Button>
</div>

<Dialog.Root bind:open={dialogEnergySavings}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,32rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-2 text-lg font-semibold">Run simulation</Dialog.Title>
      <p class="text-muted-foreground text-sm">
        Renewables currently supply {energyPercent}% of grid power. Run now, or wait for a greener
        window.
      </p>
      <div class="my-3"><RenewableView /></div>
      <div class="flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogEnergySavings = false)}>Cancel</Button>
        <Button
          onclick={() => {
            dialogEnergySavings = false;
            _runModel();
          }}
        >
          Run simulation
        </Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={dialogDownload}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-2 text-lg font-semibold">Download Results</Dialog.Title>
      <p class="text-muted-foreground text-sm">
        Do you want to retrieve all model files, including the input files and log data, or only the
        exodus result?
      </p>
      <div class="mt-4 flex flex-wrap justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogDownload = false)}>Cancel</Button>
        <Button variant="outline" onclick={() => saveResults(false)}>Only the result</Button>
        <Button onclick={() => saveResults(true)}>All data</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={dialogPlot}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-3 text-lg font-semibold">Plot results</Dialog.Title>
      <Select bind:value={plotOutput}>
        {#each outputs as output, outputIdx (outputIdx)}
          <option value={output.name}>{output.name}</option>
        {/each}
      </Select>
      <div class="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogPlot = false)}>Cancel</Button>
        <Button onclick={_getPlot}>Show</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={dialogAnalysis}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-3 text-lg font-semibold">Run analysis</Dialog.Title>
      <form
        class="space-y-3"
        onsubmit={(e) => {
          e.preventDefault();
          runAnalysis();
        }}
      >
        {#if analyses.length > 1}
          <div class="space-y-1">
            <Label for="analysis-id">Analysis</Label>
            <Select
              id="analysis-id"
              value={analysisId}
              onchange={(e) => selectAnalysis((e.currentTarget as HTMLSelectElement).value)}
            >
              {#each analyses as analysis (analysis.id)}
                <option value={analysis.id}>{analysis.label}</option>
              {/each}
            </Select>
          </div>
        {:else if selectedAnalysis}
          <p class="text-sm font-medium">{selectedAnalysis.label}</p>
        {/if}
        {#each selectedAnalysis?.params ?? [] as param (param.name)}
          {#if param.type === 'checkbox'}
            <Toggle bind:checked={analysisValues[param.name] as boolean} label={param.label} />
          {:else}
            <div class="space-y-1">
              <Label for={`analysis-${param.name}`}>{param.label}</Label>
              {#if param.type === 'select'}
                <Select
                  id={`analysis-${param.name}`}
                  bind:value={analysisValues[param.name]}
                  title={param.description}
                >
                  {#each new Set([String(param.value), ...analysisOptions(param)]) as opt (opt)}
                    <option value={opt}>{opt}</option>
                  {/each}
                </Select>
              {:else}
                <Input
                  id={`analysis-${param.name}`}
                  type={param.type === 'number' ? 'number' : 'text'}
                  bind:value={analysisValues[param.name]}
                  title={param.description}
                />
              {/if}
            </div>
          {/if}
        {/each}
        <div class="flex justify-end gap-2 pt-1">
          <Button type="button" variant="ghost" onclick={() => (dialogAnalysis = false)}>
            Cancel
          </Button>
          <Button type="submit" disabled={!selectedAnalysis}>Run</Button>
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={dialogDelete}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      {#if !dialogConfirm}
        <Dialog.Title class="mb-3 text-lg font-semibold">Delete data</Dialog.Title>
        <div class="flex flex-col gap-2">
          <Button variant="outline" onclick={() => (dialogConfirm = 'model')}>Model data</Button>
          <Button variant="outline" onclick={() => (dialogConfirm = 'localSettings')}>
            Settings stored in this browser
          </Button>
          <Button variant="outline" onclick={() => (dialogConfirm = 'userData')}>User data</Button>
          <Button variant="ghost" onclick={() => (dialogDelete = false)}>Cancel</Button>
        </div>
      {:else}
        <Dialog.Title class="mb-2 text-lg font-semibold">Are you sure?</Dialog.Title>
        <p class="text-muted-foreground text-sm">This action cannot be undone.</p>
        <div class="mt-4 flex justify-end gap-2">
          <Button variant="ghost" onclick={() => (dialogConfirm = null)}>Cancel</Button>
          <Button variant="destructive" onclick={confirmDelete}>Delete</Button>
        </div>
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
