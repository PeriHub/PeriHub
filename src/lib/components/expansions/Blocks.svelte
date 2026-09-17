<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const model = $derived(modelStore.modelData.model);
  const materials = $derived(modelStore.modelData.materials ?? []);
  const damages = $derived(modelStore.modelData.damages ?? []);
  const thermal = $derived(modelStore.modelData.thermal);
  const additive = $derived(modelStore.modelData.additive);
  const blocks = $derived(modelStore.modelData.blocks ?? []);

  function showBlock() {
    bus.emit('resetData');
  }

  function addBlock() {
    const len = blocks.length;
    const newItem =
      len > 0 ? structuredClone($state.snapshot(blocks[len - 1])) : ({} as (typeof blocks)[number]);
    newItem.blocksId = len + 1;
    newItem.name = `block_${len + 1}`;
    blocks.push(newItem);
  }

  function removeBlock(index: number) {
    blocks.splice(index, 1);
    blocks.forEach((block, i) => (block.blocksId = i + 1));
  }
</script>

<div class="space-y-3 p-3">
  {#each blocks as block, index (block.blocksId ?? index)}
    <div class="flex flex-wrap items-end gap-3 border-b border-border pb-3">
      <div class="w-28 space-y-1">
        <Label for={`blk-name-${index}`}>Block Name</Label>
        <Input id={`blk-name-${index}`} bind:value={block.name} />
      </div>
      <div class="space-y-1">
        <Label for={`blk-mat-${index}`}>Material</Label>
        <Select id={`blk-mat-${index}`} bind:value={block.material}>
          <option value={undefined}>—</option>
          {#each materials as material, materialIdx (material.name ?? materialIdx)}
            <option value={material.name}>{material.name}</option>
          {/each}
        </Select>
      </div>
      <div class="space-y-1">
        <Label for={`blk-dmg-${index}`}>Damage Model</Label>
        <Select id={`blk-dmg-${index}`} bind:value={block.damageModel}>
          <option value={undefined}>—</option>
          {#each damages as damage, damageIdx (damage.name ?? damageIdx)}
            <option value={damage.name}>{damage.name}</option>
          {/each}
        </Select>
      </div>
      {#if thermal.enabled}
        <div class="space-y-1">
          <Label for={`blk-therm-${index}`}>Thermal Model</Label>
          <Select id={`blk-therm-${index}`} bind:value={block.thermalModel}>
            <option value={undefined}>—</option>
            {#each thermal.thermalModels ?? [] as t, tIdx (t.name ?? tIdx)}
              <option value={t.name}>{t.name}</option>
            {/each}
          </Select>
        </div>
      {/if}
      {#if additive.enabled}
        <div class="space-y-1">
          <Label for={`blk-add-${index}`}>Additive Model</Label>
          <Select id={`blk-add-${index}`} bind:value={block.additiveModel}>
            <option value={undefined}>—</option>
            {#each additive.additiveModels ?? [] as a, aIdx (a.name ?? aIdx)}
              <option value={a.name}>{a.name}</option>
            {/each}
          </Select>
        </div>
      {/if}
      <div class="w-28 space-y-1">
        <Label for={`blk-dens-${index}`}>Density</Label>
        <Input id={`blk-dens-${index}`} type="number" bind:value={block.density} />
      </div>
      <div class="w-32 space-y-1">
        <Label for={`blk-shc-${index}`}>Specific Heat Capacity</Label>
        <Input id={`blk-shc-${index}`} type="number" bind:value={block.specificHeatCapacity} />
      </div>
      {#if model.ownModel}
        <div class="w-28 space-y-1">
          <Label for={`blk-hor-${index}`}>Horizon</Label>
          <Input id={`blk-hor-${index}`} type="number" bind:value={block.horizon} />
        </div>
      {/if}
      <Toggle bind:checked={block.show} label="Show" onCheckedChange={showBlock} />
      {#if model.ownModel}
        <Button variant="ghost" size="icon" onclick={() => removeBlock(block.blocksId - 1)} title="Remove block">
          <Trash2 class="h-4 w-4" />
        </Button>
      {/if}
    </div>
  {/each}

  {#if model.ownModel}
    <Button variant="outline" size="sm" onclick={addBlock}>
      <Plus class="h-4 w-4" /> Add block
    </Button>
  {/if}
</div>
