<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/auth-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { FileUp, X } from 'lucide-svelte';
  import { getModels, getJobFolders } from '$lib/client';
  import type { Discretization } from '$lib/client';
  import { api } from '$lib/api/client';
  import { refreshModelFromBackend } from '$lib/utils/modelSync';
  import { MESH_EXTENSIONS, meshTypeFromFilename } from '$lib/utils/mesh-file';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const model = $derived(modelStore.modelData.model);
  const uploaded = $derived(model.meshSource === 'upload');
  const sources = [
    { value: 'model', label: 'Predefined model' },
    { value: 'upload', label: 'Upload mesh' }
  ] as const;

  let meshInput = $state<HTMLInputElement>();
  let extraInput = $state<HTMLInputElement>();
  let uploadBusy = $state(false);
  let dragOver = $state(false);

  let modelFolderNameList = $state(['Default']);

  function _getJobFolders() {
    getJobFolders({ modelName: modelStore.selectedModel.file })
      .then((response) => (modelFolderNameList = response))
      .catch((error) => notify.apiError(error));
  }

  async function selectMethod() {
    refreshModelFromBackend(modelStore.selectedModel.file);
    _getJobFolders();
  }

  function selectModelFolderName() {
    bus.emit('getStatus' as never);
  }

  async function switchMeshSource(source: 'model' | 'upload') {
    if (source === model.meshSource) return;
    if (source === 'upload') {
      // Own workspace name, so uploads don't land in a predefined model's folders.
      modelStore.selectedModel = { title: 'Uploaded mesh', file: 'UploadedMesh' };
      model.meshSource = 'upload';
      model.meshFile = null;
      onSelectedModelChange();
      _getJobFolders();
    } else {
      modelStore.selectedModel = { title: 'Compact Tension', file: 'CompactTension' };
      model.meshSource = 'model';
      onSelectedModelChange();
      await selectMethod();
    }
  }

  function workspaceUrl() {
    return `/workspaces/${encodeURIComponent(modelStore.selectedModel.file)}/${encodeURIComponent(model.modelFolderName)}/files`;
  }

  async function postFiles(files: File[]) {
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    await api.post(workspaceUrl(), formData);
  }

  async function uploadMesh(file: File | undefined) {
    if (!file) return;
    const type = meshTypeFromFilename(file.name);
    if (!type) {
      notify.negative(`${file.name} is not a mesh file (${MESH_EXTENSIONS.replaceAll(',', ', ')})`);
      return;
    }
    uploadBusy = true;
    try {
      await postFiles([file]);
      model.meshFile = file.name;
      const data = modelStore.modelData;
      if (!data.discretization) data.discretization = {} as Discretization;
      data.discretization.discType = type;
      if (type === 'gcode' && !data.discretization.gcode) {
        data.discretization.gcode = {
          overwriteMesh: true,
          sampling: 1,
          width: 0.4,
          height: 0.2,
          scale: 1
        };
      }
      notify.positive(`Mesh ${file.name} uploaded`);
      viewStore.viewId = 'model';
      // Give the Model tab time to mount before asking it to load the points.
      await new Promise((res) => setTimeout(res, 500));
      bus.emit('viewPointData' as never);
      bus.emit('getStatus' as never);
    } catch (error) {
      notify.apiError(error);
    }
    uploadBusy = false;
  }

  async function uploadExtraFiles(files: FileList | null) {
    if (!files?.length) return;
    uploadBusy = true;
    try {
      await postFiles(Array.from(files));
      notify.positive('Files uploaded');
    } catch (error) {
      notify.apiError(error);
    }
    uploadBusy = false;
  }

  function onSelectedModelChange() {
    if (typeof window !== 'undefined') {
      localStorage.setItem('selectedModel', JSON.stringify(modelStore.selectedModel));
    }
    if (modelStore.modelData.model.meshSource !== 'upload') {
      viewStore.viewId = 'image';
    }
    bus.emit('getStatus' as never);
  }

  onMount(() => {
    bus.on('getJobFolders' as never, _getJobFolders);
    (async () => {
      modelStore.availableModels = await getModels();
      await _getJobFolders();
    })();
    return () => bus.off('getJobFolders' as never, _getJobFolders);
  });
</script>

