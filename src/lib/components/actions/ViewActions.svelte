<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onDestroy } from 'svelte';
  import { Dialog } from 'bits-ui';
  import { Play, X, Download, Eye, LineChart, Trash2 } from 'lucide-svelte';
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
    cancelJob as cancelJobApi,
    getPlot,
    deleteModel as deleteModelApi,
    deleteModelFromCluster,
    deleteUserData as deleteUserDataApi,
    deleteUserDataFromCluster
  } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import RenewableView from '$lib/components/views/RenewableView.svelte';

  const sleep = (ms: number) => new Promise((res) => setTimeout(res, ms));
  const PALETTE = ['#00658b', '#d2ae3d', '#82a043', '#666666', '#3b98cb', '#f2cd51', '#a6bf51', '#858585'];

  const modelData = $derived(modelStore.modelData);
  const outputs = $derived(modelData.outputs ?? []);
  const status = $derived(defaultStore.status);

  let submitLoading = $state(false);
  let resultsLoading = $state(false);
  let timer: ReturnType<typeof setInterval> | null = null;
  let intervalCount = 0;

  let dialogEnergySavings = $state(false);
  let dialogDownload = $state(false);
  let dialogPlot = $state(false);
  let dialogDelete = $state(false);
  let dialogConfirm = $state<null | 'model' | 'cookies' | 'userData'>(null);

  let energyPercent = $state(0);
  let plotVariables = $state<string[]>([]);
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
      await runModelApi({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName,
        verbose: modelData.job.verbose,
        jobIds,
        requestBody: modelData
      });
      notify.positive('Job submitted');
      viewStore.textId = 'log';
      viewStore.viewId = 'jobs';
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

    if (intervalCount > 10) {
      submitLoading = false;
      notify.negative('Failed to submit model');
      if (timer) clearInterval(timer);
    }
    if (status.submitted) {
      submitLoading = false;
      await sleep(20000);
      bus.emit('enableWebsocket' as never);
      if (timer) clearInterval(timer);
    }
  }

  async function cancelJob() {
    submitLoading = true;
    try {
      await cancelJobApi({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName,
        cluster: modelData.job.cluster,
        sbatch: modelData.job.sbatch
      });
      notify.positive('Job canceled');
    } catch {
      notify.negative('Failed');
    }
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
        tasks: modelData.job.tasks,
        cluster: modelData.job.cluster,
        all_data: allData
      };
      const response = await api.get('/results/getResults', { params, responseType: 'blob' });
      const filename = allData
        ? `${modelStore.selectedModel.file}_${modelData.model.modelFolderName}.zip`
        : `${modelStore.selectedModel.file}_${modelData.model.modelFolderName}_${outputs[0]?.name}.e`;
      downloadFile(filename, response.data);
    } catch {
      notify.negative('Failed');
    }
    resultsLoading = false;
  }

  function updatePlotVariables() {
    plotVariables = [...(modelData.computes ?? []).map((c) => c.name), 'Time'];
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
        cluster: modelData.job.cluster,
        output: plotOutput,
        tasks: modelData.job.tasks,
        deviationsEnabled: modelData.deviations.enabled
      })) as Record<string, number[]>;

      notify.positive('Plot loaded');

      const firstProperty = Object.keys(plotRawData)[0]!;
      const tempData = Object.entries(plotRawData)
        .filter(([name]) => name !== firstProperty)
        .map(([name, values], i) => ({
          name,
          x: plotRawData[firstProperty]!,
          y: values,
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
      notify.negative('Failed');
    }
    viewStore.modelLoading = false;
  }

  async function deleteModelData() {
    try {
      await deleteModelApi({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName
      });
      notify.positive('Model deleted');
    } catch {
      notify.negative('Failed');
    }
    try {
      await deleteModelFromCluster({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName,
        cluster: modelData.job.cluster
      });
      notify.positive('Model deleted from cluster');
    } catch {
      notify.negative('Failed');
    }
  }

  function deleteCookies() {
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
      notify.negative('Failed');
    }
    try {
      await deleteUserDataFromCluster({ cluster: modelData.job.cluster, checkDate: false });
      notify.positive('User data deleted from cluster');
    } catch {
      notify.negative('Failed');
    }
    bus.emit('getStatus' as never);
  }

  function confirmDelete() {
    if (dialogConfirm === 'model') deleteModelData();
    else if (dialogConfirm === 'cookies') deleteCookies();
    else if (dialogConfirm === 'userData') deleteUserData();
    dialogConfirm = null;
    dialogDelete = false;
  }

  onDestroy(() => timer && clearInterval(timer));
