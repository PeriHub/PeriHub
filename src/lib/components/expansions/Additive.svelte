<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import type { Additive } from '$lib/client';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const additive = $derived(modelStore.modelData.additive ?? ({} as Additive));
  const additiveTypes = ['Simple'];

  function addAdditiveModel() {
    if (!additive.additiveModels) additive.additiveModels = [];
    const list = additive.additiveModels;
    const len = list.length;
    const newItem =
      len > 0 ? structuredClone($state.snapshot(list[len - 1])) : ({} as (typeof list)[number]);
    newItem.additiveModelId = len + 1;
    newItem.name = `Additive Model ${len + 1}`;
    list.push(newItem);
  }

  function removeAdditiveModel(index: number) {
    additive.additiveModels!.splice(index, 1);
    additive.additiveModels!.forEach((model, i) => (model.additiveModelId = i + 1));
  }
</script>

<div class="space-y-3 p-3">
  <Toggle bind:checked={additive.enabled} label="Enabled" />

  {#if additive.enabled}
    <div class="border-border space-y-3 border-t pt-3">
      {#each additive.additiveModels ?? [] as model, index (model.additiveModelId ?? index)}
        <div class="border-border flex flex-wrap items-end gap-3 border-b pb-3">
          <div class="space-y-1">
            <Label for={`add-name-${index}`}>Name</Label>
            <Input id={`add-name-${index}`} bind:value={model.name} />
          </div>
          <div class="space-y-1">
            <Label for={`add-type-${index}`}>Type</Label>
            <Select id={`add-type-${index}`} bind:value={model.additiveType}>
              {#each additiveTypes as type (type)}
                <option value={type}>{type}</option>
              {/each}
            </Select>
          </div>
          <div class="space-y-1">
            <Label for={`add-temp-${index}`}>Print Temperature</Label>
            <Input id={`add-temp-${index}`} type="number" bind:value={model.printTemp} />
          </div>
          <Button
            variant="ghost"
            size="icon"
            onclick={() => removeAdditiveModel(index)}
            title="Remove additive model"
          >
            <Trash2 class="h-4 w-4" />
          </Button>
        </div>
      {/each}

      <Button variant="outline" size="sm" onclick={addAdditiveModel}>
        <Plus class="h-4 w-4" /> Add additive model
      </Button>
    </div>
  {/if}
</div>
