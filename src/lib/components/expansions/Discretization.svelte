<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { BlockFunction, Gcode, NodeSet } from '$lib/client';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const discretization = $derived(modelStore.modelData.discretization);
  const distributionTypes = ['Neighbor based', 'Node based'];

  function addNodeSet() {
    if (!discretization.nodeSets) discretization.nodeSets = [];
    const list = discretization.nodeSets;
    const len = list.length;
    const newItem = len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as NodeSet) : ({} as NodeSet);
    newItem.nodeSetId = len + 1;
    list.push(newItem);
  }

  function removeNodeSet(index: number) {
    if (!discretization.nodeSets) return;
    discretization.nodeSets.splice(index, 1);
    discretization.nodeSets.forEach((n, i) => (n.nodeSetId = i + 1));
  }

  function addBlockFunction() {
    if (!discretization.gcode) discretization.gcode = {} as Gcode;
    if (!discretization.gcode.blockFunctions) discretization.gcode.blockFunctions = [];
    const list = discretization.gcode.blockFunctions;
    const len = list.length;
    const newItem =
      len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as BlockFunction) : ({} as BlockFunction);
    newItem.id = len + 1;
    list.push(newItem);
  }

  function removeBlockFunction(index: number) {
    if (!discretization.gcode?.blockFunctions) return;
    discretization.gcode.blockFunctions.splice(index, 1);
    discretization.gcode.blockFunctions.forEach((b, i) => (b.id = i + 1));
  }
</script>

<div class="space-y-3 p-3">
  <div class="max-w-xs space-y-1">
    <Label for="disc-type">Distribution Type</Label>
    <Select id="disc-type" bind:value={discretization.distributionType}>
      {#each distributionTypes as type (type)}
        <option value={type}>{type}</option>
      {/each}
    </Select>
  </div>

  {#each discretization.nodeSets ?? [] as nodeSet, index (nodeSet.nodeSetId ?? index)}
    <div class="flex items-end gap-2 border-b border-border pb-2">
      <div class="flex-1 space-y-1">
        <Label for={`nodeset-${index}`}>Nodeset</Label>
        <Input id={`nodeset-${index}`} bind:value={nodeSet.file} />
      </div>
      <Button variant="ghost" size="icon" onclick={() => removeNodeSet(index)} title="Remove Nodeset">
        <Trash2 class="h-4 w-4" />
      </Button>
    </div>
  {/each}
  <Button variant="outline" size="sm" onclick={addNodeSet}>
    <Plus class="h-4 w-4" /> Add Nodeset
  </Button>

  {#if discretization.discType === 'gcode' && discretization.gcode != null}
    <div class="space-y-3 border-t border-border pt-3">
      <Toggle bind:checked={discretization.gcode.overwriteMesh} label="Overwrite Mesh" />
      <div class="space-y-1">
        <Label for="gcode-sampling">Sampling</Label>
        <Input id="gcode-sampling" type="number" bind:value={discretization.gcode.sampling} />
      </div>
      <div class="space-y-1">
        <Label for="gcode-width">Width</Label>
        <Input id="gcode-width" type="number" bind:value={discretization.gcode.width} />
      </div>
      <div class="space-y-1">
        <Label for="gcode-height">Height</Label>
        <Input id="gcode-height" type="number" bind:value={discretization.gcode.height} />
      </div>
      <div class="space-y-1">
        <Label for="gcode-scale">Scale</Label>
        <Input id="gcode-scale" type="number" bind:value={discretization.gcode.scale} />
      </div>

      {#each discretization.gcode.blockFunctions ?? [] as block, index (block.id ?? index)}
        <div class="flex flex-wrap items-end gap-2 border-b border-border pb-2">
          <div class="space-y-1">
            <Label for={`bf-id-${index}`}>id</Label>
            <Input id={`bf-id-${index}`} type="number" bind:value={block.id} />
          </div>
          <div class="flex-1 space-y-1">
            <Label for={`bf-fn-${index}`}>Function</Label>
            <Input id={`bf-fn-${index}`} bind:value={block.function} />
          </div>
          <Button variant="ghost" size="icon" onclick={() => removeBlockFunction(index)} title="Remove Block Function">
            <Trash2 class="h-4 w-4" />
          </Button>
        </div>
      {/each}
      <Button variant="outline" size="sm" onclick={addBlockFunction}>
        <Plus class="h-4 w-4" /> Add Block Function
      </Button>
    </div>
  {/if}
</div>
