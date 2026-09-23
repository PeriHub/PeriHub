<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { bus } from '$lib/utils/bus';
  import type { Compute, Output } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const blocks = $derived(modelStore.modelData.blocks ?? []);
  const nodeSets = $derived(modelStore.modelData.discretization?.nodeSets ?? []);
  const computes = $derived(modelStore.modelData.computes ?? []);
  const outputs = $derived(modelStore.modelData.outputs ?? []);

  const fileTypes = ['Exodus', 'CSV'];
  const computeClasses = ['Block_Data', 'Node_Set_Data', 'Nearest_Point_Data'];
  const calculationTypes = ['Sum', 'Maximum', 'Minimum'];
  const variables = ['Forces', 'Displacements', 'Damage', 'Temperature'];

  let outputKeys = $state([
    'Displacements', 'Damage', 'Forces', 'Number of Neighbors', 'Number of Filtered Neighbors',
    'Activation_Time', 'Temperature', 'Heat Flow', 'Active', 'Specific Volume', 'Strain',
    'Cauchy Stress', 'von Mises Stress', 'Angles', 'Orientations', 'Contact Nodes'
  ]);

  function addStateVarsToOutput(numStateVars: number) {
    for (let i = 1; i <= numStateVars; i++) {
      const name = `State_Parameter_Field_${i}`;
      if (!outputKeys.includes(name)) outputKeys.push(name);
    }
  }

  function addCompute() {
    if (!modelStore.modelData.computes) modelStore.modelData.computes = [];
    const list = modelStore.modelData.computes;
    const len = list.length;
    const newItem = len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as Compute) : ({} as Compute);
    newItem.computesId = len + 1;
    newItem.name = `Compute${len + 1}`;
    list.push(newItem);
  }

  function removeCompute(index: number) {
    computes.splice(index, 1);
    computes.forEach((c, i) => (c.computesId = i + 1));
  }

  function addOutput() {
    const len = outputs.length;
    outputs.push({
      outputsId: len + 1,
      name: `Output${len + 1}`,
      selectedOutputs: [],
      Write_After_Damage: false,
      InitStep: 0
    } as Output);
  }

  function removeOutput(index: number) {
    outputs.splice(index, 1);
    outputs.forEach((o, i) => (o.outputsId = i + 1));
  }

  onMount(() => {
    bus.on('addStateVarsToOutput' as never, addStateVarsToOutput as never);
    return () => bus.off('addStateVarsToOutput' as never, addStateVarsToOutput as never);
  });
</script>

