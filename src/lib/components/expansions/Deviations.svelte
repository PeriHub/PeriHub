<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Plus, Trash2 } from 'lucide-svelte';
  import { defaultStore } from '$lib/stores/default-store.svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { Parameter, OldParameter } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const deviations = $derived(modelStore.modelData.deviations);
  let parameters = $state<string[]>(['materials[0].youngsModulus']);

  function isObject(val: unknown): val is Record<string, unknown> {
    return val != null && typeof val === 'object' && !Array.isArray(val);
  }

  function objleaves(obj: unknown, prefix = '', acc: string[] = []): string[] {
    if (Array.isArray(obj) || isObject(obj)) {
      const entries = Array.isArray(obj) ? obj.entries() : Object.entries(obj);
      for (const [k, v] of entries) {
        const path = prefix ? (Array.isArray(obj) ? `${prefix}[${k}]` : `${prefix}.${k}`) : String(k);
        if (Array.isArray(v) || isObject(v)) {
          objleaves(v, path, acc);
        } else {
          acc.push(path);
        }
      }
    }
    return acc;
  }

  function getAllParameters() {
    parameters = objleaves(modelStore.modelData);
  }

  function addParameter() {
    if (!deviations.parameters) deviations.parameters = [];
    const list = deviations.parameters;
    const len = list.length;
    const newItem = len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as Parameter) : ({} as Parameter);
    newItem.parameterId = len + 1;
    list.push(newItem);
  }

  function removeParameter(index: number) {
    deviations.parameters.splice(index, 1);
    deviations.parameters.forEach((p, i) => (p.parameterId = i + 1));
  }

  function addOldParameter() {
    if (!deviations.oldParameters) deviations.oldParameters = [];
    const list = deviations.oldParameters;
    const len = list.length;
    const newItem = len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as Parameter) : ({} as Parameter);
    newItem.parameterId = len + 1;
    list.push(newItem);
  }

  function removeOldParameter(index: number) {
    deviations.oldParameters!.splice(index, 1);
    deviations.oldParameters!.forEach((p, i) => (p.parameterId = i + 1));
  }

  onMount(getAllParameters);
</script>

<div class="space-y-3 p-3">
  <Toggle bind:checked={deviations.enabled} label="Enabled" disabled={defaultStore.trial} />

  {#if deviations.enabled}
    <div class="space-y-1">
      <Label for="dev-samplesize">sampleSize</Label>
      <Input id="dev-samplesize" type="number" bind:value={deviations.sampleSize} />
    </div>

    <Toggle bind:checked={deviations.fileInput} label="Additional txt Input" />

    {#if deviations.fileInput}
      <div class="space-y-1">
        <Label for="dev-file">File</Label>
        <Input id="dev-file" bind:value={deviations.file} />
      </div>

      {#each deviations.oldParameters ?? [] as parameter, index (parameter.parameterId ?? index)}
        <div class="flex flex-wrap items-end gap-3 border-b border-border pb-2">
          <div class="w-56 space-y-1">
            <Label for={`dev-old-id-${index}`}>Id</Label>
            <select
              id={`dev-old-id-${index}`}
              multiple
              bind:value={parameter.id}
              class="h-20 w-full rounded-md border border-input bg-background px-2 py-1 text-sm"
            >
              {#each parameters as p (p)}
                <option value={p}>{p}</option>
              {/each}
            </select>
          </div>
          <div class="space-y-1">
            <Label for={`dev-old-factor-${index}`}>Factor</Label>
            <Input id={`dev-old-factor-${index}`} type="number" bind:value={parameter.factor} />
          </div>
          <Button variant="ghost" size="icon" onclick={() => removeOldParameter(index)} title="Remove parameter">
            <Trash2 class="h-4 w-4" />
          </Button>
        </div>
      {/each}
      <Button variant="outline" size="sm" onclick={addOldParameter}>
        <Plus class="h-4 w-4" /> Add parameter
      </Button>
    {/if}

    <div class="border-t border-border pt-3"></div>

    {#each deviations.parameters ?? [] as parameter, index (parameter.parameterId ?? index)}
      <div class="flex flex-wrap items-end gap-3 border-b border-border pb-2">
        <div class="w-56 space-y-1">
          <Label for={`dev-id-${index}`}>Id</Label>
          <select
            id={`dev-id-${index}`}
            multiple
            bind:value={parameter.id}
            class="h-20 w-full rounded-md border border-input bg-background px-2 py-1 text-sm"
          >
            {#each parameters as p (p)}
              <option value={p}>{p}</option>
            {/each}
          </select>
        </div>
        <div class="space-y-1">
          <Label for={`dev-std-${index}`}>Std</Label>
          <Input id={`dev-std-${index}`} type="number" bind:value={parameter.std} />
        </div>
        <Button variant="ghost" size="icon" onclick={() => removeParameter(index)} title="Remove parameter">
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>
    {/each}
    <Button variant="outline" size="sm" onclick={addParameter}>
      <Plus class="h-4 w-4" /> Add parameter
    </Button>
  {/if}
</div>
