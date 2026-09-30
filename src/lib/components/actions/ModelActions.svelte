<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { DropdownMenu } from 'bits-ui';
  import {
    Save,
    Undo2,
    Cog,
    Download,
    ArrowUpDown,
    FolderOpen,
    MoreHorizontal,
    FileCog
  } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { authStore } from '$lib/stores/auth-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { downloadFile } from '$lib/utils/download';
  import { api } from '$lib/api/client';
  import { generateModel as generateModelApi, saveConfig } from '$lib/client';
  import type { ModelData, Valves } from '$lib/client';
  import { normalizeModelData } from '$lib/utils/legacy-model-data';
  import Button, { buttonVariants } from '$lib/components/ui/Button.svelte';

  const modelData = $derived(modelStore.modelData);
  const uploaded = $derived(modelData.model.meshSource === 'upload');
  const missingMesh = $derived(uploaded && !modelData.model.meshFile);
  const isOwnModel = $derived(
    modelStore.availableModels.find((m) => m.file === modelStore.selectedModel.file)?.own === true
  );

  let modelLoading = $state(false);
  let fileInput: HTMLInputElement;

  function readData() {
    fileInput.click();
  }

  function onFilePicked(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;
    if (file.type === 'application/json') loadJsonFile(file);
  }

  function loadJsonFile(file: Blob) {
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
      await saveConfig({ modelName: modelStore.selectedModel.file, requestBody: modelData });
      notify.positive('Config saved');
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function saveModel() {
    modelLoading = true;
    try {
      const url = `/workspaces/${encodeURIComponent(modelStore.selectedModel.file)}/${encodeURIComponent(modelData.model.modelFolderName)}/download`;
      const response = await api.get(url, { responseType: 'blob' });
      const filename = `${modelStore.selectedModel.file}_${modelData.model.modelFolderName}.zip`;
      downloadFile(filename, response.data);
    } catch (error) {
      notify.negative('Download failed');
      console.error(error);
    }
    modelLoading = false;
  }

  async function generateModel() {
    if (!uploaded) {
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
      bus.emit('viewPointData' as never);
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

  const menuItems = $derived(
    [
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
        show: !uploaded
      },
      {
        label: 'Save as default config',
        icon: FileCog,
        action: _saveConfig,
        disabled: false,
        // Built-in defaults ship with the repo, so only offer them while developing PeriHub itself.
        show: authStore.canAuthorModels && (isOwnModel || defaultStore.dev)
      }
    ].filter((item) => item.show)
  );
</script>

<div class="border-border bg-muted/30 flex flex-wrap items-center gap-1 border-b px-2 py-1">
  <!-- Uploaded meshes only need the input deck; the span carries the tooltip, since a disabled button gets no hover. -->
  <span title={missingMesh ? 'Upload a mesh first' : undefined}>
    <Button size="sm" onclick={generateModel} id="button-runModel" disabled={missingMesh}>
      <Cog class="h-4 w-4" />
      {uploaded ? 'Generate input deck' : 'Generate mesh'}
    </Button>
  </span>

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
