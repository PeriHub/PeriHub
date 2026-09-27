<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import { previewHighlight } from '$lib/utils/preview-highlight';
  import type { BoundaryCondition, Discretization } from '$lib/client';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import ChipGroup from '$lib/components/ui/ChipGroup.svelte';

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
  <div class="overflow-x-auto">
    <table class="w-full min-w-[32rem] table-fixed border-collapse text-sm">
      <thead>
        <tr class="text-muted-foreground text-left text-xs">
          <th class="px-1 pb-1 font-medium">Name</th>
          <th class="w-24 px-1 pb-1 font-medium">Type</th>
          {#if discretization.nodeSets && discretization.nodeSets.length > 0}
            <th class="w-16 px-1 pb-1 font-medium">Node set</th>
          {/if}
          {#if !model.ownModel}<th class="w-16 px-1 pb-1 font-medium">Block ID</th>{/if}
          {#if solvers.length > 1}<th class="px-1 pb-1 font-medium">Steps</th>{/if}
          <th class="w-32 px-1 pb-1 font-medium">Variable</th>
          <th class="w-14 px-1 pb-1 font-medium">Axis</th>
          <th class="px-1 pb-1 font-medium">Value</th>
          <th class="w-11"><span class="sr-only">Remove</span></th>
        </tr>
      </thead>
      <tbody>
        {#each boundaryConditions.conditions ?? [] as condition, index (index)}
          <tr
            class="border-border hover:bg-muted/50 border-t"
            {...previewHighlight(() => ({
              bc: condition.name ?? '',
              block: condition.blockId ?? undefined
            }))}
          >
            <td class="p-0.5">
              <Input
                class="h-8 [appearance:textfield] px-2 text-[13px] [&::-webkit-inner-spin-button]:appearance-none"
                aria-label="Name of condition {index + 1}"
                bind:value={condition.name}
              />
            </td>
            <td class="p-0.5">
              <Select
                class="h-8 pr-6 pl-2 text-[13px]"
                aria-label="Type of {condition.name}"
                bind:value={condition.boundarytype}
              >
                {#each boundaryTypes as type (type)}
                  <option value={type}>{type}</option>
                {/each}
              </Select>
            </td>
            {#if discretization.nodeSets && discretization.nodeSets.length > 0}
              <td class="p-0.5">
                <Select
                  class="h-8 pr-6 pl-2 text-[13px]"
                  aria-label="Node set of {condition.name}"
                  bind:value={condition.nodeSet}
                >
                  {#each discretization.nodeSets as nodeSet, nsIndex (nsIndex)}
                    <option value={nodeSet.nodeSetId}>{nodeSet.nodeSetId}</option>
                  {/each}
                </Select>
              </td>
            {/if}
            {#if !model.ownModel}
              <td class="p-0.5">
                <Select
                  class="h-8 pr-6 pl-2 text-[13px]"
                  aria-label="Block of {condition.name}"
                  bind:value={condition.blockId}
                >
                  {#each blocks as block, blockIndex (blockIndex)}
                    <option value={block.blocksId}>{block.blocksId}</option>
                  {/each}
                </Select>
              </td>
            {/if}
            {#if solvers.length > 1}
              <td class="p-0.5">
                <ChipGroup
                  ariaLabel="Solver steps of {condition.name}"
                  options={solvers.flatMap((s) => (s.stepId != null ? [s.stepId] : []))}
                  bind:value={condition.stepId}
                />
              </td>
            {/if}
            <td class="p-0.5">
              <Select
                class="h-8 pr-6 pl-2 text-[13px]"
                aria-label="Variable of {condition.name}"
                bind:value={condition.variable}
              >
                {#each boundaryVariables as v (v)}
                  <option value={v}>{v}</option>
                {/each}
              </Select>
            </td>
            <td class="p-0.5">
              <Select
                class="h-8 pr-6 pl-2 text-[13px]"
                aria-label="Axis of {condition.name}"
                bind:value={condition.coordinate}
              >
                {#each coordinates as c (c)}
                  <option value={c}>{c}</option>
                {/each}
              </Select>
            </td>
            <td class="p-0.5">
              <Input
                class="h-8 [appearance:textfield] px-2 text-[13px] [&::-webkit-inner-spin-button]:appearance-none"
                aria-label="Value of {condition.name}"
                bind:value={condition.value}
              />
            </td>
            <td class="p-0.5">
              <Button
                variant="ghost"
                size="icon"
                onclick={() => removeCondition(index)}
                title="Remove {condition.name}"
              >
                <Trash2 class="h-4 w-4" />
              </Button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <AddButton noun="condition" items={boundaryConditions.conditions} onclick={addCondition} />
</div>
