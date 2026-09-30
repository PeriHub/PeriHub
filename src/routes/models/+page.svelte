<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Dialog, Tabs } from 'bits-ui';
  import { Plus, Trash2 } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { notify } from '$lib/utils/notify';
  import {
    getModels,
    getOwnModelFile,
    getConfig,
    saveConfig,
    saveModelFile,
    addModel,
    deleteModelFile
  } from '$lib/client';
  import type { ModelData } from '$lib/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import CodeBlock from '$lib/components/views/CodeBlock.svelte';
  import ModelPreview from '$lib/components/views/ModelPreview.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';

  // Model metadata from GET /models?own_only=true (support/model/loader.py).
  type OwnModel = {
    file: string;
    title: string;
    description?: string;
    version?: string;
    requirements?: string;
    format?: 'yaml' | 'python';
    /** Why the model can't be loaded, e.g. still in the legacy Valves/main format. */
    error?: string;
  };

  let modelList = $state<OwnModel[]>([]);
  let loaded = $state(false);
  let selected = $state<OwnModel | null>(null);
  let tab = $state('source');

  let dialogAddModel = $state(false);
  let dialogDeleteModel = $state(false);
  let newModelName = $state('');
  let description = $state('');

  let sourceCode = $state('');
  let analysisCode = $state('');
  let configText = $state('');
  let newModelFormat = $state<'yaml' | 'python'>('yaml');
  // Bumped after saving, so a Python model's preview re-runs the saved file.
  let savedVersion = $state(0);

  const isYaml = $derived(selected?.format === 'yaml');
  // The preview needs a ModelData; fall back to the editor's while the config is invalid.
  const previewData = $derived.by<ModelData>(() => {
    try {
      return JSON.parse(configText) as ModelData;
    } catch {
      return modelStore.modelData;
    }
  });

  const editorClass = 'h-[calc(100vh-14rem)] max-h-[45rem] min-h-[24rem]';

  async function fetchModels() {
    modelList = (await getModels({ ownOnly: true, verify: true })) as OwnModel[];
    loaded = true;
  }

  async function selectModel(model: OwnModel) {
    selected = model;
    if (tab === 'analysis' && model.format !== 'yaml') tab = 'source';
    try {
      sourceCode = (await getOwnModelFile({ modelName: model.file })) as unknown as string;
      analysisCode =
        model.format === 'yaml'
          ? ((await getOwnModelFile({
              modelName: model.file,
              part: 'analysis'
            })) as unknown as string)
          : '';
    } catch (error) {
      notify.apiError(error);
    }
    try {
      configText = JSON.stringify(await getConfig({ modelName: model.file }), null, 2);
    } catch {
      configText = '';
    }
  }

  async function addNewModel() {
    dialogAddModel = false;
    try {
      const file = (await addModel({
        modelName: newModelName,
        description,
        modelFormat: newModelFormat
      })) as unknown as string;
      await fetchModels();
      await selectModel(modelList.find((m) => m.file === file) ?? { title: newModelName, file });
      notify.positive(`Created ${newModelName}`);
      newModelName = '';
      description = '';
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function saveSource(part: 'model' | 'analysis') {
    if (!selected) return;
    try {
      await saveModelFile({
        modelName: selected.file,
        part,
        requestBody: { source_code: part === 'model' ? sourceCode : analysisCode }
      });
      notify.positive(part === 'model' ? 'Model saved' : 'Analysis saved');
      savedVersion += 1;
      // Title, version or a fixed legacy error may have changed.
      await fetchModels();
      selected = modelList.find((m) => m.file === selected?.file) ?? selected;
    } catch (error) {
      notify.apiError(error);
    }
  }

  async function saveModelConfig() {
    if (!selected) return;
    let config: ModelData;
    try {
      config = JSON.parse(configText);
    } catch (error) {
      notify.negative(`Config not saved — invalid JSON: ${(error as Error).message}`);
      return;
    }
    try {
      await saveConfig({ modelName: selected.file, requestBody: config });
      notify.positive('Config saved');
    } catch (error: unknown) {
      const detail = (error as { body?: { detail?: { msg: string; loc: string[] }[] } }).body
        ?.detail;
      if (!Array.isArray(detail)) return notify.apiError(error);
      for (const d of detail) notify.negative(`${d.msg} at ${d.loc.join('.')}`);
    }
  }

  async function confirmDeleteModel() {
    dialogDeleteModel = false;
    if (!selected) return;
    try {
      await deleteModelFile({ modelName: selected.file });
      notify.positive(`Deleted ${selected.title}`);
      selected = null;
    } catch (error) {
      notify.apiError(error);
    }
    await fetchModels();
  }

  onMount(fetchModels);
</script>

<svelte:head>
  <title>Own models — PeriHub</title>
</svelte:head>

{#snippet newModelButton(variant: 'default' | 'outline')}
  <Button
    {variant}
    class="w-full"
    disabled={defaultStore.trial}
    title={defaultStore.trial ? 'Not available in the trial' : undefined}
    onclick={() => (dialogAddModel = true)}
  >
    <Plus /> New model
  </Button>
{/snippet}

<div class="bg-background text-foreground">
  <div class="mx-auto max-w-[110rem] px-6 pt-12 pb-20 sm:pt-16">
    <header class="max-w-2xl">
      <h1
        class="font-display text-3xl leading-none font-extrabold tracking-tight sm:text-4xl"
        style="font-stretch: 125%"
      >
        Own models
      </h1>
      <p class="text-muted-foreground mt-3 text-balance">
        Describe a specimen in YAML — parameters, shapes and blocks, no programming — or write it in
        Python, and give it a default config. It then shows up in the editor's model list next to
        the built-in specimens.
      </p>
    </header>

    {#if loaded && modelList.length === 0}
      <div class="border-border mt-10 max-w-md rounded-xl border border-dashed p-6">
        <h2 class="font-semibold">No own models yet</h2>
        <p class="text-muted-foreground mt-1 mb-4 text-sm">
          A new model starts from a template: a working YAML (or Python) model and a default config
          you can edit here, with a live preview.
        </p>
        {@render newModelButton('default')}
        {#if defaultStore.trial}
          <p class="text-muted-foreground mt-2 text-xs">
            Creating models isn't available in the trial.
          </p>
        {/if}
      </div>
    {:else}
      <div class="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-[12rem_minmax(0,1fr)]">
        <nav aria-label="Own models" class="space-y-4 lg:sticky lg:top-6 lg:self-start">
          {@render newModelButton('outline')}
          <ul
            class="border-border flex gap-x-6 gap-y-3 overflow-x-auto border-b pb-3 lg:flex-col lg:border-b-0 lg:border-l lg:pb-0"
          >
            {#each modelList as m (m.file)}
              <li class="shrink-0">
                <button
                  type="button"
                  aria-current={selected?.file === m.file ? 'true' : undefined}
                  onclick={() => selectModel(m)}
                  class="group block text-left focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00658B] lg:-ml-px lg:border-l-2 lg:pl-4 {selected?.file ===
                  m.file
                    ? 'border-primary text-primary'
                    : 'hover:border-primary border-transparent'}"
                >
                  <span class="group-hover:text-primary font-medium">{m.title}</span>
                  {#if m.error}
                    <span class="text-destructive block text-xs">Can't be loaded</span>
                  {:else if m.version}
                    <span class="text-muted-foreground block font-mono text-xs">v{m.version}</span>
                  {/if}
                </button>
              </li>
            {/each}
          </ul>
        </nav>

        {#if selected}
          <section aria-labelledby="model-heading">
            <div class="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
              <div class="min-w-0">
                <h2 id="model-heading" class="text-2xl font-semibold tracking-tight">
                  {selected.title}
                  {#if selected.version}
                    <span class="text-muted-foreground ml-1 font-mono text-sm font-normal"
                      >v{selected.version}</span
                    >
                  {/if}
                </h2>
                {#if selected.description}
                  <p class="text-muted-foreground mt-1">{selected.description}</p>
                {/if}
                {#if selected.error}
                  <p
                    class="border-destructive/40 bg-destructive/10 text-destructive mt-2 rounded-md border px-3 py-1.5 text-sm"
                    role="status"
                  >
                    {selected.error}
                  </p>
                {/if}
                {#if selected.requirements}
                  <p class="text-muted-foreground mt-1 font-mono text-xs">
                    Requires {selected.requirements}
                  </p>
                {/if}
              </div>
              <Button
                variant="ghost"
                class="text-destructive hover:text-destructive"
                onclick={() => (dialogDeleteModel = true)}
              >
                <Trash2 /> Delete
              </Button>
            </div>

            <div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
              <Tabs.Root bind:value={tab} class="order-2 min-w-0 lg:order-1">
                <div class="border-border flex items-end justify-between gap-3 border-b">
                  <Tabs.List class="flex gap-1">
                    {#each isYaml ? [['source', 'Model'], ['analysis', 'Analysis'], ['config', 'Config']] : [['source', 'Model'], ['config', 'Config']] as [value, label] (value)}
                      <Tabs.Trigger
                        {value}
                        class="text-muted-foreground data-[state=active]:border-primary data-[state=active]:text-foreground -mb-px border-b-2 border-transparent px-3 py-2 text-sm font-medium whitespace-nowrap"
                      >
                        {label}
                      </Tabs.Trigger>
                    {/each}
                  </Tabs.List>
                  <Button
                    size="sm"
                    class="mb-1.5"
                    onclick={() =>
                      tab === 'config'
                        ? saveModelConfig()
                        : saveSource(tab === 'analysis' ? 'analysis' : 'model')}
                  >
                    {tab === 'config' ? 'Save config' : 'Save'}
                  </Button>
                </div>
                <Tabs.Content value="source" class="pt-3">
                  <CodeBlock
                    bind:value={sourceCode}
                    language={isYaml ? 'yaml' : 'python'}
                    class={editorClass}
                  />
                </Tabs.Content>
                <Tabs.Content value="analysis" class="pt-3">
                  <p class="text-muted-foreground mb-2 text-sm">
                    Optional <code>analysis.py</code>: functions marked with <code>@analysis</code> turn
                    a run's results into an image (Analysis button in the editor). Leave empty for none.
                  </p>
                  <CodeBlock bind:value={analysisCode} language="python" class={editorClass} />
                </Tabs.Content>
                <Tabs.Content value="config" class="pt-3">
                  <CodeBlock bind:value={configText} language="javascript" class={editorClass} />
                </Tabs.Content>
              </Tabs.Root>
              <!-- Outside the tabs, so it stays in view while editing the config or analysis too. -->
              <div
                class="border-border relative order-1 h-[45vh] min-h-[18rem] rounded-md border lg:sticky lg:top-4 lg:order-2 lg:h-[calc(100vh-2rem)] lg:max-h-[48rem] lg:self-start"
              >
                <p class="text-muted-foreground absolute bottom-2 left-3 z-10 text-xs">
                  {isYaml ? 'Preview updates as you type' : 'Preview of the saved file'}
                </p>
                {#key savedVersion}
                  <ModelPreview
                    modelName={selected.file}
                    data={previewData}
                    valves={{ valves: [] }}
                    source={isYaml ? sourceCode : undefined}
                    paused={Boolean(selected.error) && !isYaml}
                  />
                {/key}
              </div>
            </div>
          </section>
        {:else if loaded}
          <p class="text-muted-foreground self-center">
            Pick a model on the left to edit its source and default config.
          </p>
        {/if}
      </div>
    {/if}
  </div>
</div>

<Dialog.Root bind:open={dialogAddModel}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="text-lg font-semibold">New model</Dialog.Title>
      <Dialog.Description class="text-muted-foreground mb-4 text-sm">
        Starts from a template you can edit afterwards.
      </Dialog.Description>
      <form
        class="space-y-3"
        onsubmit={(e) => {
          e.preventDefault();
          addNewModel();
        }}
      >
        <div class="space-y-1">
          <Label for="new-model-name">Name</Label>
          <Input id="new-model-name" required bind:value={newModelName} />
        </div>
        <div class="space-y-1">
          <Label for="new-model-desc">Description</Label>
          <Input id="new-model-desc" bind:value={description} />
        </div>
        <fieldset class="space-y-1">
          <legend class="text-sm font-medium">Write it in</legend>
          <label class="flex items-start gap-2 text-sm">
            <input type="radio" bind:group={newModelFormat} value="yaml" class="mt-1" />
            <span
              >YAML <span class="text-muted-foreground"
                >— parameters, shapes and blocks; no programming</span
              ></span
            >
          </label>
          <label class="flex items-start gap-2 text-sm">
            <input type="radio" bind:group={newModelFormat} value="python" class="mt-1" />
            <span
              >Python <span class="text-muted-foreground">— for custom point clouds and logic</span
              ></span
            >
          </label>
        </fieldset>
        <div class="flex justify-end gap-2 pt-1">
          <Button type="button" variant="ghost" onclick={() => (dialogAddModel = false)}>
            Cancel
          </Button>
          <Button type="submit" disabled={!newModelName.trim()}>Create model</Button>
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={dialogDeleteModel}>
  <Dialog.Portal>
    <Dialog.Overlay class="fixed inset-0 z-50 bg-black/50" />
    <Dialog.Content
      class="border-border bg-card fixed top-1/2 left-1/2 z-50 w-[min(92vw,26rem)] -translate-x-1/2 -translate-y-1/2 rounded-xl border p-5 shadow-lg"
    >
      <Dialog.Title class="text-lg font-semibold">Delete {selected?.title}?</Dialog.Title>
      <Dialog.Description class="text-muted-foreground mt-1 text-sm">
        This removes its source and default config. It can't be undone.
      </Dialog.Description>
      <div class="mt-4 flex justify-end gap-2">
        <Button variant="ghost" onclick={() => (dialogDeleteModel = false)}>Cancel</Button>
        <Button variant="destructive" onclick={confirmDeleteModel}>Delete model</Button>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
