<script lang="ts">
  import { Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { BondFilters } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import ParamLabel from '$lib/components/ParamLabel.svelte';
  import SchemaParams from '$lib/components/SchemaParams.svelte';
  import { sections, node, enumOf, pick, CUSTOM_KEYS } from '$lib/perilab/schema';

  const bondFilters = $derived(modelStore.modelData.bondFilters ?? []);

  function addBondFilter() {
    const len = bondFilters.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(bondFilters[len - 1])) as BondFilters)
        : ({ params: { Type: 'Rectangular_Plane' }, show: true } as unknown as BondFilters);
    newItem.bondFiltersId = len + 1;
    newItem.name = `bf_${len + 1}`;
    bondFilters.push(newItem);
  }
</script>

<div class="space-y-3 p-3">
  {#each bondFilters as bondFilter, index (index)}
    <div class="border-border space-y-2 border-b pb-3">
      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`bf-name-${index}`}>Name</Label>
          <Input id={`bf-name-${index}`} bind:value={bondFilter.name} />
        </div>
        <div class="space-y-1">
          <ParamLabel
            key="Type"
            for={`bf-type-${index}`}
            required
            prop={sections.bondFilter?.properties?.Type}
          />
          <Select id={`bf-type-${index}`} bind:value={bondFilter.params!['Type']}>
            {#each pick(enumOf(node(['Type'], sections.bondFilter)), ['Rectangular_Plane', 'Disk'], String(bondFilter.params?.Type ?? '')) as type (type)}
              <option value={type}>{type}</option>
            {/each}
          </Select>
        </div>
        <Toggle bind:checked={bondFilter.show} label="Show" />
        <Button
          variant="ghost"
          size="icon"
          onclick={() => bondFilters.splice(index, 1)}
          title="Remove Bond Filter"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>
      <SchemaParams
        entry={sections.bondFilter}
        values={bondFilter.params!}
        custom={CUSTOM_KEYS.bondFilter}
        idPrefix={`bf-${index}`}
      />
    </div>
  {/each}

  <AddButton noun="bond filter" items={bondFilters} onclick={addBondFilter} />
</div>
