<script lang="ts">
  import { Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { ThermalModel } from '$lib/client';
  import Input from '$lib/components/ui/Input.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import ChipGroup from '$lib/components/ui/ChipGroup.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import ParamLabel from '$lib/components/ParamLabel.svelte';
  import SchemaParams from '$lib/components/SchemaParams.svelte';
  import {
    sections,
    modelNames,
    pick,
    splitModels,
    joinModels,
    CUSTOM_KEYS
  } from '$lib/perilab/schema';

  const thermal = $derived(modelStore.modelData.thermal ?? []);

  function addThermalModel() {
    if (!modelStore.modelData.thermal) modelStore.modelData.thermal = [];
    const list = modelStore.modelData.thermal;
    const len = list.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(list[len - 1])) as ThermalModel)
        : ({ params: { 'Thermal Model': 'Thermal Flow' } } as unknown as ThermalModel);
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

      <div class="space-y-1">
        <ParamLabel
          key="Thermal Model"
          for={`th-models-${index}`}
          required
          prop={sections.thermal?.properties?.['Thermal Model']}
        />
        <ChipGroup
          ariaLabel="Thermal Model of {thermalModel.name}"
          options={pick(
            modelNames(sections.thermal),
            ['Thermal Flow', 'Heat Transfer', 'Thermal Expansion'],
            splitModels(thermalModel.params?.['Thermal Model'])
          )}
          bind:value={
            () => splitModels(thermalModel.params?.['Thermal Model']),
            (v) => {
              const joined = joinModels(v ?? []);
              if (joined) thermalModel.params!['Thermal Model'] = joined;
              else delete thermalModel.params!['Thermal Model'];
            }
          }
        />
      </div>

      <SchemaParams
        entry={sections.thermal}
        values={thermalModel.params!}
        names={splitModels(thermalModel.params?.['Thermal Model'])}
        custom={CUSTOM_KEYS.thermal}
        idPrefix={`th-${index}`}
      />
    </div>
  {/each}

  <AddButton noun="thermal model" items={thermal} onclick={addThermalModel} />
</div>
