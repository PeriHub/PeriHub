<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { ThermalModel } from '$lib/client';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import ChipGroup from '$lib/components/ui/ChipGroup.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';

  const thermal = $derived(modelStore.modelData.thermal ?? []);
  const thermalModelNames = ['Thermal Flow', 'Heat Transfer', 'Thermal Expansion'];
  const thermalTypes = ['Bond based'];

  function addThermalModel() {
    if (!modelStore.modelData.thermal) modelStore.modelData.thermal = [];
    const list = modelStore.modelData.thermal;
    const len = list.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(list[len - 1])) as ThermalModel)
        : ({} as ThermalModel);
    newItem.thermalModelsId = len + 1;
    newItem.name = `Thermal Model ${len + 1}`;
    list.push(newItem);
  }

  function removeThermalModel(index: number) {
    thermal.splice(index, 1);
    thermal.forEach((m, i) => (m.thermalModelsId = i + 1));
  }
</script>

<div class="space-y-3 p-3">
  {#each thermal as thermalModel, index (index)}
    <div class="border-border space-y-3 rounded-md border p-3">
      <h4 class="font-medium">Thermal {thermalModel.thermalModelsId}</h4>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`th-name-${index}`}>Name</Label>
          <Input id={`th-name-${index}`} bind:value={thermalModel.name} />
        </div>
        <Button
          variant="ghost"
          size="icon"
          onclick={() => removeThermalModel(index)}
          title="Remove Thermal Model"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label>Type</Label>
          <ChipGroup
            ariaLabel="Type of {thermalModel.name}"
            options={thermalModelNames}
            bind:value={thermalModel.thermalModel}
          />
        </div>
        <div class="space-y-1">
          <Label for={`th-type-${index}`}>Bond type</Label>
          <Select id={`th-type-${index}`} bind:value={thermalModel.thermalType}>
            {#each thermalTypes as type (type)}
              <option value={type}>{type}</option>
            {/each}
          </Select>
        </div>
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`th-cond-${index}`}>Thermal conductivity</Label>
          <Input
            id={`th-cond-${index}`}
            type="number"
            bind:value={thermalModel.thermalConductivity}
          />
        </div>
        <div class="space-y-1">
          <Label for={`th-htc-${index}`}>Heat transfer coefficient</Label>
          <Input
            id={`th-htc-${index}`}
            type="number"
            bind:value={thermalModel.heatTransferCoefficient}
          />
        </div>
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`th-exp-${index}`}>Thermal expansion coefficient</Label>
          <Input
            id={`th-exp-${index}`}
            type="number"
            bind:value={thermalModel.thermalExpansionCoefficient}
          />
        </div>
        <div class="space-y-1">
          <Label for={`th-env-${index}`}>Environmental temperature</Label>
          <Input
            id={`th-env-${index}`}
            type="number"
            bind:value={thermalModel.environmentalTemperature}
          />
        </div>
      </div>

      <h5 class="text-muted-foreground text-sm font-medium">Additive</h5>
      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`th-pbt-${index}`}>Print bed temperature</Label>
          <Input
            id={`th-pbt-${index}`}
            type="number"
            bind:value={thermalModel.printBedTemperature}
          />
        </div>
        <div class="space-y-1">
          <Label for={`th-pbc-${index}`}>Thermal conductivity print bed</Label>
          <Input
            id={`th-pbc-${index}`}
            type="number"
            bind:value={thermalModel.thermalConductivityPrintBed}
          />
        </div>
        <div class="space-y-1">
          <Label for={`th-pbz-${index}`}>Print bed Z coordinate</Label>
          <Input id={`th-pbz-${index}`} type="number" bind:value={thermalModel.printBedZCoord} />
        </div>
      </div>

      <h5 class="text-muted-foreground text-sm font-medium">HETVAL</h5>
      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`th-file-${index}`}>File</Label>
          <Input id={`th-file-${index}`} bind:value={thermalModel.file} />
        </div>
        <div class="space-y-1">
          <Label for={`th-nsv-${index}`}>Number of state variables</Label>
          <Input id={`th-nsv-${index}`} type="number" bind:value={thermalModel.numStateVars} />
        </div>
        <div class="space-y-1">
          <Label for={`th-pfn-${index}`}>Predefined field names</Label>
          <Input id={`th-pfn-${index}`} bind:value={thermalModel.predefinedFieldNames} />
        </div>
      </div>
    </div>
  {/each}

  <AddButton noun="thermal model" items={thermal} onclick={addThermalModel} />
</div>
