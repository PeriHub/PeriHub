<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { BondFilters } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const bondFilters = $derived(modelStore.modelData.bondFilters ?? []);
  const bondFilterTypes = ['Rectangular_Plane', 'Disk'];

  function addBondFilter() {
    const len = bondFilters.length;
    const newItem =
      len > 0 ? (structuredClone($state.snapshot(bondFilters[len - 1])) as BondFilters) : ({} as BondFilters);
    newItem.bondFiltersId = len + 1;
    newItem.name = `bf_${len + 1}`;
    bondFilters.push(newItem);
  }

  function removeBondFilter(index: number) {
    bondFilters.splice(index, 1);
  }
</script>

<div class="space-y-3 p-3">
  {#each bondFilters as bondFilter, index (bondFilter.bondFiltersId ?? index)}
    <div class="space-y-2 border-b border-border pb-3">
      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`bf-name-${index}`}>name</Label>
          <Input id={`bf-name-${index}`} bind:value={bondFilter.name} />
        </div>
        <div class="space-y-1">
          <Label for={`bf-type-${index}`}>Type</Label>
          <Select id={`bf-type-${index}`} bind:value={bondFilter.type}>
            {#each bondFilterTypes as type (type)}
              <option value={type}>{type}</option>
            {/each}
          </Select>
        </div>
        {#if bondFilter.type === 'Rectangular_Plane'}
          <div class="space-y-1">
            <Label for={`bf-bottomlen-${index}`}>Bottom_Length</Label>
            <Input id={`bf-bottomlen-${index}`} type="number" bind:value={bondFilter.bottomLength} />
          </div>
          <div class="space-y-1">
            <Label for={`bf-sidelen-${index}`}>Side_Length</Label>
            <Input id={`bf-sidelen-${index}`} type="number" bind:value={bondFilter.sideLength} />
          </div>
        {:else if bondFilter.type === 'Disk'}
          <div class="space-y-1">
            <Label for={`bf-radius-${index}`}>Radius</Label>
            <Input id={`bf-radius-${index}`} type="number" bind:value={bondFilter.radius} />
          </div>
        {/if}
        <Toggle bind:checked={bondFilter.allow_contact} label="Allow Contact" />
        <Button variant="ghost" size="icon" onclick={() => removeBondFilter(index)} title="Remove Bond Filter">
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`bf-nx-${index}`}>Normal_X</Label>
          <Input id={`bf-nx-${index}`} type="number" bind:value={bondFilter.normalX} />
        </div>
        <div class="space-y-1">
          <Label for={`bf-ny-${index}`}>Normal_Y</Label>
          <Input id={`bf-ny-${index}`} type="number" bind:value={bondFilter.normalY} />
        </div>
        <div class="space-y-1">
          <Label for={`bf-nz-${index}`}>Normal_Z</Label>
          <Input id={`bf-nz-${index}`} type="number" bind:value={bondFilter.normalZ} />
        </div>
        <Toggle bind:checked={bondFilter.show} label="Show" />
      </div>

      {#if bondFilter.type === 'Rectangular_Plane'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`bf-llx-${index}`}>Lower_Left_Corner_X</Label>
            <Input id={`bf-llx-${index}`} type="number" bind:value={bondFilter.lowerLeftCornerX} />
          </div>
          <div class="space-y-1">
            <Label for={`bf-lly-${index}`}>Lower_Left_Corner_Y</Label>
            <Input id={`bf-lly-${index}`} type="number" bind:value={bondFilter.lowerLeftCornerY} />
          </div>
          <div class="space-y-1">
            <Label for={`bf-llz-${index}`}>Lower_Left_Corner_Z</Label>
            <Input id={`bf-llz-${index}`} type="number" bind:value={bondFilter.lowerLeftCornerZ} />
          </div>
        </div>
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`bf-bux-${index}`}>Bottom_Unit_Vector_X</Label>
            <Input id={`bf-bux-${index}`} type="number" bind:value={bondFilter.bottomUnitVectorX} />
          </div>
          <div class="space-y-1">
            <Label for={`bf-buy-${index}`}>Bottom_Unit_Vector_Y</Label>
            <Input id={`bf-buy-${index}`} type="number" bind:value={bondFilter.bottomUnitVectorY} />
          </div>
          <div class="space-y-1">
            <Label for={`bf-buz-${index}`}>Bottom_Unit_Vector_Z</Label>
            <Input id={`bf-buz-${index}`} type="number" bind:value={bondFilter.bottomUnitVectorZ} />
          </div>
        </div>
      {:else if bondFilter.type === 'Disk'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`bf-cx-${index}`}>Center_X</Label>
            <Input id={`bf-cx-${index}`} type="number" bind:value={bondFilter.centerX} />
          </div>
          <div class="space-y-1">
            <Label for={`bf-cy-${index}`}>Center_Y</Label>
            <Input id={`bf-cy-${index}`} type="number" bind:value={bondFilter.centerY} />
          </div>
          <div class="space-y-1">
            <Label for={`bf-cz-${index}`}>Center_Z</Label>
            <Input id={`bf-cz-${index}`} type="number" bind:value={bondFilter.centerZ} />
          </div>
        </div>
      {/if}
    </div>
  {/each}

  <Button variant="outline" size="sm" onclick={addBondFilter}>
    <Plus class="h-4 w-4" /> Add Bond Filter
  </Button>
</div>
