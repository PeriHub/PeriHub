<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Lock, Trash2, Upload } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { viewStore } from '$lib/stores/view-store.svelte';
  import { authStore } from '$lib/stores/auth-store.svelte';
  import { publicConfig } from '$lib/config';
  import { bus } from '$lib/utils/bus';
  import { notify } from '$lib/utils/notify';
  import {
    createLibraryItem,
    listLibraryItems,
    updateLibraryItem,
    uploadFiles as uploadFilesApi
  } from '$lib/client';
  import type { LibraryItemOut, Material } from '$lib/client';
  import { fromLibrary, libraryUpdateBody, toLibraryProperties } from '$lib/utils/material-library';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import MaterialEditor from '$lib/components/MaterialEditor.svelte';

  const materials = $derived(modelStore.modelData.materials ?? []);

  let multiSoInput: HTMLInputElement;
  let propsInput: HTMLInputElement;

  // Shared material library (/materials page) - accounts only, guests can't use it.
  const canUseLibrary = $derived(authStore.hasAccount);
  let library = $state<LibraryItemOut[]>([]);

  async function fetchLibrary() {
    try {
      library = await listLibraryItems({ kind: 'material' });
    } catch (error) {
      notify.apiError(error);
    }
  }

  $effect(() => {
    if (canUseLibrary) fetchLibrary();
  });

  const libraryItem = (id: string | null | undefined) => library.find((i) => i.id === id);

  function loadFromLibrary(index: number, id: string) {
    const item = libraryItem(id);
    if (!item) return;
    materials[index] = fromLibrary($state.snapshot(item), materials[index]!.materialsId);
    notify.positive(`Loaded ${item.name}`);
  }

  async function saveToLibrary(material: Material) {
    const item = libraryItem(material.libraryId);
    if (!item) return;
    try {
      await updateLibraryItem({
        kind: 'material',
        itemId: item.id,
        requestBody: libraryUpdateBody(item, $state.snapshot(material) as Material)
      });
      notify.positive(`Saved ${material.name} to the library`);
    } catch (error) {
      // Deleted from the library meanwhile - drop the stale link.
      if ((error as { status?: number }).status === 404) material.libraryId = null;
      notify.apiError(error);
    }
    await fetchLibrary();
  }

  async function saveAsNew(material: Material) {
    try {
      const created = await createLibraryItem({
        kind: 'material',
        requestBody: {
          name: material.name,
          properties: toLibraryProperties($state.snapshot(material) as Material)
        }
      });
      material.libraryId = created.id;
      notify.positive(`Saved ${material.name} as a new private library material`);
    } catch (error) {
      notify.apiError(error);
    }
    await fetchLibrary();
  }

  function editNumStateVars(numStateVars: number) {
    bus.emit('addStateVarsToOutput' as never, numStateVars as never);
  }

  function uploadSo() {
    multiSoInput.click();
  }

  function onMultiFilePicked(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    if (!files || files.length === 0) return;
    viewStore.modelLoading = true;

    const formData = new FormData();
    Array.from(files).forEach((f) => formData.append('files', f));

    uploadFilesApi({
      modelName: modelStore.selectedModel.title,
      modelFolderName: modelStore.modelData.model.modelFolderName,
      formData
    } as never)
      .then(() => notify.positive('File uploaded'))
      .catch((error) => notify.apiError(error));

    viewStore.modelLoading = false;
  }

  function uploadProps() {
    propsInput.click();
  }

  function onPropsFilePicked(event: Event) {
    const files = (event.target as HTMLInputElement).files;
    if (!files || files.length === 0) return;

    const fr = new FileReader();
    fr.onload = (e) => {
      const inputString = e.target?.result as string;
      const filteredString = inputString.match(/\*User([\D\S]*?)\*/gi);
      if (!filteredString) return;

      let propsArray = filteredString[0]!.split(/[\n,]/gi).filter((v) => v.trim() !== '');
      propsArray = propsArray.slice(0, propsArray.length - 1);
      const numConstants = propsArray.length - 2;

      if (!propsArray[1]) {
        console.log('Constants not found.');
        return;
      }
      const numConstantsFound = propsArray[1].match(/\d+/);
      if (!numConstantsFound) {
        console.log('Number of constants not found.');
        return;
      }

      if (parseFloat(numConstantsFound[0]!) === numConstants) {
        materials[0]!.properties = [];
        const parameterString = inputString.match(/\*PARAMETER([\D\S]*?)\*HEADING/gi);
        if (!parameterString) {
          console.log('Parameter string not found.');
          return;
        }
        const parameterValues = parameterString[0]!.match(/\w+=([\d.]+)/gi);
        if (!parameterValues) {
          console.log('Parameter values not found.');
          return;
        }

        for (let i = 2; i < propsArray.length; i++) {
          let propValue = propsArray[i]!.trim();
          if (propValue.startsWith('<') && propValue.endsWith('>')) {
            const paramName = propValue.slice(1, -1);
            const paramValue = parameterValues.find((p) => p.startsWith(`${paramName}=`));
            if (paramValue) propValue = paramValue.split('=')[1]!;
            else console.log(`Parameter ${paramName} not found.`);
          }
          materials[0]!.properties!.push({
            materialsPropId: i - 1,
            name: `Prop_${i - 1}`,
            value: parseFloat(propValue)
          });
        }
      } else {
        console.log('Length of Propsarray unexpected');
      }
    };
    fr.readAsText(files.item(0)!);
  }

  function addMaterial() {
    if (!modelStore.modelData.materials) modelStore.modelData.materials = [];
    const list = modelStore.modelData.materials;
    const len = list.length;
    const newItem =
      len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as Material) : ({} as Material);
    newItem.materialsId = len + 1;
    newItem.name = `Material ${len + 1}`;
    list.push(newItem);
  }

  function removeMaterial(index: number) {
    materials.splice(index, 1);
    materials.forEach((m, i) => (m.materialsId = i + 1));
  }
