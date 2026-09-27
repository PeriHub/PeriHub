<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

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

  const damages = $derived(modelStore.modelData.damages ?? []);
  const blocks = $derived(modelStore.modelData.blocks ?? []);
  const materials = $derived(modelStore.modelData.materials ?? []);
  const twoDimensional = $derived(modelStore.modelData.model.twoDimensional);

  const damageModelNames = ['Critical Stretch', 'Critical Energy'];

  function addDamage() {
    if (!modelStore.modelData.damages) modelStore.modelData.damages = [];
    const list = modelStore.modelData.damages;
    const len = list.length;
    const newItem =
      len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as Damage) : ({} as Damage);
    newItem.damagesId = len + 1;
    newItem.name = `Damage${len + 1}`;
    newItem.criticalEnergyCalc = {};
    list.push(newItem);
  }

  function removeDamage(index: number) {
    damages.splice(index, 1);
    damages.forEach((d, i) => (d.damagesId = i + 1));
    if (damages.length === 0) {
      blocks.forEach((b) => (b.damageModel = ''));
    }
  }

  function addInterBlock(index: number) {
    const damage = damages[index]!;
    if (!damage.interBlocks) damage.interBlocks = [];
    const list = damage.interBlocks;
    const len = list.length;
    const newItem =
      len > 0
        ? (structuredClone($state.snapshot(list[len - 1])) as InterBlock)
        : ({} as InterBlock);
    newItem.interBlockid = len + 1;
    newItem.firstBlockId = 1;
    newItem.secondBlockId = len + 1;
    list.push(newItem);
  }

  function removeInterBlock(index: number, subindex: number) {
    damages[index]!.interBlocks!.splice(subindex, 1);
  }

  function calculateCriticalEnergy(damageId: number) {
    const damage = damages[damageId]!;
    if (!damage.criticalEnergyCalc?.calculateCriticalEnergy) return;
    const k1c = damage.criticalEnergyCalc.k1c;
    if (k1c == null) return;

    let E = 0;
    let pr = 0;
    let materialName = '';
    for (const block of blocks) {
      if (block.damageModel === damage.name) materialName = block.material!;
    }
    let planeStress = true;
    for (const material of materials) {
      if (material?.name === materialName) {
        planeStress = material.planeStress;
        E = material.youngsModulus!;
        pr = material.poissonsRatio!;
      }
    }
    damage.criticalEnergy = planeStress ? k1c ** 2 / +E : k1c ** 2 / (+E / (1 - pr ** 2));
  }
</script>

