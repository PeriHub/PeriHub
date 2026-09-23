<!--
SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>

SPDX-License-Identifier: Apache-2.0
-->

<script lang="ts">
  import { Plus, Trash2 } from 'lucide-svelte';
  import { modelStore } from '$lib/stores/model-store.svelte';
  import type { Damage, InterBlock } from '$lib/client';
  import Toggle from '$lib/components/ui/Toggle.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import Label from '$lib/components/ui/Label.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const damages = $derived(modelStore.modelData.damages ?? []);
  const blocks = $derived(modelStore.modelData.blocks ?? []);
  const materials = $derived(modelStore.modelData.materials ?? []);
  const twoDimensional = $derived(modelStore.modelData.model.twoDimensional);

  const damageModelNames = ['Critical Stretch', 'Critical Energy'];

  function addDamage() {
    if (!modelStore.modelData.damages) modelStore.modelData.damages = [];
    const list = modelStore.modelData.damages;
    const len = list.length;
    const newItem = len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as Damage) : ({} as Damage);
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
      len > 0 ? (structuredClone($state.snapshot(list[len - 1])) as InterBlock) : ({} as InterBlock);
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
  {#each damages as damage, index (damage.damagesId ?? index)}
    <div class="space-y-3 rounded-md border border-border p-3">
      <h4 class="font-medium">Damage Model {damage.damagesId}</h4>

      <div class="flex flex-wrap items-end gap-3">
        <div class="space-y-1">
          <Label for={`dm-name-${index}`}>name</Label>
          <Input id={`dm-name-${index}`} bind:value={damage.name} />
        </div>
        <Button variant="ghost" size="icon" onclick={() => removeDamage(index)} title="Remove Damage Model">
          <Trash2 class="h-4 w-4" />
        </Button>
      </div>

      <div class="space-y-1">
        <Label for={`dm-model-${index}`}>Damage Model</Label>
        <Select id={`dm-model-${index}`} bind:value={damage.damageModel}>
          {#each damageModelNames as name (name)}
            <option value={name}>{name}</option>
          {/each}
        </Select>
      </div>

      {#if damage.damageModel !== 'Von Mises Stress'}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`dm-cs-${index}`}>Critical Stretch</Label>
            <Input id={`dm-cs-${index}`} type="number" bind:value={damage.criticalStretch} />
          </div>
          <div class="space-y-1">
            <Label for={`dm-ce-${index}`}>Critical Energy</Label>
            <Input
              id={`dm-ce-${index}`}
              type="number"
              bind:value={damage.criticalEnergy}
              readonly={damage.criticalEnergyCalc?.calculateCriticalEnergy}
            />
          </div>
        </div>
      {:else}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`dm-vms-${index}`}>Critical Von Mises Stress</Label>
            <Input id={`dm-vms-${index}`} type="number" bind:value={damage.criticalVonMisesStress} />
          </div>
          <div class="space-y-1">
            <Label for={`dm-cd-${index}`}>Critical Damage</Label>
            <Input id={`dm-cd-${index}`} type="number" bind:value={damage.criticalDamage} />
          </div>
        </div>
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`dm-td-${index}`}>Threshold Damage</Label>
            <Input id={`dm-td-${index}`} type="number" bind:value={damage.thresholdDamage} />
          </div>
          <div class="space-y-1">
            <Label for={`dm-cdn-${index}`}>Critical Damage To Neglect Material Point</Label>
            <Input id={`dm-cdn-${index}`} type="number" bind:value={damage.criticalDamageToNeglect} />
          </div>
        </div>
      {/if}

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
          <Label for={`dm-k1c-${index}`}>Fracture Toughness (K1C)</Label>
          <Input
            id={`dm-k1c-${index}`}
            type="number"
            bind:value={damage.criticalEnergyCalc.k1c}
            oninput={() => calculateCriticalEnergy(index)}
          />
        </div>
      {/if}

      <Toggle bind:checked={damage.interBlockDamage} label="Inter Block Damage" />
      {#if damage.interBlockDamage}
        {#each damage.interBlocks ?? [] as prop, subindex (prop.interBlockid ?? subindex)}
          <div class="flex flex-wrap items-end gap-3">
            <div class="space-y-1">
              <Label for={`ib-first-${index}-${subindex}`}>First Block Id</Label>
              <Select id={`ib-first-${index}-${subindex}`} bind:value={prop.firstBlockId}>
                {#each blocks as block, blockIdx (block.blocksId ?? blockIdx)}
                  <option value={block.blocksId}>{block.blocksId}</option>
                {/each}
              </Select>
            </div>
            <div class="space-y-1">
              <Label for={`ib-second-${index}-${subindex}`}>Second Block Id</Label>
              <Select id={`ib-second-${index}-${subindex}`} bind:value={prop.secondBlockId}>
                {#each blocks as block, blockIdx (block.blocksId ?? blockIdx)}
                  <option value={block.blocksId}>{block.blocksId}</option>
                {/each}
              </Select>
            </div>
            <div class="space-y-1">
              <Label for={`ib-value-${index}-${subindex}`}>Critical Energy</Label>
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
        <Button variant="outline" size="sm" onclick={() => addInterBlock(index)}>
          <Plus class="h-4 w-4" /> Add InterBlock
        </Button>
      {/if}

      <Toggle bind:checked={damage.anistropicDamage} label="Anistropic Damage" />
      {#if damage.anistropicDamage}
        <div class="flex flex-wrap items-end gap-3">
          <div class="space-y-1">
            <Label for={`ad-x-${index}`}>Anistropic Damage X</Label>
            <Input id={`ad-x-${index}`} type="number" bind:value={damage.anistropicDamageX} />
          </div>
          <div class="space-y-1">
            <Label for={`ad-y-${index}`}>Anistropic Damage Y</Label>
            <Input id={`ad-y-${index}`} type="number" bind:value={damage.anistropicDamageY} />
          </div>
          {#if !twoDimensional}
            <div class="space-y-1">
              <Label for={`ad-z-${index}`}>Anistropic Damage Z</Label>
              <Input id={`ad-z-${index}`} type="number" bind:value={damage.anistropicDamageZ} />
            </div>
          {/if}
        </div>
      {/if}

      <Toggle bind:checked={damage.onlyTension} label="Only Tension" />

      <div class="space-y-1">
        <Label for={`dm-thick-${index}`}>Thickness</Label>
        <Input id={`dm-thick-${index}`} type="number" bind:value={damage.thickness} />
      </div>
    </div>
  {/each}

  <Button variant="outline" size="sm" onclick={addDamage}>
    <Plus class="h-4 w-4" /> Add Damage Model
  </Button>
</div>