<div class="space-y-3 p-3">
  <h4 class="text-sm font-medium text-muted-foreground">Compute Parameters (Global Variables)</h4>

  {#each computes as compute, index (compute.computesId ?? index)}
    <div class="space-y-2 border-b border-border pb-3">
      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`cp-name-${index}`}>Output Label</Label>
          <Input id={`cp-name-${index}`} bind:value={compute.name} />
        </div>
        <div class="space-y-1">
          <Label for={`cp-class-${index}`}>Compute Class</Label>
          <Select id={`cp-class-${index}`} bind:value={compute.computeClass}>
            {#each computeClasses as c (c)}
              <option value={c}>{c}</option>
            {/each}
          </Select>
        </div>
        <div class="space-y-1">
          <Label for={`cp-var-${index}`}>Variable</Label>
          <Select id={`cp-var-${index}`} bind:value={compute.variable}>
            {#each variables as v (v)}
              <option value={v}>{v}</option>
            {/each}
          </Select>
        </div>
        <div class="space-y-1">
          <Label for={`cp-eq-${index}`}>Equation</Label>
          <Input id={`cp-eq-${index}`} bind:value={compute.equation} />
        </div>
      </div>

      {#if compute.computeClass === 'Block_Data'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`cp-calc-${index}`}>Calculation Type</Label>
            <Select id={`cp-calc-${index}`} bind:value={compute.calculationType}>
              {#each calculationTypes as c (c)}
                <option value={c}>{c}</option>
              {/each}
            </Select>
          </div>
          <div class="space-y-1">
            <Label for={`cp-block-${index}`}>Block</Label>
            <Select id={`cp-block-${index}`} bind:value={compute.blockName}>
              {#each blocks as block, blockIdx (block.name ?? blockIdx)}
                <option value={block.name}>{block.name}</option>
              {/each}
            </Select>
          </div>
        </div>
      {:else if compute.computeClass === 'Node_Set_Data'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`cp-calc2-${index}`}>Calculation Type</Label>
            <Select id={`cp-calc2-${index}`} bind:value={compute.calculationType}>
              {#each calculationTypes as c (c)}
                <option value={c}>{c}</option>
              {/each}
            </Select>
          </div>
          <div class="space-y-1">
            <Label for={`cp-ns-${index}`}>Node Set Id</Label>
            <Select id={`cp-ns-${index}`} bind:value={compute.nodeSetId}>
              {#each nodeSets as ns, nsIndex (ns.nodeSetId ?? nsIndex)}
                <option value={ns.nodeSetId}>{ns.nodeSetId}</option>
              {/each}
            </Select>
          </div>
        </div>
      {:else if compute.computeClass === 'Nearest_Point_Data'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`cp-x-${index}`}>X</Label>
            <Input id={`cp-x-${index}`} type="number" bind:value={compute.xValue} />
          </div>
          <div class="space-y-1">
            <Label for={`cp-y-${index}`}>Y</Label>
            <Input id={`cp-y-${index}`} type="number" bind:value={compute.yValue} />
          </div>
          <div class="space-y-1">
            <Label for={`cp-z-${index}`}>Z</Label>
            <Input id={`cp-z-${index}`} type="number" bind:value={compute.zValue} />
          </div>
        </div>
      {/if}

      <Button variant="ghost" size="icon" onclick={() => removeCompute(index)} title="Remove Compute">
        <Trash2 class="h-4 w-4" />
      </Button>
    </div>
  {/each}

  <Button variant="outline" size="sm" onclick={addCompute}>
    <Plus class="h-4 w-4" /> Add Compute
  </Button>

  <div class="border-t border-border pt-3"></div>

  {#each outputs as output, index (output.outputsId ?? index)}
    <div class="space-y-2 rounded-md border border-border p-3">
      <h4 class="font-medium">Output {output.outputsId}</h4>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`out-name-${index}`}>Output Name</Label>
          <Input id={`out-name-${index}`} bind:value={output.name} />
        </div>
        <Button variant="ghost" size="icon" onclick={() => removeOutput(index)} title="Remove Output">
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <div class="w-56 space-y-1">
          <Label for={`out-sel-${index}`}>Selected Outputs</Label>
          <select
            id={`out-sel-${index}`}
            multiple
            bind:value={output.selectedOutputs}
            class="h-24 w-full rounded-md border border-input bg-background px-2 py-1 text-sm"
          >
            {#if output.selectedFileType === 'CSV'}
              {#each computes as c, cIdx (c.name ?? cIdx)}
                <option value={c.name}>{c.name}</option>
              {/each}
            {:else}
              {#each outputKeys as key (key)}
                <option value={key}>{key}</option>
              {/each}
            {/if}
          </select>
        </div>
        <div class="space-y-1">
          <Label for={`out-type-${index}`}>File Type</Label>
          <Select
            id={`out-type-${index}`}
            bind:value={output.selectedFileType}
            onchange={() => (output.selectedOutputs = [])}
          >
            {#each fileTypes as t (t)}
              <option value={t}>{t}</option>
            {/each}
          </Select>
        </div>
        <Toggle bind:checked={output.useOutputFrequency} label="Use Output Frequency" />
        {#if output.useOutputFrequency}
          <div class="space-y-1">
            <Label for={`out-freq-${index}`}>Output Frequency</Label>
            <Input id={`out-freq-${index}`} type="number" bind:value={output.Frequency} />
          </div>
        {:else}
          <div class="space-y-1">
            <Label for={`out-numsteps-${index}`}>Number of Outputs</Label>
            <Input id={`out-numsteps-${index}`} type="number" bind:value={output.numberOfOutputSteps} />
          </div>
        {/if}
        <div class="space-y-1">
          <Label for={`out-init-${index}`}>Initial Output Step</Label>
          <Input id={`out-init-${index}`} type="number" bind:value={output.InitStep} />
        </div>
        <Toggle bind:checked={output.Write_After_Damage} label="Write After Damage" />
      </div>
    </div>
  {/each}

  <Button variant="outline" size="sm" onclick={addOutput}>
    <Plus class="h-4 w-4" /> Add Output
  </Button>
</div>
