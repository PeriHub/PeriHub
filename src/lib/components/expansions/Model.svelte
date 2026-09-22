<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import { getModels, getJobFolders } from '$lib/client';
  import { refreshModelFromBackend } from '$lib/utils/modelSync';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';

  const model = $derived(modelStore.modelData.model);

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

  async function switchOwnModels() {
    if (!model.ownModel) {
      modelStore.selectedModel = { title: 'Compact Tenison', file: 'CompactTension' };
    }
    await selectMethod();
  }

  function onSelectedModelChange() {
    if (typeof window !== 'undefined') {
      localStorage.setItem('selectedModel', JSON.stringify(modelStore.selectedModel));
    }
    if (!modelStore.modelData.model.ownModel) {
      bus.emit('showModelImg' as never, modelStore.selectedModel.file as never);
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
  <Toggle
    checked={model.ownModel}
    onCheckedChange={(v: boolean) => {
      model.ownModel = v;
      switchOwnModels();
    }}
    label="Own Model"
    disabled={defaultStore.trial}
  />

  {#if !model.ownModel}
    <div class="max-w-xs space-y-1">
      <Label for="model-select">Model Name</Label>
      <Select
        id="model-select"
        value={modelStore.selectedModel.file}
        onchange={(e) => {
          const file = (e.target as HTMLSelectElement).value;
          const m = modelStore.availableModels.find((x) => x.file === file);
          if (m) modelStore.selectedModel = m;
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
      <Label for="model-name">Model Name</Label>
      <Input
        id="model-name"
        bind:value={modelStore.selectedModel.file}
        oninput={onSelectedModelChange}
      />
    </div>
  {/if}

  <div class="max-w-xs space-y-1">
    <Label for="model-subname">Model Subname</Label>
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

  {#if model.ownModel}
    <div class="max-w-xs space-y-1">
      <Label for="mesh-file">Mesh File</Label>
      <Input id="mesh-file" bind:value={model.meshFile} />
    </div>
  {/if}

  <Toggle bind:checked={model.twoDimensional} label="Two Dimensional" />

  {#if !model.ownModel}
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
            <Toggle bind:checked={param.value} label={param.label} />
          {/if}
        {/if}
      {/each}
    </div>
  {/if}
</div>
