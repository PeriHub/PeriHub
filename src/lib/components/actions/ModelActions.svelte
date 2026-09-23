<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Dialog } from 'bits-ui';
  import { Upload, Save, Undo2, Cog, Download, Rewind, ArrowUpDown, Info, X } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { downloadFile } from '$lib/utils/download';
  import { api } from '$lib/api/client';
  import { config } from '$lib/config';
  import { generateModel as generateModelApi, saveConfig } from '$lib/client';
  import type { Discretization, ModelData, Valves } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';

  const sleep = (ms: number) => new Promise((res) => setTimeout(res, ms));

  const modelData = $derived(modelStore.modelData);
  const uploadPath = `${config.apiBase}/upload/files`;

  let dialogUpload = $state(false);
  let modelLoading = $state(false);
  let fileInput: HTMLInputElement;
  let uploadInput: HTMLInputElement;
  let uploadBusy = $state(false);

  function switchModels() {
    modelStore.modelData.model.ownMesh = false;
    modelStore.modelData.model.ownModel = false;
  }

  function readData() {
    fileInput.click();
  }

  function onFilePicked(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;
    if (file.type === 'application/json') loadJsonFile(file);
  }

  function loadJsonFile(file: Blob) {
    modelStore.modelData.model.ownMesh = false;
    modelStore.modelData.model.ownModel = false;

    const fr = new FileReader();
    fr.onload = (e) => {
      const result = JSON.parse(e.target?.result as string);
      if (result.modelData) {
        modelStore.modelData = { ...modelStore.modelData, ...result.modelData } as ModelData;
      } else {
        modelStore.modelData = { ...modelStore.modelData, ...result } as ModelData;
        console.log('Deprecated Json Format!');
      }
      if (result.modelParams) {
        modelStore.modelParams = structuredClone(result.modelParams) as Valves;
      }
      if (result.selectedModel) {
        modelStore.selectedModel = structuredClone(result.selectedModel);
      }
    };
    fr.readAsText(file);
  }

  function saveData() {
    downloadFile(
      `${modelStore.selectedModel.file}.json`,
      '{"modelData":' +
        JSON.stringify(modelStore.modelData) +
        ',"modelParams":' +
        JSON.stringify(modelStore.modelParams) +
        ',"selectedModel":' +
        JSON.stringify(modelStore.selectedModel) +
        '}',
      'application/json'
    );
  }

  async function _saveConfig() {
    try {
      await saveConfig({ configFile: modelStore.selectedModel.file, requestBody: modelData });
      notify.positive('Config saved');
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function saveModel() {
    modelLoading = true;
    try {
      const params = {
        model_name: modelStore.selectedModel.file,
        model_folder_name: modelData.model.modelFolderName
      };
      const response = await api.get('/model/getModel', { params, responseType: 'blob' });
      const filename = `${modelStore.selectedModel.file}_${modelData.model.modelFolderName}.zip`;
      downloadFile(filename, response.data);
    } catch (error) {
      notify.negative('Download failed');
      console.error(error);
    }
    modelLoading = false;
  }

  async function generateModel() {
    if (!modelData.model.ownModel) {
      viewStore.modelLoading = true;
    }
    viewStore.textLoading = true;
    viewStore.viewId = 'model';

    const body = { data: modelData, valves: modelStore.modelParams };

    try {
      await generateModelApi({
        modelName: modelStore.selectedModel.file,
        modelFolderName: modelData.model.modelFolderName,
        requestBody: body
      });
      notify.positive('Model generated');
      bus.emit('updateTextView' as never);
      bus.emit('viewInputFile' as never);
      if (!modelData.model.ownModel) {
        bus.emit('viewPointData' as never);
      }
      bus.emit('getStatus' as never);
      bus.emit('getJobFolders' as never);
    } catch (error: unknown) {
      const err = error as { status?: number; body?: { detail?: unknown } };
      if (err?.status === 422 && Array.isArray(err.body?.detail)) {
        for (const d of err.body!.detail as { msg: string; loc: string[] }[]) {
          notify.negative(`${d.msg} ${d.loc.join(', ')}`);
        }
      } else {
        notify.negative(String(err?.body?.detail ?? 'Model generation failed'));
      }
    }

    viewStore.modelLoading = false;
    viewStore.textLoading = false;
  }

  async function uploadFiles(files: FileList) {
    uploadBusy = true;
    const formData = new FormData();
    Array.from(files).forEach((f) => formData.append('files', f));

    try {
      const response = await api.post(
        `${uploadPath}?model_name=${modelStore.selectedModel.file}&model_folder_name=${modelData.model.modelFolderName}`,
        formData,
        { headers: { username: defaultStore.username } }
      );
      notify.positive('Files uploaded');
      dialogUpload = false;

      const first = files[0]!;
      const type = first.name.split('.')[1];
      if (type === 'gcode') {
        modelStore.modelData.model.meshFile = first.name;
        if (!modelStore.modelData.discretization) {
          modelStore.modelData.discretization = {} as Discretization;
        }
        modelStore.modelData.discretization.discType = 'gcode';
        if (!modelStore.modelData.discretization.gcode) {
          modelStore.modelData.discretization.gcode = {
            overwriteMesh: true,
            sampling: 1,
            width: 0.4,
            height: 0.2,
            scale: 1
          };
        }
      } else if (type === 'g') {
        viewStore.modelLoading = true;
        viewStore.viewId = 'model';
        await sleep(500);
        bus.emit('viewPointData' as never);
      } else if (type === 'txt' || type === 'e') {
        if (response.data?.message) {
          modelStore.modelData.model.meshFile = first.name;
          if (!modelStore.modelData.discretization) {
            modelStore.modelData.discretization = {} as Discretization;
          }
          modelStore.modelData.discretization.discType = type as 'txt' | 'e';
        }
        if (type === 'txt') {
          viewStore.modelLoading = true;
          viewStore.viewId = 'model';
          await sleep(500);
          bus.emit('viewPointData' as never);
        }
      }
      bus.emit('getStatus' as never);
    } catch (error) {
      console.error(error);
      notify.negative('Upload failed, file type not supported!');
    }
    viewStore.modelLoading = false;
    uploadBusy = false;
  }

  function onUploadPicked(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    if (files && files.length > 0) uploadFiles(files);
  }
</script>

<div class="flex flex-wrap items-center gap-1 border-b border-border bg-muted/30 px-2 py-1">
  <Button variant="ghost" size="icon" onclick={readData} disabled={defaultStore.trial} title={defaultStore.trial ? 'Disabled in trial version' : 'Load Model'}>
    <Upload class="h-4 w-4" />
  </Button>
  <input bind:this={fileInput} type="file" class="hidden" accept="application/json" onchange={onFilePicked} />

  <Button variant="ghost" size="icon" onclick={saveData} title="Save as JSON">
    <Save class="h-4 w-4" />
  </Button>

  {#if defaultStore.dev}
    <Button variant="ghost" size="icon" onclick={_saveConfig} title="Save Config">
      <Save class="h-4 w-4" />
    </Button>
  {/if}

  {#if !modelData.model.ownModel}
    <Button variant="ghost" size="icon" onclick={() => bus.emit('resetData')} title="Reset Data">
      <Undo2 class="h-4 w-4" />
    </Button>
  {/if}

  <Button variant="ghost" size="icon" onclick={generateModel} title="Generate Model" id="button-runModel">
    <Cog class="h-4 w-4" />
  </Button>

  {#if modelData.model.ownModel}
    <Button
      variant="ghost"
      size="icon"
      onclick={() => (dialogUpload = true)}
      disabled={defaultStore.trial}
      title={defaultStore.trial ? 'Disabled in trial version' : 'Upload Modelfiles'}
    >
      <Upload class="h-4 w-4" />
    </Button>
  {/if}

  <Button
    variant="ghost"
    size="icon"
    onclick={saveModel}
    disabled={modelLoading || !defaultStore.status.created}
    title="Download Modelfiles"
  >
    <Download class="h-4 w-4" />
  </Button>

  {#if modelData.model.ownModel}
    <Button variant="ghost" size="icon" onclick={switchModels} title="Use predefined Models">
      <Rewind class="h-4 w-4" />
    </Button>
  {/if}

  <div class="flex-1"></div>

  <Button variant="ghost" size="icon" onclick={() => bus.emit('openHidePanels')} title="Collapse/Expand all panels">
    <ArrowUpDown class="h-4 w-4" />
  </Button>

  <Button variant="ghost" size="icon" onclick={() => bus.emit('showTutorial')} title="Show Tutorial">
    <Info class="h-4 w-4" />
  </Button>
</div>

<Dialog.Root bind:open={dialogUpload}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="fixed left-1/2 top-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-5 shadow-lg"
    >
      <div class="mb-3 flex items-center justify-between">
        <Dialog.Title class="text-lg font-semibold">Upload Data</Dialog.Title>
        <Dialog.Close class="rounded-full p-1.5 hover:bg-muted"><X class="h-4 w-4" /></Dialog.Close>
      </div>
      <input
        bind:this={uploadInput}
        type="file"
        multiple
        onchange={onUploadPicked}
        disabled={uploadBusy}
        class="block w-full text-sm text-muted-foreground file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-primary-foreground hover:file:bg-primary/90"
      />
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
