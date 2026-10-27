<script lang="ts">
  import { Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { Damage, InterBlock } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import AddButton from '$lib/components/ui/AddButton.svelte';
  import ParamLabel from '$lib/components/ParamLabel.svelte';
  import SchemaParams from '$lib/components/SchemaParams.svelte';
  import { sections, modelNames, pick, CUSTOM_KEYS } from '$lib/perilab/schema';

  const damages = $derived(modelStore.modelData.damages ?? []);
  const blocks = $derived(modelStore.modelData.blocks ?? []);
  const materials = $derived(modelStore.modelData.materials ?? []);

  function addDamage() {
    const list = (modelStore.modelData.damages ??= []);
    const len = list.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(list[len - 1])) as Damage)
        : ({ name: '', params: { 'Damage Model': 'Critical Stretch' } } as Damage);
    newItem.damagesId = len + 1;
    newItem.name = `Damage${len + 1}`;
    list.push(newItem);
  }

  function removeDamage(index: number) {
    damages.splice(index, 1);
    damages.forEach((d, i) => (d.damagesId = i + 1));
    if (damages.length === 0) blocks.forEach((b) => delete b.params!['Damage Model']);
  }

  function addInterBlock(damage: Damage) {
    const list = (damage.interBlocks ??= []);
    list.push({
      interBlockid: list.length + 1,
      firstBlockId: 1,
      secondBlockId: list.length + 1,
      value: 0
    } as InterBlock);
  }

  // Critical energy from the fracture toughness: G = K1C² / E (plane stress) or K1C² (1 - ν²) / E (plane strain),
  // with E and ν of the material of the first block using this damage model.
  function calculateCriticalEnergy(damage: Damage) {
    const k1c = damage.criticalEnergyCalc?.k1c;
    if (!damage.criticalEnergyCalc?.calculateCriticalEnergy || k1c == null) return;
    const block = blocks.find((b) => b.params?.['Damage Model'] === damage.name);
    const material = materials.find((m) => m.name === block?.params?.['Material Model']);
    const E = Number(material?.params?.["Young's Modulus"]);
    const nu = Number(material?.params?.["Poisson's Ratio"] ?? 0);
    if (!E) return;
    const planeStrain = String(material?.params?.['Symmetry'] ?? '').includes('plane strain');
    damage.params!['Critical Value'] = planeStrain ? (k1c ** 2 * (1 - nu ** 2)) / E : k1c ** 2 / E;
  }
</script>

<div class="space-y-3 p-3">
  {#each damages as damage, index (index)}
    <div class="border-border space-y-3 rounded-md border p-3">
      <div class="flex items-center justify-between">
        <h4 class="font-medium">{damage.name}</h4>
        <Button
          variant="ghost"
          size="icon"
          onclick={() => removeDamage(index)}
          title="Remove Damage Model"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`dm-name-${index}`}>Name</Label>
          <Input id={`dm-name-${index}`} bind:value={damage.name} />
        </div>
        <div class="space-y-1">
          <ParamLabel
            key="Damage Model"
            for={`dm-model-${index}`}
            required
            prop={sections.damage?.properties?.['Damage Model']}
          />
          <Select id={`dm-model-${index}`} bind:value={damage.params!['Damage Model']}>
            {#each pick(modelNames(sections.damage), ['Critical Stretch', 'Critical Energy'], String(damage.params?.['Damage Model'] ?? '')) as name (name)}
              <option value={name}>{name}</option>
            {/each}
          </Select>
        </div>
      </div>

      {#if damage.params?.['Damage Model'] === 'Critical Energy'}
        <div class="flex flex-wrap items-end gap-3">
          <Toggle
            checked={damage.criticalEnergyCalc?.calculateCriticalEnergy ?? false}
            onCheckedChange={(on: boolean) => {
              damage.criticalEnergyCalc ??= { calculateCriticalEnergy: false };
              damage.criticalEnergyCalc.calculateCriticalEnergy = on;
              calculateCriticalEnergy(damage);
            }}
            label="Calculate Critical Value from K1C"
          />
          {#if damage.criticalEnergyCalc?.calculateCriticalEnergy}
            <div class="space-y-1">
              <Label for={`dm-k1c-${index}`}>Fracture toughness (K1C)</Label>
              <Input
                id={`dm-k1c-${index}`}
                type="number"
                bind:value={damage.criticalEnergyCalc.k1c}
                oninput={() => calculateCriticalEnergy(damage)}
              />
            </div>
          {/if}
        </div>
      {/if}

      <SchemaParams
        entry={sections.damage}
        values={damage.params!}
        names={[String(damage.params?.['Damage Model'] ?? '')]}
        custom={CUSTOM_KEYS.damage}
        idPrefix={`dm-${index}`}
      />

      <div class="border-border space-y-2 border-t pt-2">
        <h5 class="text-muted-foreground text-sm font-medium">Interblock Damage</h5>
        {#each damage.interBlocks ?? [] as ib, subindex (ib.interBlockid ?? subindex)}
          <div class="flex flex-wrap items-end gap-3">
            <div class="space-y-1">
              <Label for={`ib-first-${index}-${subindex}`}>First block ID</Label>
              <Select id={`ib-first-${index}-${subindex}`} bind:value={ib.firstBlockId}>
                {#each blocks as block (block.blocksId)}<option value={block.blocksId}
                    >{block.blocksId}</option
                  >{/each}
              </Select>
            </div>
            <div class="space-y-1">
              <Label for={`ib-second-${index}-${subindex}`}>Second block ID</Label>
              <Select id={`ib-second-${index}-${subindex}`} bind:value={ib.secondBlockId}>
                {#each blocks as block (block.blocksId)}<option value={block.blocksId}
                    >{block.blocksId}</option
                  >{/each}
              </Select>
            </div>
            <div class="space-y-1">
              <Label for={`ib-value-${index}-${subindex}`}>Critical Value</Label>
              <Input id={`ib-value-${index}-${subindex}`} type="number" bind:value={ib.value} />
            </div>
            <Button
              variant="ghost"
              size="icon"
              onclick={() => damage.interBlocks!.splice(subindex, 1)}
              title="Remove interblock damage"
            >
              <Trash2 class="h-4 w-4" />
            </Button>
          </div>
        {/each}
        <AddButton
          noun="interblock damage"
          items={damage.interBlocks}
          onclick={() => addInterBlock(damage)}
        />
      </div>
    </div>
  {/each}

  <AddButton noun="damage model" items={damages} onclick={addDamage} />
</div>