</script>

<div class="space-y-3 p-3">
  {#if authStore.ready && !canUseLibrary}
    <p class="text-muted-foreground flex flex-wrap items-center gap-1.5 text-xs">
      <Lock class="h-3.5 w-3.5" aria-hidden="true" />
      Save materials to your own library and reuse them across models.
      {#if publicConfig.signupOpen}
        <a href="/auth/login?mode=signup&next=%2Fperihub" class="text-primary underline">
          Create account
        </a>
      {:else}
        <a href="/auth/login?next=%2Fperihub" class="text-primary underline">Log in</a>
      {/if}
    </p>
  {/if}
  {#each materials as material, index (index)}
    <div class="border-border space-y-3 rounded-md border p-3">
      <div class="flex items-center justify-between gap-3">
        <h4 class="truncate font-medium">{material.name || `Material ${material.materialsId}`}</h4>
        <Button
          variant="ghost"
          size="icon"
          onclick={() => removeMaterial(index)}
          title="Remove {material.name}"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      {#if canUseLibrary}
        {@const linked = libraryItem(material.libraryId)}
        <div class="flex flex-wrap items-center gap-2">
          <Select
            class="h-8 w-56"
            aria-label="Load {material.name} from the material library"
            value=""
            onchange={(e) => {
              loadFromLibrary(index, e.currentTarget.value);
              e.currentTarget.value = '';
            }}
          >
            <option value="" disabled>Load from library…</option>
            {#each library as item (item.id)}
              <option value={item.id}>{item.name}</option>
            {/each}
          </Select>
          {#if linked?.can_edit}
            <Button variant="outline" size="sm" onclick={() => saveToLibrary(material)}>
              Save to library
            </Button>
          {/if}
          <Button variant="outline" size="sm" onclick={() => saveAsNew(material)}>
            Save as new
          </Button>
          {#if linked}
            <span class="text-muted-foreground text-xs">From library: {linked.name}</span>
          {/if}
        </div>
      {/if}

      {#snippet userTools()}
        <Button variant="outline" size="sm" onclick={() => uploadProps()}>
          <Upload class="h-4 w-4" /> Upload Property
        </Button>
        <Button variant="outline" size="sm" onclick={uploadSo}>
          <Upload class="h-4 w-4" /> Upload shared Library
        </Button>
        <div class="space-y-1">
          <Label for={`mat-${index}-nsv`}>Number of state variables</Label>
          <Input
            id={`mat-${index}-nsv`}
            type="number"
            bind:value={material.numStateVars}
            oninput={() => editNumStateVars(material.numStateVars!)}
          />
        </div>
      {/snippet}
      <MaterialEditor bind:material={materials[index]!} idPrefix={`mat-${index}`} {userTools} />
    </div>
  {/each}

  <AddButton noun="material" items={materials} onclick={addMaterial} />

  <input
    bind:this={multiSoInput}
    type="file"
    multiple
    accept=".so"
    class="hidden"
    onchange={onMultiFilePicked}
  />
  <input
    bind:this={propsInput}
    type="file"
    multiple
    accept=".inp"
    class="hidden"
    onchange={onPropsFilePicked}
  />
</div>
