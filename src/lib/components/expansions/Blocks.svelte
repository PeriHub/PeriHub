<script lang="ts">
  import { SlidersHorizontal, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import { previewHighlight } from '$lib/utils/preview-highlight';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import { sections, CUSTOM_KEYS } from '$lib/perilab/schema';
  import SchemaParams from '$lib/components/SchemaParams.svelte';

  const model = $derived(modelStore.modelData.model);
  const uploaded = $derived(model.meshSource === 'upload');
  const materials = $derived(modelStore.modelData.materials ?? []);
  const damages = $derived(modelStore.modelData.damages ?? []);
  const thermal = $derived(modelStore.modelData.thermal ?? []);
  const additive = $derived(modelStore.modelData.additive ?? []);
  const blocks = $derived(modelStore.modelData.blocks ?? []);

  let expanded = $state<boolean[]>([]);
  // Must match the header: an oversized colspan adds phantom columns to the table-fixed grid.
  const columnCount = $derived(
    5 + (thermal.length ? 2 : 0) + (additive.length ? 1 : 0) + (uploaded ? 2 : 0)
  );

  function addBlock() {
    const len = blocks.length;
    const newItem =
      len > 0
        ? structuredClone($state.snapshot(blocks[len - 1]))
        : ({ params: {} } as (typeof blocks)[number]);
    newItem.blocksId = len + 1;
    newItem.name = `block_${len + 1}`;
    blocks.push(newItem);
  }

  function removeBlock(index: number) {
    blocks.splice(index, 1);
    expanded.splice(index, 1);
    blocks.forEach((block, i) => (block.blocksId = i + 1));
  }
</script>

<div class="space-y-3 p-3">
  <div class="overflow-x-auto">
    <table class="w-full min-w-[32rem] table-fixed border-collapse text-sm">
      <thead>
        <tr class="text-muted-foreground text-left text-xs">
          <th class="px-1 pb-1 font-medium">Name</th>
          <th class="px-1 pb-1 font-medium">Material Model</th>
          <th class="px-1 pb-1 font-medium">Damage Model</th>
          {#if thermal.length}<th class="px-1 pb-1 font-medium">Thermal Model</th>{/if}
          {#if additive.length}<th class="px-1 pb-1 font-medium">Additive Model</th>{/if}
          <th class="px-1 pb-1 font-medium">Density</th>
          {#if thermal.length}<th class="px-1 pb-1 font-medium">Specific Heat Capacity</th>{/if}
          {#if uploaded}<th class="px-1 pb-1 font-medium">Horizon</th>{/if}
          <th class="w-11"><span class="sr-only">PeriLab parameters</span></th>
          {#if uploaded}<th class="w-11"><span class="sr-only">Remove</span></th>{/if}
        </tr>
      </thead>
      <tbody>
        {#each blocks as block, index (index)}
          <tr
            class="border-border hover:bg-muted/50 border-t"
            {...previewHighlight(() => ({ block: block.blocksId }))}
          >
            <td class="p-0.5">
              <Input
                class="h-8 [appearance:textfield] px-2 text-[13px] [&::-webkit-inner-spin-button]:appearance-none"
                aria-label="Name of block {block.blocksId}"
                bind:value={block.name}
              />
            </td>
            <td class="p-0.5">
              <Select
                class="h-8 pr-6 pl-2 text-[13px]"
                aria-label="Material of {block.name}"
                bind:value={block.params!['Material Model']}
                onchange={(e) => {
                  if (!e.currentTarget.value) delete block.params!['Material Model'];
                }}
              >
                <option value={undefined}>—</option>
                {#each materials as material, materialIdx (materialIdx)}
                  <option value={material.name}>{material.name}</option>
                {/each}
              </Select>
            </td>
            <td class="p-0.5">
              <Select
                class="h-8 pr-6 pl-2 text-[13px]"
                aria-label="Damage model of {block.name}"
                bind:value={block.params!['Damage Model']}
                onchange={(e) => {
                  if (!e.currentTarget.value) delete block.params!['Damage Model'];
                }}
              >
                <option value={undefined}>—</option>
                {#each damages as damage, damageIdx (damageIdx)}
                  <option value={damage.name}>{damage.name}</option>
                {/each}
              </Select>
            </td>
            {#if thermal.length}
              <td class="p-0.5">
                <Select
                  class="h-8 pr-6 pl-2 text-[13px]"
                  aria-label="Thermal model of {block.name}"
                  bind:value={block.params!['Thermal Model']}
                  onchange={(e) => {
                    if (!e.currentTarget.value) delete block.params!['Thermal Model'];
                  }}
                >
                  <option value={undefined}>—</option>
                  {#each thermal as t, tIdx (tIdx)}
                    <option value={t.name}>{t.name}</option>
                  {/each}
                </Select>
              </td>
            {/if}
            {#if additive.length}
              <td class="p-0.5">
                <Select
                  class="h-8 pr-6 pl-2 text-[13px]"
                  aria-label="Additive model of {block.name}"
                  bind:value={block.params!['Additive Model']}
                  onchange={(e) => {
                    if (!e.currentTarget.value) delete block.params!['Additive Model'];
                  }}
                >
                  <option value={undefined}>—</option>
                  {#each additive as a, aIdx (aIdx)}
                    <option value={a.name}>{a.name}</option>
                  {/each}
                </Select>
              </td>
            {/if}
            <td class="p-0.5">
              <Input
                class={`h-8 [appearance:textfield] px-2 text-[13px] [&::-webkit-inner-spin-button]:appearance-none${block.params?.Density == null ? ' border-destructive' : ''}`}
                type="number"
                aria-label="Density of {block.name}"
                aria-required="true"
                bind:value={block.params!['Density']}
              />
            </td>
            {#if thermal.length}
              <td class="p-0.5">
                <Input
                  class="h-8 [appearance:textfield] px-2 text-[13px] [&::-webkit-inner-spin-button]:appearance-none"
                  type="number"
                  aria-label="Specific heat capacity of {block.name}"
                  title="Specific heat capacity"
                  bind:value={block.params!['Specific Heat Capacity']}
                />
              </td>
            {/if}
            {#if uploaded}
              <td class="p-0.5">
                <Input
                  class={`h-8 [appearance:textfield] px-2 text-[13px] [&::-webkit-inner-spin-button]:appearance-none${block.params?.Horizon == null ? ' border-destructive' : ''}`}
                  type="number"
                  aria-label="Horizon of {block.name}"
                  aria-required="true"
                  bind:value={block.params!['Horizon']}
                />
              </td>
            {/if}
            <td class="p-0.5">
              <Button
                variant="ghost"
                size="icon"
                onclick={() => (expanded[index] = !expanded[index])}
                title="PeriLab parameters of {block.name}"
                aria-expanded={expanded[index] ?? false}
              >
                <SlidersHorizontal class="h-4 w-4" />
              </Button>
            </td>
            {#if uploaded}
              <td class="p-0.5">
                <Button
                  variant="ghost"
                  size="icon"
                  onclick={() => removeBlock(block.blocksId - 1)}
                  title="Remove {block.name}"
                >
                  <Trash2 class="h-4 w-4" />
                </Button>
              </td>
            {/if}
          </tr>
          {#if expanded[index]}
            <tr>
              <td colspan={columnCount} class="p-2">
                <SchemaParams
                  entry={sections.block}
                  values={block.params!}
                  custom={CUSTOM_KEYS.block}
                  idPrefix={`blk-${index}`}
                />
              </td>
            </tr>
          {/if}
        {/each}
      </tbody>
    </table>
  </div>

  {#if uploaded}
    <AddButton noun="block" items={blocks} onclick={addBlock} />
  {/if}
</div>