<div class="space-y-3 p-3">
  {#each damages as damage, index (index)}
    <div class="border-border space-y-3 rounded-md border p-3">
      <h4 class="font-medium">Damage Model {damage.damagesId}</h4>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`dm-name-${index}`}>Name</Label>
          <Input id={`dm-name-${index}`} bind:value={damage.name} />
        </div>
        <Button
          variant="ghost"
          size="icon"
          onclick={() => removeDamage(index)}
          title="Remove Damage Model"
        >
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      <div class="space-y-1">
        <Label for={`dm-model-${index}`}>Damage model</Label>
        <Select id={`dm-model-${index}`} bind:value={damage.damageModel}>
          {#each damageModelNames as name (name)}
            <option value={name}>{name}</option>
          {/each}
        </Select>
      </div>

      {#if damage.damageModel === 'Critical Stretch'}
        <div class="space-y-1">
          <Label for={`dm-cs-${index}`}>Critical stretch</Label>
          <Input id={`dm-cs-${index}`} type="number" bind:value={damage.criticalStretch} />
        </div>
      {:else if damage.damageModel === 'Critical Energy'}
        <div class="space-y-1">
          <Label for={`dm-ce-${index}`}>Critical energy</Label>
          <Input
            id={`dm-ce-${index}`}
            type="number"
            bind:value={damage.criticalEnergy}
            readonly={damage.criticalEnergyCalc?.calculateCriticalEnergy}
          />
        </div>

        <Toggle
          checked={damage.criticalEnergyCalc?.calculateCriticalEnergy ?? false}
          onCheckedChange={(v: boolean) => {
            if (!damage.criticalEnergyCalc) damage.criticalEnergyCalc = {};
            damage.criticalEnergyCalc.calculateCriticalEnergy = v;
          }}
          label="Calculate Critical Energy"
        />
        {#if damage.criticalEnergyCalc?.calculateCriticalEnergy}
          <div class="space-y-1">
            <Label for={`dm-k1c-${index}`}>Fracture toughness (K1C)</Label>
            <Input
              id={`dm-k1c-${index}`}
              type="number"
              bind:value={damage.criticalEnergyCalc.k1c}
              oninput={() => calculateCriticalEnergy(index)}
            />
          </div>
        {/if}
      {:else if damage.damageModel === 'Von Mises Stress'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`dm-vms-${index}`}>Critical von Mises stress</Label>
            <Input
              id={`dm-vms-${index}`}
              type="number"
              bind:value={damage.criticalVonMisesStress}
            />
          </div>
          <div class="space-y-1">
            <Label for={`dm-cd-${index}`}>Critical damage</Label>
            <Input id={`dm-cd-${index}`} type="number" bind:value={damage.criticalDamage} />
          </div>
        </div>
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`dm-td-${index}`}>Threshold damage</Label>
            <Input id={`dm-td-${index}`} type="number" bind:value={damage.thresholdDamage} />
          </div>
          <div class="space-y-1">
            <Label for={`dm-cdn-${index}`}>Critical damage to neglect material point</Label>
            <Input
              id={`dm-cdn-${index}`}
              type="number"
              bind:value={damage.criticalDamageToNeglect}
            />
          </div>
        </div>
      {/if}

      <Toggle bind:checked={damage.interBlockDamage} label="Inter block damage" />
      {#if damage.interBlockDamage}
        {#each damage.interBlocks ?? [] as prop, subindex (prop.interBlockid ?? subindex)}
          <div class="flex flex-wrap items-end gap-3">
            <div class="space-y-1">
              <Label for={`ib-first-${index}-${subindex}`}>First block ID</Label>
              <Select id={`ib-first-${index}-${subindex}`} bind:value={prop.firstBlockId}>
                {#each blocks as block, blockIdx (blockIdx)}
                  <option value={block.blocksId}>{block.blocksId}</option>
                {/each}
              </Select>
            </div>
            <div class="space-y-1">
              <Label for={`ib-second-${index}-${subindex}`}>Second block ID</Label>
              <Select id={`ib-second-${index}-${subindex}`} bind:value={prop.secondBlockId}>
                {#each blocks as block, blockIdx (blockIdx)}
                  <option value={block.blocksId}>{block.blocksId}</option>
                {/each}
              </Select>
            </div>
            <div class="space-y-1">
              <Label for={`ib-value-${index}-${subindex}`}>Critical value</Label>
              <Input id={`ib-value-${index}-${subindex}`} type="number" bind:value={prop.value} />
            </div>
            <Button
              variant="ghost"
              size="icon"
              onclick={() => removeInterBlock(index, subindex)}
              title="Remove InterBlock"
            >
              <Trash2 class="h-4 w-4" />
            </Button>
          </div>
        {/each}
        <AddButton
          noun="inter-block damage"
          items={damage.interBlocks}
          onclick={() => addInterBlock(index)}
        />
      {/if}

      <Toggle bind:checked={damage.anistropicDamage} label="Anisotropic damage" />
      {#if damage.anistropicDamage}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`ad-x-${index}`}>Anisotropic damage X</Label>
            <Input id={`ad-x-${index}`} type="number" bind:value={damage.anistropicDamageX} />
          </div>
          <div class="space-y-1">
            <Label for={`ad-y-${index}`}>Anisotropic damage Y</Label>
            <Input id={`ad-y-${index}`} type="number" bind:value={damage.anistropicDamageY} />
          </div>
          {#if !twoDimensional}
            <div class="space-y-1">
              <Label for={`ad-z-${index}`}>Anisotropic damage Z</Label>
              <Input id={`ad-z-${index}`} type="number" bind:value={damage.anistropicDamageZ} />
            </div>
          {/if}
        </div>
      {/if}

      <Toggle bind:checked={damage.onlyTension} label="Only tension" />

      <div class="space-y-1">
        <Label for={`dm-thick-${index}`}>Thickness</Label>
        <Input id={`dm-thick-${index}`} type="number" bind:value={damage.thickness} />
      </div>
    </div>
  {/each}

  <AddButton noun="damage model" items={damages} onclick={addDamage} />
</div>