<div class="space-y-3 p-3">
  <div
    role="radiogroup"
    aria-label="Mesh source"
    class="border-input bg-muted/40 inline-flex rounded-md border p-0.5"
    title={authStore.isGuest ? 'Log in for full access' : undefined}
  >
    {#each sources as source (source.value)}
      <button
        type="button"
        role="radio"
        aria-checked={model.meshSource === source.value}
        disabled={authStore.isGuest}
        onclick={() => switchMeshSource(source.value)}
        class="focus-visible:ring-ring h-7 rounded px-3 text-xs transition-colors focus-visible:ring-2 focus-visible:outline-none disabled:opacity-50 {model.meshSource ===
        source.value
          ? 'bg-background shadow-sm'
          : 'text-muted-foreground hover:text-foreground'}"
      >
        {source.label}
      </button>
    {/each}
  </div>

  {#if !uploaded}
    <div class="max-w-xs space-y-1">
      <Label for="model-select">Model name</Label>
      <Select
        id="model-select"
        value={modelStore.selectedModel.file}
        onchange={(e) => {
          const file = (e.target as HTMLSelectElement).value;
          const m = modelStore.availableModels.find((x) => x.file === file);
          if (m) modelStore.selectedModel = { title: m.title as string, file: m.file as string };
          onSelectedModelChange();
          selectMethod();
        }}
      >
        {#each modelStore.availableModels as m, mIdx (m.file ?? mIdx)}
          <option value={m.file}>{m.title}</option>
        {/each}
      </Select>
    </div>
  {:else}
    <div class="max-w-xs space-y-1">
      <Label for="model-name">Workspace name</Label>
      <Input
        id="model-name"
        bind:value={modelStore.selectedModel.file}
        oninput={onSelectedModelChange}
      />
    </div>
  {/if}

  <div class="max-w-xs space-y-1">
    <Label for="model-subname">Model subname</Label>
    <input
      id="model-subname"
      list="model-folder-names"
      bind:value={model.modelFolderName}
      onchange={selectModelFolderName}
      class="border-input bg-background flex h-9 w-full rounded-md border px-3 py-1 text-sm shadow-sm"
    />
    <datalist id="model-folder-names">
      {#each modelFolderNameList as name, folderIdx (name ?? folderIdx)}
        <option value={name}></option>
      {/each}
    </datalist>
  </div>

  {#if uploaded}
    <div class="max-w-xs space-y-1">
      <Label for="mesh-file">Mesh file</Label>
      {#if model.meshFile}
        <div class="border-input flex items-center gap-2 rounded-md border px-2 py-1.5 text-sm">
          <FileUp class="text-muted-foreground h-4 w-4 shrink-0" />
          <span class="min-w-0 flex-1 truncate" title={model.meshFile}>{model.meshFile}</span>
          <span class="text-muted-foreground text-xs uppercase">
            {modelStore.modelData.discretization?.discType ?? ''}
          </span>
          <Button
            variant="ghost"
            size="sm"
            disabled={uploadBusy}
            onclick={() => meshInput?.click()}
          >
            Replace
          </Button>
          <button
            type="button"
            class="hover:bg-muted rounded p-1"
            aria-label="Remove mesh"
            onclick={() => (model.meshFile = null)}
          >
            <X class="h-3.5 w-3.5" />
          </button>
        </div>
      {:else}
        <button
          id="mesh-file"
          type="button"
          disabled={uploadBusy}
          onclick={() => meshInput?.click()}
          ondragover={(e) => {
            e.preventDefault();
            dragOver = true;
          }}
          ondragleave={() => (dragOver = false)}
          ondrop={(e) => {
            e.preventDefault();
            dragOver = false;
            uploadMesh(e.dataTransfer?.files[0]);
          }}
          class="flex w-full flex-col items-center gap-1 rounded-md border-2 border-dashed px-3 py-4 text-center text-sm transition-colors {dragOver
            ? 'border-primary bg-primary/5'
            : 'border-input hover:bg-muted/50'}"
        >
          <FileUp class="text-muted-foreground h-5 w-5" />
          <span>{uploadBusy ? 'Uploading…' : 'Drop a mesh file or click to choose'}</span>
          <span class="text-muted-foreground text-xs">.txt, .e, .g, .gcode — required</span>
        </button>
      {/if}
      <input
        bind:this={meshInput}
        type="file"
        class="hidden"
        accept={MESH_EXTENSIONS}
        onchange={(e) => {
          const input = e.target as HTMLInputElement;
          uploadMesh(input.files?.[0]);
          input.value = '';
        }}
      />
      <button
        type="button"
        class="text-muted-foreground hover:text-foreground text-xs underline-offset-2 hover:underline"
        disabled={uploadBusy}
        onclick={() => extraInput?.click()}
      >
        Additional files (node sets, …)
      </button>
      <input
        bind:this={extraInput}
        type="file"
        multiple
        class="hidden"
        onchange={(e) => {
          const input = e.target as HTMLInputElement;
          uploadExtraFiles(input.files);
          input.value = '';
        }}
      />
    </div>
  {/if}

  <Toggle bind:checked={model.twoDimensional} label="Two dimensional" />

  {#if !uploaded}
    <div class="border-border space-y-2 border-t pt-3">
      {#each modelStore.modelParams.valves ?? [] as param, paramIdx (param.name ?? paramIdx)}
        {#if !param.depends || modelStore.modelParams.valves?.find((o) => o.name === param.depends)?.value}
          {#if typeof param.value !== 'boolean' && ['text', 'number'].includes(param.type)}
            <div class="max-w-xs space-y-1">
              <Label for={`valve-${param.name}`}>{param.label}</Label>
              <Input
                id={`valve-${param.name}`}
                type={param.type}
                bind:value={param.value}
                title={param.description}
              />
            </div>
          {:else if param.type === 'select' && param.options}
            <div class="max-w-xs space-y-1">
              <Label for={`valve-${param.name}`}>{param.label}</Label>
              <Select id={`valve-${param.name}`} bind:value={param.value} title={param.description}>
                {#each Array.isArray(param.options) ? param.options : [param.options] as opt (opt)}
                  <option value={opt}>{opt}</option>
                {/each}
              </Select>
            </div>
          {:else if param.type === 'checkbox'}
            <Toggle bind:checked={param.value as boolean} label={param.label} />
          {/if}
        {/if}
      {/each}
    </div>
  {/if}
</div>
