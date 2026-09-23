<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import type { BoundaryCondition, Discretization } from '$lib/client';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const model = $derived(modelStore.modelData.model);
  const blocks = $derived(modelStore.modelData.blocks ?? []);
  const solvers = $derived(modelStore.modelData.solvers ?? []);
  const boundaryConditions = $derived(modelStore.modelData.boundaryConditions);
  const discretization = $derived(modelStore.modelData.discretization ?? ({} as Discretization));

  const boundaryTypes = ['Dirichlet', 'Initial'];
  const boundaryVariables = [
    'Displacements',
    'Force Densities',
    'Forces',
    'Temperature',
    'Damage',
    'Velocity'
  ];
  const coordinates = ['x', 'y', 'z'];

  function addCondition() {
    if (!boundaryConditions.conditions) boundaryConditions.conditions = [];
    const list = boundaryConditions.conditions;
    const len = list.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(list[len - 1])) as BoundaryCondition)
        : ({} as BoundaryCondition);
    newItem.conditionsId = len + 1;
    newItem.name = `BC_${len + 1}`;
    newItem.blockId = len + 1;
    list.push(newItem);
  }

  function removeCondition(index: number) {
    boundaryConditions.conditions.splice(index, 1);
    boundaryConditions.conditions.forEach((c, i) => (c.conditionsId = i + 1));
  }

  onMount(() => {
    bus.on('addCondition' as never, addCondition);
    return () => bus.off('addCondition' as never, addCondition);
  });
</script>

<div class="space-y-3 p-3">
  {#each boundaryConditions.conditions ?? [] as condition, index (condition.conditionsId ?? index)}
    <div class="border-border space-y-2 border-b pb-3">
      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`bc-name-${index}`}>name</Label>
          <Input id={`bc-name-${index}`} bind:value={condition.name} />
        </div>
        <div class="space-y-1">
          <Label for={`bc-type-${index}`}>Type</Label>
          <Select id={`bc-type-${index}`} bind:value={condition.boundarytype}>
            {#each boundaryTypes as type (type)}
              <option value={type}>{type}</option>
            {/each}
          </Select>
        </div>
        {#if discretization.nodeSets && discretization.nodeSets.length > 0}
          <div class="w-28 space-y-1">
            <Label for={`bc-nodeset-${index}`}>Node Set</Label>
            <Select id={`bc-nodeset-${index}`} bind:value={condition.nodeSet}>
              {#each discretization.nodeSets as nodeSet, nsIndex (nodeSet.nodeSetId ?? nsIndex)}
                <option value={nodeSet.nodeSetId}>{nodeSet.nodeSetId}</option>
              {/each}
            </Select>
          </div>
        {/if}
        {#if !model.ownModel}
          <div class="w-28 space-y-1">
            <Label for={`bc-block-${index}`}>Block Id</Label>
            <Select id={`bc-block-${index}`} bind:value={condition.blockId}>
              {#each blocks as block, blockIndex (block.blocksId ?? blockIndex)}
                <option value={block.blocksId}>{block.blocksId}</option>
              {/each}
            </Select>
          </div>
        {/if}
        {#if solvers.length > 1}
          <div class="w-32 space-y-1">
            <Label for={`bc-step-${index}`}>Step Id</Label>
            <select
              id={`bc-step-${index}`}
              multiple
              bind:value={condition.stepId}
              class="border-input bg-background h-20 w-full rounded-md border px-2 py-1 text-sm"
            >
              {#each solvers as solver, solverIndex (solver.stepId ?? solverIndex)}
                <option value={solver.stepId}>{solver.stepId}</option>
              {/each}
            </select>
          </div>
        {/if}
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`bc-var-${index}`}>Variable</Label>
          <Select id={`bc-var-${index}`} bind:value={condition.variable}>
            {#each boundaryVariables as v (v)}
              <option value={v}>{v}</option>
            {/each}
          </Select>
        </div>
        <div class="w-28 space-y-1">
          <Label for={`bc-coord-${index}`}>Coordinate</Label>
          <Select id={`bc-coord-${index}`} bind:value={condition.coordinate}>
            {#each coordinates as c (c)}
              <option value={c}>{c}</option>
            {/each}
          </Select>
        </div>
        <div class="space-y-1">
          <Label for={`bc-value-${index}`}>Value</Label>
          <Input id={`bc-value-${index}`} bind:value={condition.value} />
        </div>
        <Button
          variant="ghost"
          size="icon"
          onclick={() => removeCondition(index)}
          title="Remove Condition"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>
    </div>
  {/each}

  <Button variant="outline" size="sm" onclick={addCondition}>
    <Plus class="h-4 w-4" /> Add Condition
  </Button>
</div>