</script>

<div class="flex flex-wrap items-center gap-1 border-b border-border bg-muted/30 px-2 py-1">
  {#if !status.submitted}
    <Button
      variant="ghost"
      size="icon"
      onclick={checkEnergy}
      disabled={submitLoading || !status.created || !status.meshfileExist}
      title={!status.created
        ? 'Model not created yet'
        : !status.meshfileExist
          ? 'Meshfile not created or uploaded yet'
          : 'Submit Model'}
    >
      <Play class="h-4 w-4" />
    </Button>
  {:else}
    <Button variant="ghost" size="icon" onclick={cancelJob} disabled={submitLoading} title="Cancel Job">
      <X class="h-4 w-4" />
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

  <div class="flex-1"></div>

  <Button variant="ghost" size="icon" onclick={() => (dialogDelete = true)} title="Delete data">
    <Trash2 class="h-4 w-4" />
  </Button>
</div>

<Dialog.Root bind:open={dialogEnergySavings}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 z-50 w-[min(92vw,32rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-5 shadow-lg"
    >
      <Dialog.Title class="mb-2 text-lg font-semibold">Submit Model</Dialog.Title>
      <p class="text-sm text-muted-foreground">
        Are you sure you want to submit the model? The current renewable energy share is {energyPercent}%.
      </p>
      <div class="my-3"><RenewableView /></div>
      <div class="flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogEnergySavings = false)}>No</Button>
        <Button
          onclick={() => {
            dialogEnergySavings = false;
            _runModel();
          }}
        >
          Yes
        </Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={dialogDownload}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-5 shadow-lg"
    >
      <Dialog.Title class="mb-2 text-lg font-semibold">Download Results</Dialog.Title>
      <p class="text-sm text-muted-foreground">
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
      class="fixed left-1/2 top-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-5 shadow-lg"
    >
      <Dialog.Title class="mb-3 text-lg font-semibold">Plot results</Dialog.Title>
      <Select bind:value={plotOutput}>
        {#each outputs as output, outputIdx (output.name ?? outputIdx)}
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

<Dialog.Root bind:open={dialogDelete}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-5 shadow-lg"
    >
      {#if !dialogConfirm}
        <Dialog.Title class="mb-3 text-lg font-semibold">Delete data</Dialog.Title>
        <div class="flex flex-col gap-2">
          <Button variant="outline" onclick={() => (dialogConfirm = 'model')}>Model data</Button>
          <Button variant="outline" onclick={() => (dialogConfirm = 'cookies')}>Cookies</Button>
          <Button variant="outline" onclick={() => (dialogConfirm = 'userData')}>User data</Button>
          <Button variant="ghost" onclick={() => (dialogDelete = false)}>Cancel</Button>
        </div>
      {:else}
        <Dialog.Title class="mb-2 text-lg font-semibold">Are you sure?</Dialog.Title>
        <p class="text-sm text-muted-foreground">This action cannot be undone.</p>
        <div class="mt-4 flex justify-end gap-2">
          <Button variant="ghost" onclick={() => (dialogConfirm = null)}>No</Button>
          <Button variant="destructive" onclick={confirmDelete}>Yes</Button>
        </div>
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
