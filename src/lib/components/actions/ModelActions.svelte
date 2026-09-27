<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Dialog, DropdownMenu } from 'bits-ui';
  import {
    Upload,
    Save,
    Undo2,
    Cog,
    Download,
    Rewind,
    ArrowUpDown,
    X,
    FolderOpen,
    MoreHorizontal,
    FileCog
  } from 'lucide-svelte';
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
  import { normalizeModelData } from '$lib/utils/legacy-model-data';
  import Button, { buttonVariants } from '$lib/components/ui/Button.svelte';

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
        modelStore.modelData = {
          ...modelStore.modelData,
          ...normalizeModelData(result.modelData)
        } as ModelData;
      } else {
        modelStore.modelData = {
          ...modelStore.modelData,
          ...normalizeModelData(result)
        } as ModelData;
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

  const menuItems = $derived(
    [
      {
        label: 'Upload model files',
        icon: Upload,
        action: () => (dialogUpload = true),
        disabled: defaultStore.trial,
        show: modelData.model.ownModel
      },
      {
        label: 'Download model files',
        icon: Download,
        action: saveModel,
        disabled: modelLoading || !defaultStore.status.created,
        show: true
      },
      {
        label: 'Reset to model defaults',
        icon: Undo2,
        action: () => bus.emit('resetData'),
        disabled: false,
        show: !modelData.model.ownModel
      },
      {
        label: 'Use predefined models',
        icon: Rewind,
        action: switchModels,
        disabled: false,
        show: modelData.model.ownModel
      },
      {
        label: 'Save as default config',
        icon: FileCog,
        action: _saveConfig,
        disabled: false,
        show: defaultStore.dev
      }
    ].filter((item) => item.show)
  );

  function onUploadPicked(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    if (files && files.length > 0) uploadFiles(files);
  }
</script>

<div class="border-border bg-muted/30 flex flex-wrap items-center gap-1 border-b px-2 py-1">
  <Button size="sm" onclick={generateModel} id="button-runModel">
    <Cog class="h-4 w-4" />
    Generate mesh
  </Button>

  <Button
    variant="ghost"
    size="icon"
    onclick={readData}
    disabled={defaultStore.trial}
    title={defaultStore.trial ? 'Disabled in trial version' : 'Load model from JSON'}
  >
    <FolderOpen class="h-4 w-4" />
  </Button>
  <input
    bind:this={fileInput}
    type="file"
    class="hidden"
    accept="application/json"
    onchange={onFilePicked}
  />

  <Button variant="ghost" size="icon" onclick={saveData} title="Save model as JSON">
    <Save class="h-4 w-4" />
  </Button>

  <!-- Less frequent actions, kept out of the toolbar so the two main
       actions (Generate mesh here, Run simulation on the output side) stand out. -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger
      class={buttonVariants({ variant: 'ghost', size: 'icon' })}
      title="More model actions"
      aria-label="More model actions"
    >
      <MoreHorizontal class="h-4 w-4" />
    </DropdownMenu.Trigger>
    <DropdownMenu.Portal>
      <DropdownMenu.Content
        class="border-border bg-popover text-popover-foreground z-50 min-w-[220px] rounded-md border p-1 shadow-md"
        align="start"
      >
        {#each menuItems as item (item.label)}
          <DropdownMenu.Item
            class="data-[highlighted]:bg-muted flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none data-[disabled]:opacity-50"
            disabled={item.disabled}
            onSelect={item.action}
          >
            <item.icon class="h-4 w-4" />
            {item.label}
          </DropdownMenu.Item>
        {/each}
      </DropdownMenu.Content>
    </DropdownMenu.Portal>
  </DropdownMenu.Root>

  <div class="flex-1"></div>

  <Button
    variant="ghost"
    size="icon"
    onclick={() => bus.emit('openHidePanels')}
    title="Collapse/expand all sections"
  >
    <ArrowUpDown class="h-4 w-4" />
  </Button>
</div>

<Dialog.Root bind:open={dialogUpload}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <div class="mb-3 flex items-center justify-between">
        <Dialog.Title class="text-lg font-semibold">Upload Data</Dialog.Title>
        <Dialog.Close class="hover:bg-muted rounded-full p-1.5"><X class="h-4 w-4" /></Dialog.Close>
      </div>
      <input
        bind:this={uploadInput}
        type="file"
        multiple
        onchange={onUploadPicked}
        disabled={uploadBusy}
        class="text-muted-foreground file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 block w-full text-sm file:mr-3 file:rounded-md file:border-0 file:px-3 file:py-1.5"
      />
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
