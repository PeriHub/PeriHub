<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Dialog } from 'bits-ui';
  import { Plus } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { notify } from '$lib/utils/notify';
  import {
    getOwnModels,
    getOwnModelFile,
    getConfig,
    saveConfig,
    saveModelFile,
    addModel,
    deleteModelFile
  } from '$lib/client';
  import type { GetOwnModelsResponse, ModelData } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import CodeBlock from '$lib/components/views/CodeBlock.svelte';
  import JsonView from '$lib/components/views/JsonView.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';

  let modelList = $state<GetOwnModelsResponse>([]);
  let selectedModel = $state({ title: '', file: '' });

  let dialogAddModel = $state(false);
  let dialogDeleteModel = $state(false);
  let newModelName = $state('');
  let description = $state('');

  let sourceCode = $state('');
  let config = $state<ModelData | Record<string, never>>({});

  async function fetchModels() {
    modelList = await getOwnModels({ verify: true });
  }

  async function selectModel() {
    if (!selectedModel.file) return;
    try {
      sourceCode = (await getOwnModelFile({ modelFile: selectedModel.file })) as unknown as string;
      config = (await getConfig({ configFile: selectedModel.file })) as ModelData;
      viewStore.jsonData = config;
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function addNewModel() {
    dialogAddModel = false;
    try {
      const response = await addModel({ modelName: newModelName, description });
      selectedModel = { title: newModelName, file: response as unknown as string };
      await fetchModels();
      await selectModel();
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function saveModel() {
    try {
      await saveModelFile({ modelFile: selectedModel.file, sourceCode });
      notify.positive('Model saved');
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function saveModelConfig() {
    try {
      await saveConfig({ configFile: selectedModel.file, requestBody: config as ModelData });
      notify.positive('Config saved');
    } catch (error: unknown) {
      const err = error as { body?: { detail?: { msg: string; loc: string[] }[] } };
      for (const d of err.body?.detail ?? []) {
        notify.negative(`${d.msg}\n${d.loc}`);
      }
    }
  }

  async function confirmDeleteModel() {
    dialogDeleteModel = false;
    try {
      await deleteModelFile({ modelName: selectedModel.file });
      notify.positive('Model deleted');
      sourceCode = '';
      config = {};
    } catch (error) {
      notify.apiError(error);
    }
    await fetchModels();
  }

  onMount(fetchModels);
</script>

<svelte:head>
  <title>Models — PeriHub</title>
</svelte:head>

<div class="mx-auto max-w-6xl px-4 py-8">
  {#if !selectedModel.file}
    <div class="flex justify-center">
      <Card class="w-full max-w-md p-6 text-center">
        {#if modelList.length > 0}
          <h2 class="mb-3 text-lg font-semibold">Select existing model</h2>
          <Select
            value={selectedModel.file}
            onchange={(e) => {
              const file = (e.target as HTMLSelectElement).value;
              const m = modelList.find((x) => x.file === file);
              if (m) {
                selectedModel = m as { title: string; file: string };
                selectModel();
              }
            }}
          >
            <option value="">— choose a model —</option>
            {#each modelList as model, modelIdx (model.file ?? modelIdx)}
              <option value={model.file}>{model.title}</option>
            {/each}
          </Select>
          <div class="border-border my-4 border-t"></div>
          <p class="text-muted-foreground mb-3 text-sm">Or</p>
        {/if}
        <Button
          class="w-full"
          disabled={defaultStore.trial}
          onclick={() => (dialogAddModel = true)}
          title={defaultStore.trial ? 'Disabled in trial version' : undefined}
        >
          <Plus class="h-4 w-4" /> Add a new Model
        </Button>
      </Card>
    </div>
  {:else}
    <div class="mb-4 flex flex-wrap items-center gap-3">
      <Button
        variant="ghost"
        size="icon"
        disabled={defaultStore.trial}
        onclick={() => (dialogAddModel = true)}
      >
        <Plus class="h-4 w-4" />
      </Button>
      <Select
        class="max-w-xs"
        value={selectedModel.file}
        onchange={(e) => {
          const file = (e.target as HTMLSelectElement).value;
          const m = modelList.find((x) => x.file === file);
          if (m) {
            selectedModel = m as { title: string; file: string };
            selectModel();
          }
        }}
      >
        {#each modelList as model, modelIdx (model.file ?? modelIdx)}
          <option value={model.file}>{model.title}</option>
        {/each}
      </Select>
    </div>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {#if sourceCode !== ''}
        <div>
          <div class="mb-2 flex gap-2">
            <Button onclick={saveModel}>Save</Button>
            <Button variant="destructive" onclick={() => (dialogDeleteModel = true)}>Delete</Button>
          </div>
          <div class="border-border h-[calc(100vh-320px)] overflow-auto rounded-md border">
            <CodeBlock bind:value={sourceCode} language="python" />
          </div>
        </div>
      {/if}

      {#if Object.keys(config).length !== 0}
        <div>
          <div class="mb-2">
            <Button onclick={saveModelConfig}>Save</Button>
          </div>
          <div class="border-border h-[calc(100vh-320px)] overflow-auto rounded-md border">
            <JsonView />
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<Dialog.Root bind:open={dialogAddModel}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-3 text-lg font-semibold">Add Model</Dialog.Title>
      <div class="space-y-3">
        <div class="space-y-1">
          <Label for="new-model-name">Model Name</Label>
          <Input id="new-model-name" bind:value={newModelName} />
        </div>
        <div class="space-y-1">
          <Label for="new-model-desc">Description</Label>
          <Input id="new-model-desc" bind:value={description} />
        </div>
      </div>
      <div class="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogAddModel = false)}>Cancel</Button>
        <Button onclick={addNewModel}>Create</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={dialogDeleteModel}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="mb-3 text-lg font-semibold">
        Are you sure you want to delete {selectedModel.title}?
      </Dialog.Title>
      <div class="flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogDeleteModel = false)}>Cancel</Button>
        <Button variant="destructive" onclick={confirmDeleteModel}>Delete</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
